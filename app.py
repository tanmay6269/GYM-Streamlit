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
if cookies.ready():
    # keep the last cookie reader that has loaded, so other files (and logout) can write cookies
    st.session_state['_cookies'] = cookies
    st.session_state['_cookies_seen'] = True
elif not st.session_state.get('_cookies_seen'):
    # First run of this visit: the browser's cookies arrive on the next run. Register every
    # page address now (hidden), so a refresh on e.g. /payments stays on Payments.
    from navigation import all_url_paths

    def _loading():
        pass

    st.navigation(
        [st.Page(_loading, title="Loading", url_path="", default=True)]
        + [st.Page(_loading, title="Loading", url_path=p) for p in all_url_paths()],
        position="hidden",
    )
    st.stop()
# Otherwise the cookie component is re-syncing (it does this after a page change and does
# not always report back). This visit already knows who is logged in, so carry on.

# ---------------- LOGOUT ----------------
def _clear_login():
    """Forget the signed-in user and queue the cookie changes that log them out.

    Everything the previous user did (quiz, searches, forms) is removed, but the
    cookie manager's own state is kept: its queue holds the "logged out" cookie
    values until the browser has saved them, and deleting it would log the user
    straight back in.
    """
    jar = st.session_state.get("_cookies", cookies)
    for key in list(st.session_state.keys()):
        if key not in ("_cookies", "_cookies_seen") and not key.startswith("CookieManager"):
            del st.session_state[key]
    st.session_state.logged_in = False
    st.session_state._logged_out = True
    for name in ("logged_in", "Role", "id", "User_name", "member_id", "login_time"):
        jar[name] = "False" if name == "logged_in" else ""


def _logout():
    _clear_login()
    cookies.save()
    st.rerun()


# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

#-----------Restore Login From Cookie-----------
# "_logged_out" blocks re-login from a cookie the browser hasn't cleared yet
if cookies.ready() and cookies.get("logged_in") == "True" and not st.session_state.get("_logged_out"):
    st.session_state.logged_in = True

    # Restore login time so the 12 hour limit survives a page refresh
    if "login_time" not in st.session_state:
        try:
            st.session_state.login_time = datetime.fromisoformat(cookies.get("login_time"))
        except (TypeError, ValueError):
            st.session_state.login_time = datetime.min  # unknown: treat as expired

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
                # database unreachable: keep the cookie and let the user retry,
                # instead of logging them out for good
                st.error("⚠️ Could not reach the database to restore your login. Please refresh the page in a moment.")
                st.stop()

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
        _clear_login()
        st.session_state._expired = True
        cookies.save()
        st.rerun()

# ---------------- HOME PAGE ----------------
if st.session_state.logged_in:
    if "user" not in st.session_state:
        _logout()

    from navigation import build_pages
    role = st.session_state.user.get("Role")
    ordered_pages, pages = build_pages(role)
    if not ordered_pages:  # unknown role: never fall back to a dashboard
        _logout()

    # every menu option is its own page with its own URL, so the browser's
    # back / forward arrows move between options instead of leaving the site
    current = st.navigation(ordered_pages)

    with st.sidebar:
        st.button("🚪 Logout", width="stretch", on_click=_clear_login)

    from GYM import apply_theme
    from footer import render_footer
    st.session_state['_pages'] = pages
    apply_theme()
    current.run()
    render_footer(role, pages, show_latest=(current.url_path != "feedback"))
else:
    # Logged out: only the login box. The navigation is replaced by hidden pages, so
    # the old menu disappears; old addresses (e.g. a bookmarked /my-attendance, or the
    # browser's back arrow after logout) also show the login box instead of a
    # "page not found" message, and are then switched back to the main address.
    def _login_screen():
        if st.session_state.pop("_expired", False):
            st.warning("⏰ Session expired. Please login again.")
        from login import login
        login()

    from navigation import all_url_paths

    # login screen only: no sidebar, no menu toggle, no top bar
    st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"], [data-testid="stHeader"], [data-testid="stToolbar"]{display:none !important;}
    </style>
    """, unsafe_allow_html=True)
    login_page = st.Page(_login_screen, title="Login", default=True)
    old_addresses = [st.Page(_login_screen, title="Login", url_path=p) for p in all_url_paths()]
    current = st.navigation([login_page, *old_addresses], position="hidden")
    if current.url_path:  # an old address: move to the main address
        st.switch_page(login_page)
    current.run()
