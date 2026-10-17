# delete Record

from dbconn import get_db
from validators import valid_id
import pymysql as sql
import streamlit as st
from login import load

def delete_member():

    st.title("[Delete Member]")
    id = st.text_input("Enter Member Id U Want To Delete:")
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
                st.session_state.delete_record = record
                st.success("Member Found")
            else:
                st.error("Member Not Found...")
                st.session_state.pop('delete_record', None)
            db.close()
        except Exception as e:
            st.error(e)

    if 'delete_record' in st.session_state:
        st.write("**Member ID:**", st.session_state.delete_record['memberid'])
        st.write("**Member Name:**", st.session_state.delete_record['membername'])
        st.write("**Address:**", st.session_state.delete_record['address'])           # ✅ Fixed
        st.write("**Membership Start:**", st.session_state.delete_record['membershipstart'])
        st.write("**Membership End:**", st.session_state.delete_record['membershipend'])
        st.write("**Plan:**", st.session_state.delete_record['membershipplan'])       # ✅ Fixed
        st.write("**Mobile:**", st.session_state.delete_record['mobilenumber'])       # ✅ Fixed

        if st.button("Delete"):
            db = None
            try:
                db = get_db()
                smt = db.cursor()
                member_id = st.session_state.delete_record['memberid']
                # remove dependent rows first so foreign keys don't block the delete
                for tbl in ("attendance", "payments", "quiz_scores"):
                    try:
                        smt.execute(f"delete from {tbl} where member_id=%s", (member_id,))
                    except sql.err.ProgrammingError:
                        pass  # table doesn't exist yet
                smt.execute("delete from members where memberid=%s", (member_id,))
                load()
                db.commit()
                st.success("Member Deleted Successfully...")
                del st.session_state.delete_record
            except Exception as e:
                st.error(e)
            finally:
                if db:
                    db.close()
