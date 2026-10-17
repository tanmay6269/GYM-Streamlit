# Edit Record

from dbconn import get_db
from validators import valid_id
import streamlit as st
from login import load
from dateutil.relativedelta import relativedelta
from datetime import datetime

def edit_member():

    st.title("[Edit Member Details]")
    id = st.text_input("Enter Member ID U Want To Edit:")
    if st.button("Search"):
        if valid_id(id) is None:
            st.error("Member ID must be a number")
            return
        try:
            db = get_db()
            smt = db.cursor()
            smt.execute("select * from members where memberid=%s", (id,))
            record = smt.fetchone()
            load()

            if record:
                st.session_state.edit_record = record
                st.session_state.edit_id = id
                st.success("Member Found")
            else:
                st.error("Member Not Found...")
                if 'edit_record' in st.session_state:
                    del st.session_state.edit_record
            db.close()
        except Exception as e:
            st.error(e)

    if 'edit_record' in st.session_state:
        record = st.session_state.edit_record

        mn = st.text_input(
            "Member Name",
            value=f"{record['membername']}"
        )
        add = st.text_input(
            "Address",
            value=record['address'] or ""
        )

        try:
            current_start = datetime.strptime(str(record['membershipstart']), '%Y-%m-%d')
        except Exception:
            current_start = datetime.now()

        msd = st.date_input(
            "Membership Start Date",
            value=current_start
        )

        # Use membershipplan column name
        current_plan = record.get('membershipplan', '1 Month')
        plan_options = ['1 Month', '3 Months', '6 Months', '12 Months']
        plan_index = plan_options.index(current_plan) if current_plan in plan_options else 0

        plan = st.selectbox(
            "Membership Plan",
            plan_options,
            index=plan_index
        )

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

        mob = st.text_input(
            "Mobile Number",
            value=record['mobilenumber'] or ""
        )

        total_days = (med - msd).days
        months = total_days // 30

        st.info(f"📅 Plan: **{plan}** | Duration: **{months} months ({total_days} days)** | Start: **{msd}** → End: **{med}**")

        if st.button("Edit"):
            try:
                db = get_db()
                smt = db.cursor()

                q = """
                    UPDATE members
                    SET membername=%s,
                        address=%s,
                        membershipstart=%s,
                        membershipend=%s,
                        membershipplan=%s,
                        mobilenumber=%s
                    WHERE memberid=%s
                """
                params = (mn, add, msd, med, plan, mob, st.session_state.edit_id)
                smt.execute(q, params)
                db.commit()
                db.close()

                # Update the session record with new values
                st.session_state.edit_record['membername'] = mn
                st.session_state.edit_record['address'] = add
                st.session_state.edit_record['membershipstart'] = str(msd)
                st.session_state.edit_record['membershipend'] = str(med)
                st.session_state.edit_record['membershipplan'] = plan
                st.session_state.edit_record['mobilenumber'] = mob

                load()
                st.success("✅ Member Updated Successfully!")

            except Exception as e:
                st.error(f"Error updating member: {e}")