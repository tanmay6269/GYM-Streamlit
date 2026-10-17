from dbconn import get_db, check_password, lockout_remaining, record_failure, clear_failures
from validators import valid_id
import streamlit as st
import time as t
from datetime import datetime


def load():
    status = st.empty()
    bar = st.progress(0)
    for i in range(100):
        status.text(f"Progress {i+1}%")
        bar.progress(i+1)
        t.sleep(0.0005)
    status.text("Completed")

@st.dialog("              TA Fitness User Login                 ", dismissible=False)
def login():

    # Get cookies from session state (set by app.py)
    cookies = st.session_state.get('_cookies')
    if cookies is None:
        st.error("Session error. Please refresh.")
        return

    id = st.text_input("Enter User Id:")
    name = st.text_input("Enter User Name:")
    pwd = st.text_input("Enter Password:", type='password')
    Role = st.selectbox("Login As", ["Admin", "Team", "Member"])

    if st.button("🚀 Login", width='stretch'):
        if id == "" or name == "" or pwd == "":
            st.warning("Please Fill All Fields")
            return
        if valid_id(id) is None:
            st.error("❌ Invalid ID, Name or Password")
            return
        id = str(valid_id(id))  # " 12 " -> "12", so the cookie restores after a refresh
        name = name.strip()

        try:
            db = get_db()
            smt = db.cursor()

            login_key = f"{Role}:{id}"
            wait = lockout_remaining(smt, login_key)
            if wait:
                db.close()
                st.error(f"🔒 Too many failed attempts. Try again in about {wait} minute(s).")
                return

            if Role == "Member":
                smt.execute("SELECT * FROM members WHERE memberid=%s AND membername=%s", (id, name))
            else:
                smt.execute("SELECT * FROM user_login WHERE User_id=%s AND User_Name=%s AND Role=%s", (id, name, Role))

            record = smt.fetchone()
            if record and not check_password(pwd, record['Password']):
                record = None
            if record:
                clear_failures(smt, login_key)
            else:
                record_failure(smt, login_key)
            db.commit()
            db.close()
            load()

            if record:
                if Role == "Member":
                    st.session_state.user = {
                        "UserID": record['memberid'],
                        "Name": record['membername'],
                        "Role": "Member"
                    }
                else:
                    st.session_state.user = {
                        "UserID": record['User_id'],
                        "Name": record['User_Name'],
                        "Role": Role
                    }

                st.session_state.logged_in = True
                st.session_state.pop("_logged_out", None)
                st.session_state.login_time = datetime.now()

                # Save to cookies
                cookies["logged_in"] = "True"
                cookies["login_time"] = st.session_state.login_time.isoformat()
                cookies["id"] = str(id)
                cookies["Role"] = Role
                cookies["User_name"] = st.session_state.user["Name"]

                if Role == "Member":
                    cookies["member_id"] = str(record['memberid'])
                else:
                    cookies["member_id"] = "0"

                cookies.save()

                st.success("Login Successful....")

                if Role == "Member":
                    st.success(f"Welcome {record['membername']} 🏋️")
                else:
                    st.success(f"Welcome {record['User_Name']} 🏋️")

                t.sleep(1)
                st.rerun()
            else:
                st.error("❌ Invalid ID, Name or Password")

        except Exception as e:
            st.error(f"Database Error : {e}")