# delete Record
 
import pymysql as sql
import streamlit as st
from login import load

def delete_member():

    st.title("[Delete Member]")
    id = st.text_input("Enter Member Id U Want To Delete:")
    if st.button("Search"):
        try:
            db = sql.connect(host='localhost',port=3306,user='root',password='1234',database='TA_Fitness',cursorclass=sql.cursors.DictCursor)
            smt = db.cursor()
            smt.execute(f"select * from members where memberid={id}")
            record = smt.fetchone()
            load()

            if record:
                st.session_state.record = record
                st.success("Member Found")
            else:
                st.error("Member Not Found...")
            db.close()
        except Exception as e:
            st.error(e)
    
    if 'record' in st.session_state:
        st.write("**Member ID:**", st.session_state.record['memberid'])
        st.write("**Member Name:**", st.session_state.record['membername'])
        st.write("**Address:**", st.session_state.record['address'])           # ✅ Fixed
        st.write("**Membership Start:**", st.session_state.record['membershipstart'])
        st.write("**Membership End:**", st.session_state.record['membershipend'])
        st.write("**Plan:**", st.session_state.record['membershipplan'])       # ✅ Fixed
        st.write("**Mobile:**", st.session_state.record['mobilenumber'])       # ✅ Fixed
        
        if st.button("Delete"):
            db = sql.connect(host='localhost',port=3306,user='root',password='1234',database='TA_Fitness',cursorclass=sql.cursors.DictCursor)
            smt = db.cursor()
            q = f"delete from members where memberid={id}"
            smt.execute(q)
            load()

            db.commit()
            st.success("Member Deleted Successfully...")
            db.close()