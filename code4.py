# Edit Record 

import streamlit as st
import pymysql as sql
from login import load
from dateutil.relativedelta import relativedelta
from datetime import datetime

def edit_member():

    st.title("[Edit Member Details]")
    id = st.text_input("Enter Member ID U Want To Edit:")
    if st.button("Search"):
        try:
            db = sql.connect(host='localhost',port=3306,user='root',password='1234',database='TA_Fitness',cursorclass=sql.cursors.DictCursor)
            smt = db.cursor()
            smt.execute(f"select * from members where memberid={id}")
            record = smt.fetchone()
            load()

            if record:
                st.session_state.record = record
                st.session_state.edit_id = id
                st.success("Member Found")
            else:
                st.error("Member Not Found...")
                if 'record' in st.session_state:
                    del st.session_state.record
            db.close()
        except Exception as e:
            st.error(e)
    
    if 'record' in st.session_state:
        record = st.session_state.record
        
        mn = st.text_input(
            "Member Name",
            value=f"{record['membername']}"
        )
        add = st.text_input(
            "Address",
            value=f"{record['address']}"
        )
        
        try:
            current_start = datetime.strptime(str(record['membershipstart']), '%Y-%m-%d')
        except:
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
            value=f"{record['mobilenumber']}"
        )
        
        total_days = (med - msd).days
        months = total_days // 30
        
        st.info(f"📅 Plan: **{plan}** | Duration: **{months} months ({total_days} days)** | Start: **{msd}** → End: **{med}**")
        
        if st.button("Edit"):
            try:
                db = sql.connect(host='localhost',port=3306,user='root',password='1234',database='TA_Fitness',cursorclass=sql.cursors.DictCursor)
                smt = db.cursor()
                
                q = f"""
                    UPDATE members 
                    SET membername='{mn}',
                        address='{add}',
                        membershipstart='{msd}',
                        membershipend='{med}',
                        membershipplan='{plan}',
                        mobilenumber='{mob}'
                    WHERE memberid={st.session_state.edit_id}
                """
                
                smt.execute(q)
                db.commit()
                db.close()
                
                # Update the session record with new values
                st.session_state.record['membername'] = mn
                st.session_state.record['address'] = add
                st.session_state.record['membershipstart'] = str(msd)
                st.session_state.record['membershipend'] = str(med)
                st.session_state.record['membershipplan'] = plan
                st.session_state.record['mobilenumber'] = mob
                
                load()
                st.success("✅ Member Updated Successfully!")
                
            except Exception as e:
                st.error(f"Error updating member: {e}")