# Insert Record.....
from dbconn import get_db, hash_password
from validators import valid_id, valid_date, valid_mobile
import streamlit as st
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
            if valid_id(mid) is None:
                st.error("Member ID must be a number")
                return
            if valid_date(dob) is None:
                st.error("Date Of Birth must be a valid date in YYYY-MM-DD format")
                return
            if valid_mobile(mob) is None:
                st.error("Mobile Number must be 7 to 15 digits")
                return
            if not mn.strip():
                st.error("Member Name is required")
                return
            dob = valid_date(dob)
            db = None
            try:
                db = get_db()
                smt = db.cursor()
                q = """
                    INSERT INTO members (memberid, membername, dob, gender, address, membershipstart, membershipend, membershipplan, mobilenumber, Password)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
                smt.execute(q, (mid, mn, dob, mg, mc, msd, med, plan, mob, hash_password(mid)))
                load()
                db.commit()
                st.success("Member Submitted Successfully...")
            except Exception as e:
                st.error(e)
            finally:
                if db:
                    db.close()
