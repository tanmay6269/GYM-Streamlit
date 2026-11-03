"""Online join requests.

A visitor fills in the Join Now form (member details, plan, payment and a password of their
own). The request is saved as Pending. An Admin checks the payment on the Join Requests page and
approves it, which creates the member with the next member ID, records the payment and sets the
dates from the plan. No card or bank details are ever stored: only the payment mode and a short
reference (for example a UPI transaction ID).
"""
import html
import re
import time
from datetime import date, datetime

import streamlit as st
from dateutil.relativedelta import relativedelta

import advisor
from dbconn import get_db, hash_password
from validators import valid_mobile

PLAN_MONTHS = {"1 Month": 1, "3 Months": 3, "6 Months": 6, "12 Months": 12}
PRICES = {name: price for name, _, price in advisor.PLANS}
PAYMENT_MODES = ["UPI", "Cash at the gym", "Card", "Bank transfer"]
MAX_PENDING_PER_MOBILE = 3
MIN_AGE = 14

_schema_ready = False


# ---------------------------------------------------------------- database
def ensure_schema(smt):
    """Create the join_requests table if it is missing (checked once per app process)."""
    global _schema_ready
    if _schema_ready:
        return
    smt.execute("""
        CREATE TABLE IF NOT EXISTS join_requests (
            request_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            dob DATE NOT NULL,
            gender ENUM('Male','Female','Other') NOT NULL,
            address VARCHAR(200) DEFAULT NULL,
            mobile VARCHAR(15) NOT NULL,
            plan ENUM('1 Month','3 Months','6 Months','12 Months') NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            payment_mode VARCHAR(30) NOT NULL,
            payment_ref VARCHAR(40) DEFAULT NULL,
            password_hash VARCHAR(100) NOT NULL,
            status ENUM('Pending','Approved','Rejected') NOT NULL DEFAULT 'Pending',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            reviewed_by VARCHAR(100) DEFAULT NULL,
            reviewed_at DATETIME DEFAULT NULL,
            review_note VARCHAR(200) DEFAULT NULL,
            member_id INT DEFAULT NULL,
            KEY idx_mobile (mobile),
            KEY idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    _schema_ready = True


def create_member(smt, name, dob, gender, address, start, end, plan, mobile, password_hash=None):
    """Insert a member with the next member ID and return that ID.

    The next ID is the highest ID plus one, read with a row lock inside the caller's transaction, so
    two people approved at the same moment cannot get the same number (the database would refuse a
    duplicate anyway). MySQL cannot make memberid AUTO_INCREMENT here because other tables point at it.
    With a password_hash it is stored as given; without one the first password is the member ID
    (the default the Insert Member page always used).
    """
    smt.execute("SELECT COALESCE(MAX(memberid), 0) + 1 AS n FROM members FOR UPDATE")
    member_id = smt.fetchone()["n"]
    smt.execute("INSERT INTO members (memberid, membername, dob, gender, address, membershipstart, membershipend, "
                "membershipplan, mobilenumber, Password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (member_id, name, dob, gender, address, start, end, plan, mobile, password_hash))
    if password_hash is None:
        smt.execute("UPDATE members SET Password=%s WHERE memberid=%s", (hash_password(member_id), member_id))
    return member_id


# ---------------------------------------------------------------- checks
def looks_like_card_number(text):
    digits = re.sub(r"[\s-]", "", str(text))
    return digits.isdigit() and 13 <= len(digits) <= 19


def validate_application(a):
    """Return a list of problems with a join application (empty list = fine)."""
    errors = []
    name = (a.get("name") or "").strip()
    if not (2 <= len(name) <= 100) or not re.fullmatch(r"[A-Za-z][A-Za-z .'\-]*", name):
        errors.append("Enter your full name using letters only.")
    dob = a.get("dob")
    if not isinstance(dob, date) or dob >= date.today():
        errors.append("Enter a valid date of birth.")
    elif relativedelta(date.today(), dob).years < MIN_AGE:
        errors.append(f"You must be at least {MIN_AGE} years old to join.")
    if a.get("gender") not in ("Male", "Female", "Other"):
        errors.append("Choose your gender.")
    if len((a.get("address") or "").strip()) > 200:
        errors.append("Address is too long (200 characters at most).")
    if valid_mobile(a.get("mobile")) is None:
        errors.append("Mobile number must be 7 to 15 digits.")
    if a.get("plan") not in PLAN_MONTHS:
        errors.append("Choose a membership plan.")
    mode, ref = a.get("payment_mode"), (a.get("payment_ref") or "").strip()
    if mode not in PAYMENT_MODES:
        errors.append("Choose how you paid.")
    elif ref and looks_like_card_number(ref):
        errors.append("That looks like a card number. Never enter card details here, only a transaction reference.")
    elif mode in ("UPI", "Bank transfer") and not re.fullmatch(r"[A-Za-z0-9]{6,30}", ref):
        errors.append("Enter the transaction reference (6 to 30 letters or digits) of your payment.")
    elif mode == "Card" and ref and not re.fullmatch(r"[A-Za-z0-9]{4,30}", ref):
        errors.append("The payment reference can only have letters and digits.")
    pw = a.get("password") or ""
    if len(pw) < 6:
        errors.append("Choose a password of at least 6 characters.")
    elif pw != a.get("password2"):
        errors.append("The two passwords do not match.")
    return errors


# ---------------------------------------------------------------- actions
def submit_request(a):
    """Save a validated application as Pending. Returns the request number."""
    amount = PRICES[a["plan"]]  # always from the plan, never from the form
    db = get_db()
    try:
        smt = db.cursor()
        ensure_schema(smt)
        smt.execute("SELECT COUNT(*) AS n FROM join_requests WHERE mobile=%s AND status='Pending'", (a["mobile"].strip(),))
        if smt.fetchone()["n"] >= MAX_PENDING_PER_MOBILE:
            raise ValueError("This mobile number already has several requests waiting. Please wait for the gym team to review them.")
        smt.execute(
            "INSERT INTO join_requests (name, dob, gender, address, mobile, plan, amount, payment_mode, payment_ref, password_hash) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (a["name"].strip(), a["dob"], a["gender"], (a.get("address") or "").strip(), a["mobile"].strip(), a["plan"],
             amount, a["payment_mode"], (a.get("payment_ref") or "").strip() or None, hash_password(a["password"])))
        rid = smt.lastrowid
        db.commit()
        return rid
    finally:
        db.close()


def lookup_status(request_id, mobile):
    """Status of a request, only when the request number and mobile number both match."""
    if not str(request_id).strip().isdigit() or valid_mobile(mobile) is None:
        return None
    db = get_db()
    try:
        smt = db.cursor()
        ensure_schema(smt)
        smt.execute("SELECT request_id, name, plan, status, review_note, member_id FROM join_requests "
                    "WHERE request_id=%s AND mobile=%s", (int(request_id), mobile.strip()))
        return smt.fetchone()
    finally:
        db.close()


def list_requests(status=None):
    db = get_db()
    try:
        smt = db.cursor()
        ensure_schema(smt)
        if status:
            smt.execute("SELECT * FROM join_requests WHERE status=%s ORDER BY request_id DESC", (status,))
        else:
            smt.execute("SELECT * FROM join_requests ORDER BY request_id DESC")
        rows = smt.fetchall()
        # flags for the reviewer: possible duplicates (never merged automatically), two queries for all rows
        mobiles = sorted({r["mobile"] for r in rows})
        members, pending = {}, {}
        if mobiles:
            marks = ",".join(["%s"] * len(mobiles))
            smt.execute(f"SELECT memberid, membername, mobilenumber FROM members WHERE mobilenumber IN ({marks})", mobiles)
            for m in smt.fetchall():
                members.setdefault(m["mobilenumber"], []).append(m)
            smt.execute(f"SELECT mobile, COUNT(*) AS n FROM join_requests WHERE status='Pending' AND mobile IN ({marks}) "
                        "GROUP BY mobile", mobiles)
            pending = {p["mobile"]: p["n"] for p in smt.fetchall()}
        for r in rows:
            r["same_mobile_members"] = members.get(r["mobile"], [])
            r["other_pending"] = pending.get(r["mobile"], 0) - (1 if r["status"] == "Pending" else 0)
        return rows
    finally:
        db.close()


def status_counts():
    """Number of requests in each status, in one query."""
    db = get_db()
    try:
        smt = db.cursor()
        ensure_schema(smt)
        smt.execute("SELECT status, COUNT(*) AS n FROM join_requests GROUP BY status")
        found = {r["status"]: r["n"] for r in smt.fetchall()}
        return {s: found.get(s, 0) for s in ("Pending", "Approved", "Rejected")}
    finally:
        db.close()


def approve_request(request_id, admin_name):
    """Create the member and the payment from a pending request. Returns the new member ID."""
    db = get_db()
    try:
        smt = db.cursor()
        ensure_schema(smt)
        smt.execute("SELECT * FROM join_requests WHERE request_id=%s FOR UPDATE", (request_id,))
        r = smt.fetchone()
        if not r or r["status"] != "Pending":
            raise ValueError("This request is no longer pending.")
        start = date.today()
        end = start + relativedelta(months=PLAN_MONTHS[r["plan"]])
        member_id = create_member(smt, r["name"], r["dob"], r["gender"], r["address"], start, end, r["plan"],
                                  r["mobile"], password_hash=r["password_hash"])
        smt.execute("INSERT INTO payments (member_id, amount, payment_date, payment_mode, recorded_by) VALUES (%s,%s,%s,%s,%s)",
                    (member_id, r["amount"], start, f"{r['payment_mode']} (online request {request_id})"[:50], admin_name))
        smt.execute("UPDATE join_requests SET status='Approved', reviewed_by=%s, reviewed_at=%s, member_id=%s WHERE request_id=%s",
                    (admin_name, datetime.now(), member_id, request_id))
        db.commit()
        return member_id
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def reject_request(request_id, admin_name, note):
    db = get_db()
    try:
        smt = db.cursor()
        ensure_schema(smt)
        n = smt.execute("UPDATE join_requests SET status='Rejected', reviewed_by=%s, reviewed_at=%s, review_note=%s "
                        "WHERE request_id=%s AND status='Pending'", (admin_name, datetime.now(), (note or "").strip()[:200] or None, request_id))
        db.commit()
        if not n:
            raise ValueError("This request is no longer pending.")
    finally:
        db.close()


# ---------------------------------------------------------------- public page
def _css():
    st.markdown("""
<style>
.st-key-hp{position:absolute !important;left:-9999px;height:0;overflow:hidden;}
.join-sec{background:#fff;border-radius:18px;padding:14px 18px 4px 18px;box-shadow:0 3px 12px rgba(0,0,0,.07);margin:12px 0;}
.join-sec h4{margin:0 0 4px 0;color:#111;display:flex;align-items:center;gap:8px;font-size:18px;}
.join-amt{background:linear-gradient(135deg,#ff512f,#f09819);color:#fff;border-radius:16px;padding:14px 18px;text-align:center;}
.join-amt b{display:block;font-size:34px;line-height:1.1;} .join-amt span{font-size:13px;opacity:.95;}
.req-no{background:#ecfdf5;border:1px solid #6ee7b7;border-radius:18px;padding:20px;text-align:center;color:#065f46;margin:12px 0;}
.req-no b{display:block;font-size:44px;color:#047857;line-height:1.1;}
.stat-pill{display:inline-block;border-radius:999px;padding:3px 14px;font-weight:700;font-size:13px;color:#fff;}
</style>""", unsafe_allow_html=True)


def join_page():
    import landing
    landing._top("join")
    _css()
    ic = landing.ic
    st.markdown(f'<div class="pub pub-page-title">{ic("how_to_reg", 44)} Join TA Fitness</div>', unsafe_allow_html=True)
    apply_view = st.segmented_control("Join", ["Apply to join", "Check my request"], default="Apply to join",
                                      key="join_view", label_visibility="collapsed") or "Apply to join"
    if apply_view == "Apply to join":
        _apply_form(ic)
    else:
        _status_form(ic)
    landing.public_footer("join")


def _apply_form(ic):
    st.markdown(f'<div class="pub pub-note">{ic("info", 20, "#c2410c")}<span>Fill in the form and choose your plan. The gym team checks your '
                'payment and approves your membership. You will get a request number to follow its status.</span></div>', unsafe_allow_html=True)
    if "_join_done" in st.session_state:
        done = st.session_state["_join_done"]
        st.markdown(f"<div class='pub req-no'>{ic('task_alt', 40, '#059669')}<div>Your request number</div><b>#{done}</b>"
                    "<div>Your request is Pending. Keep this number and use <b>Check my request</b> with your mobile number to follow it.</div></div>",
                    unsafe_allow_html=True)
        if st.button("Submit another request", icon=":material/add:"):
            del st.session_state["_join_done"]
            st.rerun()
        return

    st.markdown(f"<div class='pub join-sec'><h4>{ic('person', 22, '#ff4500')} Your details</h4></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    name = c1.text_input("Full name *", max_chars=100, key="j_name")
    gender = c2.radio("Gender *", ["Male", "Female", "Other"], horizontal=True, key="j_gender")
    c3, c4 = st.columns(2)
    dob = c3.date_input("Date of birth *", value=date(2000, 1, 1), min_value=date(1940, 1, 1), max_value=date.today(), key="j_dob")
    mobile = c4.text_input("Mobile number *", max_chars=15, key="j_mobile")
    address = st.text_input("Address", max_chars=200, key="j_address")

    st.markdown(f"<div class='pub join-sec'><h4>{ic('fitness_center', 22, '#ff4500')} Membership plan</h4></div>", unsafe_allow_html=True)
    plans = list(PLAN_MONTHS)
    preset = st.session_state.pop("join_plan", None)
    if preset in plans:
        st.session_state["j_plan"] = preset
    plan = st.selectbox("Plan *", plans, key="j_plan")
    months = PLAN_MONTHS[plan]
    saving = advisor.MONTHLY_PRICE * months - PRICES[plan]

    st.markdown(f"<div class='pub join-sec'><h4>{ic('payments', 22, '#ff4500')} Payment</h4></div>", unsafe_allow_html=True)
    pc1, pc2 = st.columns([1, 1.6], vertical_alignment="center")
    pc1.markdown(f"<div class='pub join-amt'><span>Amount for {plan}</span><b>₹{PRICES[plan]:,}</b>"
                 f"<span>{'Save ₹' + format(saving, ',') if saving else 'Monthly plan'} • ₹{round(PRICES[plan] / months)} per month</span></div>",
                 unsafe_allow_html=True)
    with pc2:
        mode = st.radio("How did you pay? *", PAYMENT_MODES, horizontal=True, key="j_mode")
        if mode == "Cash at the gym":
            ref = ""
            st.info("Pay the amount in cash at the gym front desk. The team approves your request after receiving it.", icon=":material/payments:")
        else:
            ref = st.text_input("Transaction reference *" if mode != "Card" else "Payment reference (optional)", max_chars=40, key="j_ref",
                                placeholder="e.g. the UPI transaction ID")
            st.caption("Enter only the transaction reference. Never type card numbers, PINs or bank account details here.")

    st.markdown(f"<div class='pub join-sec'><h4>{ic('lock', 22, '#ff4500')} Your password</h4></div>", unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    pw = p1.text_input("Choose a password *", type="password", key="j_pw", help="At least 6 characters. You will log in with your member ID, name and this password.")
    pw2 = p2.text_input("Confirm password *", type="password", key="j_pw2")
    with st.container(key="hp"):
        trap = st.text_input("Website", key="j_site", label_visibility="collapsed")

    if st.button("Submit my request", type="primary", icon=":material/send:", width="stretch"):
        if trap:  # a bot filled the hidden field: pretend it worked
            st.session_state["_join_done"] = "0"
            st.rerun()
        if time.time() - st.session_state.get("_join_last", 0) < 20:
            st.error("Please wait a few seconds before submitting again.")
            return
        data = {"name": name, "dob": dob, "gender": gender, "address": address, "mobile": mobile, "plan": plan,
                "payment_mode": mode, "payment_ref": ref, "password": pw, "password2": pw2}
        problems = validate_application(data)
        if problems:
            for p in problems:
                st.error(p, icon=":material/error:")
            return
        try:
            rid = submit_request(data)
        except ValueError as e:
            st.error(str(e))
            return
        except Exception as e:
            st.error(f"Could not save your request right now. Please try again later. ({e.__class__.__name__})")
            return
        st.session_state["_join_last"] = time.time()
        st.session_state["_join_done"] = rid
        for k in ("j_name", "j_mobile", "j_address", "j_ref", "j_pw", "j_pw2"):
            st.session_state.pop(k, None)
        st.rerun()


def _status_form(ic):
    st.markdown(f"<div class='pub join-sec'><h4>{ic('search', 22, '#ff4500')} Check my request</h4></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    rid = c1.text_input("Request number", key="s_rid")
    mobile = c2.text_input("Mobile number used in the request", key="s_mobile")
    if st.button("Check status", icon=":material/search:", width="stretch"):
        try:
            row = lookup_status(rid, mobile)
        except Exception as e:
            st.error(f"Could not check right now. Please try again later. ({e.__class__.__name__})")
            return
        if not row:
            st.error("No request found with that number and mobile number.", icon=":material/error:")
        elif row["status"] == "Pending":
            st.warning(f"Request #{row['request_id']} for the {row['plan']} plan is **Pending**. The gym team is checking your payment.",
                       icon=":material/hourglass_top:")
        elif row["status"] == "Approved":
            st.success(f"Request #{row['request_id']} is **Approved**. Welcome to TA Fitness!\n\n"
                       f"Your member ID is **{row['member_id']}**. Log in as **Member** with ID **{row['member_id']}**, the name "
                       f"**{row['name']}** and the password you chose.", icon=":material/check_circle:")
        else:
            note = f" Reason: {row['review_note']}" if row["review_note"] else ""
            st.error(f"Request #{row['request_id']} was **Rejected**.{note} Please contact the gym.", icon=":material/cancel:")


# ---------------------------------------------------------------- admin page
def requests_page():
    """Admin page: review online join requests."""
    user = st.session_state.get("user", {})
    if user.get("Role") != "Admin":
        st.error("Only the Admin can review join requests.")
        return
    admin_name = user.get("Name", "Admin")
    st.title("[Join Requests]")
    st.markdown("---")
    view = st.segmented_control("Show", ["Pending", "Approved", "Rejected", "All"], default="Pending", key="jr_view") or "Pending"
    try:
        rows = list_requests(None if view == "All" else view)
        counts = status_counts()
    except Exception as e:
        st.error(f"Database Error : {e}")
        return
    m1, m2, m3 = st.columns(3)
    m1.metric("Pending", counts["Pending"])
    m2.metric("Approved", counts["Approved"])
    m3.metric("Rejected", counts["Rejected"])
    if not rows:
        st.info(f"No {view.lower()} requests." if view != "All" else "No requests yet.", icon=":material/inbox:")
        return
    colors = {"Pending": "#f59e0b", "Approved": "#16a34a", "Rejected": "#dc2626"}
    for r in rows:
        title = f"#{r['request_id']}  {r['name']}  |  {r['plan']}  |  ₹{int(r['amount']):,}  |  {r['status']}"
        with st.expander(title, expanded=(r["status"] == "Pending" and view == "Pending")):
            st.markdown(f"<span class='stat-pill' style='background:{colors[r['status']]}'>{r['status']}</span>", unsafe_allow_html=True)
            d1, d2 = st.columns(2)
            d1.write(f"**Name:** {html.escape(r['name'])}")
            d1.write(f"**Date of birth:** {r['dob']}   |   **Gender:** {r['gender']}")
            d1.write(f"**Mobile:** {html.escape(r['mobile'])}")
            d1.write(f"**Address:** {html.escape(r['address'] or '-')}")
            d2.write(f"**Plan:** {r['plan']}   |   **Amount:** ₹{int(r['amount']):,}")
            d2.write(f"**Payment mode:** {r['payment_mode']}")
            d2.write(f"**Reference:** {html.escape(r['payment_ref'] or '-')}")
            d2.write(f"**Applied on:** {r['created_at']:%d %b %Y, %I:%M %p}")
            if r["same_mobile_members"]:
                who = ", ".join(f"#{m['memberid']} {m['membername']}" for m in r["same_mobile_members"])
                st.warning(f"Possible duplicate: this mobile number already belongs to member {who}. Check before approving.",
                           icon=":material/warning:")
            if r["other_pending"]:
                st.warning(f"{r['other_pending']} other pending request(s) use the same mobile number.", icon=":material/warning:")
            if r["status"] == "Pending":
                ok = st.checkbox(f"I have confirmed that ₹{int(r['amount']):,} was received ({r['payment_mode']})", key=f"ok_{r['request_id']}")
                a1, a2 = st.columns(2)
                note = a2.text_input("Reason if rejecting", key=f"note_{r['request_id']}", max_chars=200)
                if a1.button("Approve and add member", key=f"appr_{r['request_id']}", icon=":material/check:", width="stretch", disabled=not ok):
                    try:
                        mid = approve_request(r["request_id"], admin_name)
                        st.success(f"Approved. New member ID is {mid}.", icon=":material/check_circle:")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                if a2.button("Reject", key=f"rej_{r['request_id']}", icon=":material/close:", width="stretch"):
                    try:
                        reject_request(r["request_id"], admin_name, note)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            else:
                st.caption(f"Reviewed by {r['reviewed_by'] or '-'} on {r['reviewed_at']:%d %b %Y}" if r["reviewed_at"] else "")
                if r["member_id"]:
                    st.write(f"**Member ID:** {r['member_id']}")
                if r["review_note"]:
                    st.write(f"**Reason:** {html.escape(r['review_note'])}")
