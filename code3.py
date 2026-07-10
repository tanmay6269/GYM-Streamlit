# Search by id...

import streamlit as st
import pymysql as sql
from login import load

def search_memberById():
    st.title("[Search Member By Id]")
    id=st.text_input("Enter Member Id U Want To Search:")
    if(st.button('Submit')):
        try:
            db=sql.connect(host='localhost',port=3306,user='root',password='1234',database='TA_Fitness',cursorclass=sql.cursors.DictCursor)
            smt=db.cursor()
            smt.execute(f"Select * from members where memberid={id}")
            record=smt.fetchone()
            load()
            if(record):
                st.dataframe(record)
            else:
                st.error(f"Record does not Exists....")
            db.close()
        except Exception as e:
            st.error(e)