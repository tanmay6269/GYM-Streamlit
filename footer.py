import base64
from pathlib import Path

import streamlit as st

from dbconn import get_db

BASE_DIR = Path(__file__).parent


def _logo_b64():
    return base64.b64encode((BASE_DIR / "gym.png").read_bytes()).decode()


def _save_feedback(name, phone, message):
    user = st.session_state.get("user", {})
    db = get_db()
    try:
        smt = db.cursor()
        smt.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                message TEXT NOT NULL,
                user_role VARCHAR(20),
                user_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        smt.execute(
            "INSERT INTO feedback (name, phone, message, user_role, user_id) VALUES (%s, %s, %s, %s, %s)",
            (name, phone or None, message, user.get("Role"), user.get("UserID")),
        )
        db.commit()
    finally:
        db.close()


def feedback_form(key="footer"):
    with st.form(f"feedback_form_{key}", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Name *", value=st.session_state.get("user", {}).get("Name", ""), placeholder="Your name", key=f"fb_name_{key}")
        phone = c2.text_input("Phone", placeholder="Your phone number", key=f"fb_phone_{key}")
        message = st.text_area("Message *", placeholder="Tell us what you think", max_chars=1000, height=110, key=f"fb_msg_{key}")
        sent = st.form_submit_button("Send feedback")
    if sent:
        if not name.strip() or not message.strip():
            st.error("Name and message are required.")
        elif phone.strip() and not (phone.strip().isdigit() and 7 <= len(phone.strip()) <= 15):
            st.error("Phone must be 7 to 15 digits.")
        else:
            try:
                _save_feedback(name.strip(), phone.strip(), message.strip())
                st.success("Thank you! Your feedback has been sent.")
            except Exception as e:
                st.error(f"Could not save feedback: {e}")


def feedback_page():
    st.title("[Send Feedback]")
    st.markdown("---")
    feedback_form(key="page")


def render_footer():
    st.markdown("""
<style>
.ta-footer{margin-top:40px;color:#334155;}
.ta-footer-grid{display:flex;flex-wrap:wrap;gap:30px;justify-content:space-between;}
.ta-footer-brand{flex:1.6;min-width:260px;}
.ta-footer-brand .name{display:flex;align-items:center;gap:12px;font-size:28px;font-weight:800;color:#111;}
.ta-footer-brand .name img{width:44px;height:44px;border-radius:10px;border:1px solid #fed7aa;background:#fff;padding:3px;}
.ta-footer-brand .name span{color:#ff4500;}
.ta-footer-brand p{margin:14px 0;font-size:15px;line-height:1.6;}
.ta-badge{display:inline-flex;align-items:center;gap:8px;border:1px solid #e2e8f0;border-radius:999px;padding:6px 14px;font-size:12px;font-weight:700;background:#fff;}
.ta-badge i{width:8px;height:8px;border-radius:50%;background:#ff4500;display:inline-block;}
.ta-footer-col{flex:1;min-width:150px;}
.ta-footer-col h5{margin:0 0 12px 0;font-size:13px;letter-spacing:1.5px;font-weight:800;color:#111;}
.ta-footer-col div{font-size:14px;margin-bottom:10px;}
.ta-note{border:1px solid #e2e8f0;border-radius:14px;padding:14px 18px;font-size:12px;color:#64748b;background:rgba(255,255,255,.7);margin-top:18px;}
.ta-bottom{display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between;border-top:1px solid #e2e8f0;margin-top:22px;padding-top:16px;font-size:12px;color:#64748b;}
.ta-eyebrow{color:#ff4500;font-size:12px;font-weight:800;letter-spacing:1.5px;}
</style>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div class="ta-footer">
<div class="ta-footer-grid">
<div class="ta-footer-brand">
<div class="name"><img src="data:image/png;base64,{_logo_b64()}" alt="TA Fitness"> TA <span>Fitness</span></div>
<p>Manage memberships, attendance, renewals and payments for your gym in one place.</p>
<div class="ta-badge"><i></i> Demo gym platform</div>
</div>
<div class="ta-footer-col"><h5>MEMBERSHIP</h5>
<div>1 Month - ₹1000</div><div>3 Months - ₹2400</div><div>6 Months - ₹4200</div><div>12 Months - ₹7000</div></div>
<div class="ta-footer-col"><h5>GYM</h5>
<div>Attendance</div><div>Renewals</div><div>Payments</div><div>Reports</div></div>
<div class="ta-footer-col"><h5>ACCOUNT</h5>
<div>My profile</div><div>My membership</div><div>Payment history</div><div>Fitness quiz</div></div>
</div>
</div>
""", unsafe_allow_html=True)

    with st.container(border=True):
        left, right = st.columns([1, 2.4])
        with left:
            st.markdown('<div class="ta-eyebrow">HELP US IMPROVE</div>', unsafe_allow_html=True)
            st.subheader("Send your feedback")
            st.caption("Your message is saved for the TA Fitness team to read.")
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


def view_feedback():
    """Admin: list every feedback message that has been sent."""
    st.title("[Feedback Received]")
    st.markdown("---")
    db = get_db()
    try:
        smt = db.cursor()
        smt.execute("SELECT id, created_at, name, phone, user_role, message FROM feedback ORDER BY id DESC")
        rows = smt.fetchall()
    except Exception:
        rows = []
    finally:
        db.close()
    if rows:
        st.metric("Total feedback", len(rows))
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.info("No feedback yet.")
