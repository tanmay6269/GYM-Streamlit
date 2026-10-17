from dbconn import get_db
import streamlit as st
import pymysql as sql
from datetime import datetime
from dateutil.relativedelta import relativedelta

def mark_attendance():
    st.title("[Mark Attendance]")
    st.markdown("---")

    member_id = st.text_input("Enter Member ID:")

    if st.button("🔍 Check Member", width='stretch'):
        if not member_id:
            st.warning("Please enter Member ID")
            return

        try:
            db = get_db()
            smt = db.cursor()

            smt.execute("""
                SELECT memberid, membername, membershipplan, membershipend
                FROM members
                WHERE memberid=%s AND membershipend >= CURDATE()
            """, (member_id,))
            member = smt.fetchone()

            if member:
                # Create attendance table
                smt.execute("""
                    CREATE TABLE IF NOT EXISTS attendance (
                        attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                        member_id INT,
                        attendance_date DATE,
                        check_in_time TIME,
                        marked_by VARCHAR(100),
                        UNIQUE KEY uq_member_day (member_id, attendance_date),
                        FOREIGN KEY (member_id) REFERENCES members(memberid)
                    )
                """)

                # Check if already marked today
                today = datetime.now().date()
                smt.execute("""
                    SELECT * FROM attendance
                    WHERE member_id=%s AND attendance_date=%s
                """, (member['memberid'], today))
                already_marked = smt.fetchone()

                # Store in session state
                st.session_state.attendance_member = member
                st.session_state.attendance_marked = already_marked is not None
                if already_marked:
                    st.session_state.attendance_time = already_marked['check_in_time']

                db.close()
                st.rerun()
            else:
                st.error("❌ Member not found or membership expired")
                if 'attendance_member' in st.session_state:
                    del st.session_state.attendance_member
                    st.session_state.pop('attendance_marked', None)

            db.close()

        except Exception as e:
            st.error(f"Error: {e}")

    # Show member details after search
    if 'attendance_member' in st.session_state:
        member = st.session_state.attendance_member

        st.success(f"✅ Active Member: {member['membername']}")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Plan:** {member['membershipplan']}")
        with col2:
            end_date = member['membershipend']
            if isinstance(end_date, str):
                end_date = datetime.strptime(str(end_date), '%Y-%m-%d').date()
            days_left = (end_date - datetime.now().date()).days
            st.write(f"**Days Remaining:** {days_left}")

        st.markdown("---")

        # Show mark button or already marked message
        if st.session_state.attendance_marked:
            st.warning(f"⚠️ Attendance already marked today at {st.session_state.attendance_time}")

            if st.button("🔄 Check Another Member", width='stretch'):
                del st.session_state.attendance_member
                del st.session_state.attendance_marked
                if 'attendance_time' in st.session_state:
                    del st.session_state.attendance_time
                st.rerun()
        else:
            if st.button("✅ Mark Attendance", width='stretch', type="primary"):
                try:
                    db = get_db()
                    smt = db.cursor()

                    today = datetime.now().date()
                    current_time = datetime.now().strftime("%H:%M:%S")

                    smt.execute("""
                        INSERT INTO attendance (member_id, attendance_date, check_in_time, marked_by)
                        VALUES (%s, %s, %s, %s)
                    """, (member['memberid'], today, current_time, st.session_state.user.get('Name', 'Team')))
                    db.commit()
                    db.close()

                    st.success(f"✅ Attendance marked for {member['membername']} at {current_time}!")
                    st.balloons()

                    # Clear and refresh
                    del st.session_state.attendance_member
                    del st.session_state.attendance_marked
                    import time
                    time.sleep(1)
                    st.rerun()

                except sql.err.IntegrityError:
                    st.warning("⚠️ Attendance already marked today")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Today's attendance list
    st.markdown("---")
    st.subheader("📋 Today's Attendance")

    try:
        db = get_db()
        smt = db.cursor()

        try:
            today = datetime.now().date()
            smt.execute("""
                SELECT m.membername, m.membershipplan, a.check_in_time
                FROM attendance a
                JOIN members m ON a.member_id = m.memberid
                WHERE a.attendance_date = %s
                ORDER BY a.check_in_time DESC
            """, (today,))
            records = smt.fetchall()

            if records:
                st.dataframe(records, width='stretch', hide_index=True)
                st.success(f"✅ Total Present Today: {len(records)}")
            else:
                st.info("📭 No attendance records for today")
        except sql.err.ProgrammingError:
            st.info("📋 Attendance will show after first check-in")

        db.close()

    except Exception as e:
        st.error(f"Error: {e}")


def team_renew_membership():
    st.title("[Renew Membership]")
    st.markdown("---")

    # Use a different session state key to avoid conflict
    id = st.text_input("Enter Member ID to renew:")

    if st.button("🔍 Search Member", width='stretch'):
        if not id:
            st.warning("Please enter Member ID")
            return

        try:
            db = get_db()
            smt = db.cursor()
            smt.execute("SELECT * FROM members WHERE memberid=%s", (id,))
            record = smt.fetchone()
            db.close()

            if record:
                st.session_state.team_renew_data = record
                st.rerun()
            else:
                st.error("❌ Member not found")
                if 'team_renew_data' in st.session_state:
                    del st.session_state.team_renew_data
        except Exception as e:
            st.error(f"Error: {e}")

    # Show renewal form
    if 'team_renew_data' in st.session_state:
        record = st.session_state.team_renew_data

        st.success(f"✅ Member Found: {record['membername']}")
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            current_end = record['membershipend']
            if isinstance(current_end, str):
                current_end = datetime.strptime(current_end, '%Y-%m-%d').date()
            new_start_date = st.date_input("New Start Date:", value=max(current_end, datetime.now().date()))
            new_plan = st.selectbox("New Plan:", ['1 Month', '3 Months', '6 Months', '12 Months'])

        with col2:
            if new_plan == "1 Month":
                new_end_date = new_start_date + relativedelta(months=1)
                amount = 1000
            elif new_plan == "3 Months":
                new_end_date = new_start_date + relativedelta(months=3)
                amount = 2400
            elif new_plan == "6 Months":
                new_end_date = new_start_date + relativedelta(months=6)
                amount = 4200
            else:
                new_end_date = new_start_date + relativedelta(months=12)
                amount = 7000

            st.date_input("New End Date:", value=new_end_date, disabled=True)
            st.metric("💰 Amount to Pay", f"₹{amount}")

        col1, col2 = st.columns(2)
        with col1:
            payment_mode = st.selectbox("Payment Mode:", ["Cash", "Card", "UPI", "Bank Transfer"])
        with col2:
            payment_received = st.checkbox("✅ Payment Received", value=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Renew Membership", width='stretch', type="primary"):
                if not payment_received:
                    st.warning("⚠️ Please confirm payment received")
                    return

                try:
                    db = get_db()
                    smt = db.cursor()

                    # Update membership
                    query = """
                        UPDATE members
                        SET membershipstart=%s,
                            membershipend=%s,
                            membershipplan=%s
                        WHERE memberid=%s
                    """
                    smt.execute(query, (new_start_date, new_end_date, new_plan, record['memberid']))

                    # Record payment
                    try:
                        pay_query = """
                            INSERT INTO payments (member_id, amount, payment_date, payment_mode, recorded_by)
                            VALUES (%s, %s, CURDATE(), %s, %s)
                        """
                        pay_params = (record['memberid'], amount, payment_mode, st.session_state.user.get('Name', 'Team'))
                        smt.execute(pay_query, pay_params)
                    except sql.err.ProgrammingError:
                        smt.execute("""
                            CREATE TABLE IF NOT EXISTS payments (
                                payment_id INT AUTO_INCREMENT PRIMARY KEY,
                                member_id INT,
                                amount DECIMAL(10,2),
                                payment_date DATE,
                                payment_mode VARCHAR(50),
                                recorded_by VARCHAR(100),
                                FOREIGN KEY (member_id) REFERENCES members(memberid)
                            )
                        """)
                        smt.execute(pay_query, pay_params)

                    db.commit()
                    db.close()

                    st.success(f"✅ Membership renewed for {record['membername']}!")
                    st.balloons()

                    # Clear and refresh
                    del st.session_state.team_renew_data
                    import time
                    time.sleep(1.5)
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {e}")

        with col2:
            if st.button("❌ Cancel", width='stretch'):
                del st.session_state.team_renew_data
                st.rerun()