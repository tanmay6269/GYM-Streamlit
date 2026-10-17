# Display Record....

from dbconn import get_db
import streamlit as st

def display_all_members():
    st.title("[Display All Records]")
    try:
        db=get_db()
        smt=db.cursor()
        smt.execute('Select * from members')
        records=smt.fetchall()
        st.dataframe([{k: v for k, v in r.items() if k.lower() != 'password'} for r in records])
        db.close()
    except Exception as e:
        st.error(e)