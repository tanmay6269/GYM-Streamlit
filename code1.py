# Insert Record.....
import streamlit as st
import pymysql as sql
from dateutil.relativedelta import relativedelta
from login import load

# ---------------------------------------------------------------

def insert_member():
    # Get user role from session state instead of cookies
    user_cookie = st.session_state.user.get("Role", "Member") if "user" in st.session_state else "Member"
    
# -----------------------------------------------------------Admin--------------------------------------------------------
    if user_cookie == 'Admin':
        mid = st.text_input("Enter Member ID:")
        mn = st.text_input("Enter Member Name:")
        mg = st.radio("Gender:", ['Male', 'Female', 'Other'])
        dob = st.text_input("Date Of Birth:")
        mc = st.text_input("Enter Address:")
        msd = st.date_input("Membership Start Date:")
        plan = st.selectbox(
            "Membership Plan",
            ['1 Month','3 Months','6 Months','12 Months']
        )
        # Auto-calculate End Date-------

        if plan == "1 Month":
            med = msd + relativedelta(months=1)

        elif plan == "3 Months":
            med = msd + relativedelta(months=3)

        elif plan == "6 Months":
            med = msd + relativedelta(months=6)

        else:
            med = msd + relativedelta(months=12)

        st.date_input(
            "Membership End Date",
            value=med,
            disabled=True
        )
        mob = st.text_input("Enter Mobile Number:")

        if st.button("Submit"):
            try:
                db = sql.connect(host='localhost',port=3306,user='root',password='1234',database='TA_Fitness',cursorclass=sql.cursors.DictCursor)
                smt = db.cursor()
                q = f"""
                    INSERT INTO members (memberid, membername, dob, gender, address, membershipstart, membershipend, membershipplan, mobilenumber) 
                    VALUES ({mid},'{mn}','{dob}','{mg}','{mc}','{msd}','{med}','{plan}','{mob}')
                """
                smt.execute(q)
                load()
                db.commit()
                st.success("Member Submitted Successfully...")
            except Exception as e:
                st.error(e)
            finally:
                db.close()

# -----------------------------------------------------------Member--------------------------------------------------------

    elif user_cookie == 'Member':
        # Member dashboard is handled in member_functions.py
        pass

# -----------------------------------------------------------Team--------------------------------------------------------

    else:
        # Team dashboard is handled in team_functions.py
        pass