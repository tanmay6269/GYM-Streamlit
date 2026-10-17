from datetime import datetime, timedelta
import streamlit as st

# streamlit-cookies-manager still calls st.cache, which new Streamlit versions removed
if not hasattr(st, "cache"):
    st.cache = st.cache_data

from streamlit_cookies_manager import EncryptedCookieManager

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TA Fitness Gym",
    page_icon="💪",
    layout="wide"
)

# ---------------- COOKIES ----------------
cookies = EncryptedCookieManager(
    prefix="ta_fitness_",
    password=st.secrets.get("cookie_password", "my_secret_password")
)
if not cookies.ready():
    st.stop()

# ✅ Store cookies in session state so other files can access
st.session_state['_cookies'] = cookies

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

#-----------Restore Login From Cookie-----------
if cookies.get("logged_in") == "True":
    st.session_state.logged_in = True

    # Restore login time so the 12 hour limit survives a page refresh
    if "login_time" not in st.session_state:
        try:
            st.session_state.login_time = datetime.fromisoformat(cookies.get("login_time"))
        except (TypeError, ValueError):
            st.session_state.login_time = datetime.now()

    if "user" not in st.session_state:
        role = cookies.get("Role")
        user_id = cookies.get("id")
        user_name = cookies.get("User_name")
        member_id = cookies.get("member_id")

        verified = False
        if role and user_id and user_name and user_id.isdigit():
            from dbconn import get_db
            try:
                _db = get_db()
                _smt = _db.cursor()
                if role == "Member":
                    _smt.execute("SELECT memberid FROM members WHERE memberid=%s AND membername=%s", (user_id, user_name))
                else:
                    _smt.execute("SELECT User_id FROM user_login WHERE User_id=%s AND User_Name=%s AND Role=%s", (user_id, user_name, role))
                verified = _smt.fetchone() is not None
                _db.close()
            except Exception:
                verified = False

        if verified:
            st.session_state.user = {
                "UserID": int(user_id),
                "Name": user_name,
                "Role": role
            }
            if member_id and member_id != "0" and member_id != "":
                st.session_state.user["member_id"] = int(member_id)
        else:
            # cookie doesn't match a real account: treat as logged out
            st.session_state.logged_in = False
            cookies["logged_in"] = "False"
            cookies.save()

# Auto Logout After 12 Hour
if "login_time" in st.session_state:
    if datetime.now() - st.session_state.login_time > timedelta(hours=12):
        st.session_state.logged_in = False
        if "login_time" in st.session_state:
            del st.session_state.login_time
        if "user" in st.session_state:
            del st.session_state.user
        cookies["logged_in"] = "False"
        cookies["Role"] = ""
        cookies["id"] = ""
        cookies["User_name"] = ""
        cookies["member_id"] = ""
        cookies.save()
        st.warning("⏰ Session Expired. Please Login Again.")
        st.rerun()

# ---------------- HOME PAGE ----------------
if st.session_state.logged_in:
    from GYM import Home
    Home()

    with st.sidebar:
        st.markdown("<br>" * 5, unsafe_allow_html=True)
        if st.button("🚪 Logout", width='stretch'):
            st.session_state.logged_in = False
            if "login_time" in st.session_state:
                del st.session_state.login_time
            if "user" in st.session_state:
                del st.session_state.user
            cookies["logged_in"] = "False"
            cookies["Role"] = ""
            cookies["id"] = ""
            cookies["User_name"] = ""
            cookies["member_id"] = ""
            cookies.save()
            st.rerun()
else:
    from login import login
    login()