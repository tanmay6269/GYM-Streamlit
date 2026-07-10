# Display Record....

import streamlit as st
import pymysql as sql

def display_all_members():
    st.title("[Display All Records]")
    try:
        db=sql.connect(host='localhost',port=3306,user='root',password='1234',database='TA_Fitness',cursorclass=sql.cursors.DictCursor)
        smt=db.cursor()
        smt.execute('Select * from Members')
        records=smt.fetchall()
        st.dataframe(records)
        db.close()
    except Exception as e:
        st.error(e)