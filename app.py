from datetime import datetime, timedelta
import streamlit as st
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
    password="my_secret_password"
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
    
    if "user" not in st.session_state:
        role = cookies.get("Role")
        user_id = cookies.get("id")
        user_name = cookies.get("User_name")
        member_id = cookies.get("member_id")
        
        if role and user_id and user_name:
            st.session_state.user = {
                "UserID": int(user_id) if user_id else None,
                "Name": user_name,
                "Role": role
            }
            if member_id and member_id != "0" and member_id != "":
                st.session_state.user["member_id"] = int(member_id)

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
        if st.button("🚪 Logout", use_container_width=True):
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