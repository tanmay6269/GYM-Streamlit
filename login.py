import streamlit as st
import pymysql as sql    
import time as t
from datetime import datetime

# ❌ REMOVE THIS - cookies will be imported from app
# cookies = EncryptedCookieManager(...)
# if not cookies.ready():
#     st.stop()

def load():
    status = st.empty()
    bar = st.progress(0)
    for i in range(100):
        status.text(f"Progress {i+1}%")
        bar.progress(i+1)
        t.sleep(0.0005)
    status.text("Completed")

@st.dialog("              TA Fitness User Login                 ")
def login():
    # ✅ Import cookies here from app
    from streamlit_cookies_manager import EncryptedCookieManager
    import streamlit as st
    
    # Get cookies from session state (set by app.py)
    cookies = st.session_state.get('_cookies')
    if not cookies:
        st.error("Session error. Please refresh.")
        return
    
    id = st.text_input("Enter User Id:")
    name = st.text_input("Enter User Name:")
    pwd = st.text_input("Enter Password:", type='password')
    Role = st.selectbox("Login As", ["Admin", "Team", "Member"])
    
    if st.button("🚀 Login", use_container_width=True):
        if id == "" or name == "" or pwd == "":
            st.warning("Please Fill All Fields")
            return
        
        try:
            db = sql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='1234',
                database='TA_fitness',
                cursorclass=sql.cursors.DictCursor
            )
            smt = db.cursor()
            
            if Role == "Member":
                smt.execute(f"SELECT * FROM members WHERE memberid={id} AND membername='{name}' AND Password={pwd}")
            else:
                smt.execute(f"SELECT * FROM user_login WHERE User_id={id} AND User_Name='{name}' AND Password={pwd} AND Role='{Role}'")
            
            record = smt.fetchone()
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
                st.session_state.login_time = datetime.now()
                
                # Save to cookies
                cookies["logged_in"] = "True"
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
                db.close()
                
        except Exception as e:
            st.error(f"Database Error : {e}")