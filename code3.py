# Search by id...

from dbconn import get_db
from validators import valid_id
import streamlit as st
from login import load

def search_memberById():
    st.title("[Search Member By Id]")
    id=st.text_input("Enter Member Id U Want To Search:")
    if(st.button('Submit')):
        if valid_id(id) is None:
            st.error("Member Id must be a number")
            return
        try:
            db=get_db()
            smt=db.cursor()
            smt.execute("Select * from members where memberid=%s", (id,))
            record=smt.fetchone()
            load()
            if(record):
                st.dataframe({k: v for k, v in record.items() if k.lower() != 'password'})
            else:
                st.error("Record does not Exists....")
            db.close()
        except Exception as e:
            st.error(e)