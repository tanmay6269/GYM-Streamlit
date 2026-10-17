import base64
import html
from pathlib import Path

import pymysql as sql
import streamlit as st

from dbconn import get_db
from navigation import footer_layout

BASE_DIR = Path(__file__).parent

ROLE_COLORS = {"Admin": "#dc2626", "Team": "#ea580c", "Member": "#2563eb"}


def _logo_b64():
    return base64.b64encode((BASE_DIR / "gym.png").read_bytes()).decode()


# ---------------------------------------------------------------- database
def _ensure_table(smt):
    smt.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(20),
            message TEXT NOT NULL,
            rating TINYINT,
            user_role VARCHAR(20),
            user_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try:  # older installs created the table without a rating column
        smt.execute("ALTER TABLE feedback ADD COLUMN rating TINYINT")
    except sql.err.OperationalError:
        pass  # column already exists


def _save_feedback(name, phone, rating, message):
    user = st.session_state.get("user", {})
    db = get_db()
    try:
        smt = db.cursor()
        _ensure_table(smt)
        smt.execute(
            "INSERT INTO feedback (name, phone, rating, message, user_role, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, phone or None, rating, message, user.get("Role"), user.get("UserID")),
        )
        db.commit()
    finally:
        db.close()


def _load_feedback(limit=200):
    """Return (rows newest first, stats dict)."""
    db = get_db()
    try:
        smt = db.cursor()
        _ensure_table(smt)
        smt.execute(
            "SELECT id, created_at, name, phone, rating, message, user_role "
            "FROM feedback ORDER BY id DESC LIMIT %s", (limit,))
        rows = smt.fetchall()
        smt.execute("SELECT rating, COUNT(*) AS n FROM feedback WHERE rating IS NOT NULL GROUP BY rating")
        dist = {r["rating"]: r["n"] for r in smt.fetchall()}
    finally:
        db.close()
    total_rated = sum(dist.values())
    avg = sum(k * v for k, v in dist.items()) / total_rated if total_rated else 0
    return rows, {"avg": avg, "rated": total_rated, "dist": dist}


# ---------------------------------------------------------------- styling
def _css():
    st.markdown("""
<style>
.ta-footer{margin-top:40px;color:#334155;}
.ta-footer-brand .name{display:flex;align-items:center;gap:12px;font-size:28px;font-weight:800;color:#111;}
.ta-footer-brand .name img{width:44px;height:44px;border-radius:10px;border:1px solid #fed7aa;background:#fff;padding:3px;}
.ta-footer-brand .name span{color:#ff4500;}
.ta-footer-brand p{margin:14px 0;font-size:15px;line-height:1.6;}
.ta-badge{display:inline-flex;align-items:center;gap:8px;border:1px solid #e2e8f0;border-radius:999px;padding:6px 14px;font-size:12px;font-weight:700;background:#fff;}
.ta-badge i{width:8px;height:8px;border-radius:50%;background:#ff4500;display:inline-block;}
.ta-footer-col h5{margin:0 0 8px 0;font-size:13px;letter-spacing:1.5px;font-weight:800;color:#111;}
.ta-note{border:1px solid #e2e8f0;border-radius:14px;padding:14px 18px;font-size:12px;color:#64748b;background:rgba(255,255,255,.7);margin-top:18px;}
.ta-bottom{display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between;border-top:1px solid #e2e8f0;margin-top:22px;padding-top:16px;font-size:12px;color:#64748b;}
.ta-eyebrow{color:#ff4500;font-size:12px;font-weight:800;letter-spacing:1.5px;}
.fb-hero{display:flex;flex-wrap:wrap;gap:28px;align-items:center;background:linear-gradient(135deg,#1f1f1f,#7a1c0a 60%,#ff4500);border-radius:20px;padding:26px 30px;color:#fff;margin-bottom:20px;}
.fb-hero .big{font-size:64px;font-weight:800;line-height:1;}
.fb-hero .sub{opacity:.85;font-size:14px;margin-top:4px;}
.fb-stars{color:#fbbf24;letter-spacing:2px;}
.fb-bars{flex:1;min-width:240px;}
.fb-bar{display:flex;align-items:center;gap:10px;font-size:13px;margin:5px 0;}
.fb-bar .track{flex:1;height:8px;background:rgba(255,255,255,.25);border-radius:99px;overflow:hidden;}
.fb-bar .fill{height:100%;background:#fbbf24;border-radius:99px;}
.fb-card{display:flex;gap:14px;background:#fff;border:1px solid #e5e7eb;border-left:5px solid #ff4500;border-radius:16px;padding:16px 18px;margin-bottom:12px;box-shadow:0 2px 10px rgba(0,0,0,.05);color:#1f2937;}
.fb-avatar{flex:0 0 46px;height:46px;border-radius:50%;background:linear-gradient(135deg,#ff512f,#f09819);color:#fff;font-weight:800;font-size:20px;display:flex;align-items:center;justify-content:center;}
.fb-body{flex:1;min-width:0;}
.fb-head{display:flex;flex-wrap:wrap;gap:8px;align-items:center;}
.fb-name{font-weight:700;font-size:16px;color:#111;}
.fb-role{font-size:11px;font-weight:700;color:#fff;border-radius:99px;padding:2px 10px;}
.fb-card .fb-stars{font-size:18px;}
.fb-msg{margin:6px 0 4px 0;font-size:15px;line-height:1.55;color:#374151;overflow-wrap:anywhere;}
.fb-meta{font-size:12px;color:#6b7280;}
.fb-empty{border:1px dashed #cbd5e1;border-radius:16px;padding:26px;text-align:center;color:#64748b;background:rgba(255,255,255,.7);}
</style>
""", unsafe_allow_html=True)


def _stars(n):
    n = int(n or 0)
    return "★" * n + "☆" * (5 - n)


def _card_html(r, show_private=False):
    name = html.escape(r["name"] or "")
    role = r["user_role"] or "Member"
    color = ROLE_COLORS.get(role, "#6b7280")
    msg = html.escape(r["message"] or "").replace("\n", "<br>")
    when = r["created_at"].strftime("%d %b %Y, %I:%M %p") if r["created_at"] else ""
    meta = when
    if show_private and r["phone"]:
        meta += f" &nbsp;•&nbsp; 📞 {html.escape(r['phone'])}"
    comment = f'<div class="fb-msg">{msg}</div>' if msg else ""
    return (
        '<div class="fb-card">'
        f'<div class="fb-avatar">{html.escape((r["name"] or "?")[:1].upper())}</div>'
        '<div class="fb-body">'
        f'<div class="fb-head"><span class="fb-name">{name}</span>'
        f'<span class="fb-role" style="background:{color}">{html.escape(role)}</span>'
        f'<span class="fb-stars">{_stars(r["rating"])}</span></div>'
        f'{comment}<div class="fb-meta">{meta}</div>'
        '</div></div>'
    )


def _hero_html(stats):
    total = stats["rated"]
    bars = ""
    for star in (5, 4, 3, 2, 1):
        n = stats["dist"].get(star, 0)
        pct = round(n / total * 100) if total else 0
        bars += (f'<div class="fb-bar"><span>{star} ★</span><div class="track">'
                 f'<div class="fill" style="width:{pct}%"></div></div><span>{n}</span></div>')
    return (
        '<div class="fb-hero">'
        f'<div><div class="big">{stats["avg"]:.1f}</div>'
        f'<div class="fb-stars" style="font-size:22px">{_stars(round(stats["avg"]))}</div>'
        f'<div class="sub">{total} rating{"s" if total != 1 else ""}</div></div>'
        f'<div class="fb-bars">{bars}</div></div>'
    )


# ---------------------------------------------------------------- form
def feedback_form(key="footer"):
    with st.form(f"feedback_form_{key}", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Name *", value=st.session_state.get("user", {}).get("Name", ""), placeholder="Your name", key=f"fb_name_{key}")
        phone = c2.text_input("Phone", placeholder="Optional (only the admin can see it)", key=f"fb_phone_{key}")
        st.write("Rating *")
        stars = st.feedback("stars", key=f"fb_stars_{key}")
        message = st.text_area("Comment", placeholder="Tell us what you think", max_chars=1000, height=110, key=f"fb_msg_{key}")
        sent = st.form_submit_button("Send feedback", type="primary")
    if sent:
        if not name.strip():
            st.error("Name is required.")
        elif stars is None:
            st.error("Please choose a star rating.")
        elif phone.strip() and not (phone.strip().isdigit() and 7 <= len(phone.strip()) <= 15):
            st.error("Phone must be 7 to 15 digits.")
        else:
            try:
                _save_feedback(name.strip(), phone.strip(), stars + 1, message.strip())
                st.success("Thank you! Your feedback has been posted.")
            except Exception as e:
                st.error(f"Could not save feedback: {e}")


# ---------------------------------------------------------------- pages
def feedback_page():
    """Full Feedback page: rating summary, form and every message (all roles see it)."""
    _css()
    st.title("[Feedback & Reviews]")
    st.markdown("---")
    is_admin = st.session_state.get("user", {}).get("Role") == "Admin"
    rows, stats = _load_feedback()

    if stats["rated"]:
        st.markdown(_hero_html(stats), unsafe_allow_html=True)

    left, right = st.columns([1, 1.4], gap="large")
    with left:
        with st.container(border=True):
            st.markdown('<div class="ta-eyebrow">SHARE YOUR EXPERIENCE</div>', unsafe_allow_html=True)
            st.subheader("Rate TA Fitness")
            feedback_form(key="page")
    with right:
        st.subheader("💬 What everyone is saying")
        f1, f2 = st.columns(2)
        pick = f1.selectbox("Show", ["All ratings", "5 stars", "4 stars", "3 stars", "2 stars", "1 star"], key="fb_filter")
        who = f2.selectbox("From", ["Everyone", "Members", "Team", "Admin"], key="fb_who")
        shown = rows
        if pick != "All ratings":
            shown = [r for r in shown if r["rating"] == int(pick[0])]
        if who != "Everyone":
            role = "Member" if who == "Members" else who
            shown = [r for r in shown if r["user_role"] == role]
        if not shown:
            st.markdown('<div class="fb-empty">No feedback here yet.<br>Be the first to share your thoughts!</div>', unsafe_allow_html=True)
        for r in shown:
            st.markdown(_card_html(r, show_private=is_admin), unsafe_allow_html=True)


def render_footer(role, pages, show_latest=True):
    _css()
    layout = footer_layout(role)

    # ---- latest feedback, shown at the bottom of every page for every role
    if show_latest:
        try:
            rows, stats = _load_feedback(limit=3)
        except Exception:
            rows, stats = [], {"avg": 0, "rated": 0, "dist": {}}
        st.markdown("---")
        h1, h2 = st.columns([3, 1])
        with h1:
            summary = (f" &nbsp; <span class='fb-stars'>{_stars(round(stats['avg']))}</span> "
                       f"{stats['avg']:.1f} / 5 ({stats['rated']})") if stats["rated"] else ""
            st.markdown(f"### 💬 Latest feedback{summary}", unsafe_allow_html=True)
        with h2:
            if "feedback" in pages:
                st.page_link(pages["feedback"], label="See all feedback →")
        if rows:
            is_admin = st.session_state.get("user", {}).get("Role") == "Admin"
            for r in rows:
                st.markdown(_card_html(r, show_private=is_admin), unsafe_allow_html=True)
        else:
            st.markdown('<div class="fb-empty">No feedback yet. Be the first to rate TA Fitness!</div>', unsafe_allow_html=True)

    # ---- link columns (every item opens its page)
    brand, plans, gym, account = st.columns([1.6, 1, 1, 1])
    with brand:
        st.markdown(f"""
<div class="ta-footer"><div class="ta-footer-brand">
<div class="name"><img src="data:image/png;base64,{_logo_b64()}" alt="TA Fitness"> TA <span>Fitness</span></div>
<p>Manage memberships, attendance, renewals and payments for your gym in one place.</p>
<div class="ta-badge"><i></i> Demo gym platform</div>
</div></div>
""", unsafe_allow_html=True)
    plan_page = pages.get(layout["plan_page"])
    columns = [
        (plans, "MEMBERSHIP", [(p, plan_page) for p in ("1 Month - ₹1000", "3 Months - ₹2400", "6 Months - ₹4200", "12 Months - ₹7000")]),
        (gym, "GYM", [(pages[k].title, pages[k]) for k in layout["GYM"] if k in pages]),
        (account, "ACCOUNT", [(pages[k].title, pages[k]) for k in layout["ACCOUNT"] if k in pages]),
    ]
    for col, heading, links in columns:
        with col:
            st.markdown(f'<div class="ta-footer-col"><h5>{heading}</h5></div>', unsafe_allow_html=True)
            for label, page in links:
                if page is not None:
                    st.page_link(page, label=label)

    # ---- quick feedback form on every page except the Feedback page itself
    if show_latest:
        with st.container(border=True):
            left, right = st.columns([1, 2.4])
            with left:
                st.markdown('<div class="ta-eyebrow">HELP US IMPROVE</div>', unsafe_allow_html=True)
                st.subheader("Send your feedback")
                st.caption("Your rating and comment are posted in the app for everyone to see.")
            with right:
                feedback_form()

    st.markdown("""
<div class="ta-note">TA Fitness is a prototype gym management system. All members, payments and attendance shown are demo data.</div>
<div class="ta-bottom">
<span>© 2026 TA Fitness. All rights reserved.</span>
<span>Created by Tanmay Agrawal</span>
<span>Train • Track • Transform</span>
</div>
""", unsafe_allow_html=True)
