import streamlit as st
from streamlit_option_menu import option_menu
from code3 import search_memberById
from code4 import edit_member
import pymysql as sql
from datetime import datetime
from dateutil.relativedelta import relativedelta

def team_dashboard():
    with st.sidebar:
        option = option_menu(
            "Team",
            [
                "Search Member",
                "Edit Member",
                "Attendance",
                "Renew Membership"
            ],
            icons=[
                "search",
                "pencil-square",
                "clipboard-check",
                "arrow-repeat"
            ],
            menu_icon="people-fill",
            default_index=0
        )
    
    if option == "Search Member":
        search_memberById()
    
    elif option == "Edit Member":
        edit_member()
    
    elif option == "Attendance":
        mark_attendance()
    
    elif option == "Renew Membership":
        team_renew_membership()

def mark_attendance():
    st.title("[Mark Attendance]")
    st.markdown("---")
    
    member_id = st.text_input("Enter Member ID:")
    
    if st.button("🔍 Check Member", use_container_width=True):
        if not member_id:
            st.warning("Please enter Member ID")
            return
        
        try:
            db = sql.connect(
                host='localhost', port=3306, user='root', password='1234',
                database='TA_Fitness', cursorclass=sql.cursors.DictCursor
            )
            smt = db.cursor()
            
            smt.execute(f"""
                SELECT memberid, membername, membershipplan, membershipend 
                FROM members 
                WHERE memberid={member_id} AND membershipend >= CURDATE()
            """)
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
                        FOREIGN KEY (member_id) REFERENCES members(memberid)
                    )
                """)
                
                # Check if already marked today
                today = datetime.now().date()
                smt.execute(f"""
                    SELECT * FROM attendance 
                    WHERE member_id={member_id} AND attendance_date='{today}'
                """)
                already_marked = smt.fetchone()
                
                # Store in session state
                st.session_state.attendance_member = member
                st.session_state.attendance_marked = already_marked is not None
                if already_marked:
                    st.session_state.attendance_time = already_marked['check_in_time']
                
                st.rerun()
            else:
                st.error("❌ Member not found or membership expired")
                if 'attendance_member' in st.session_state:
                    del st.session_state.attendance_member
            
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
            
            if st.button("🔄 Check Another Member", use_container_width=True):
                del st.session_state.attendance_member
                del st.session_state.attendance_marked
                if 'attendance_time' in st.session_state:
                    del st.session_state.attendance_time
                st.rerun()
        else:
            if st.button("✅ Mark Attendance", use_container_width=True, type="primary"):
                try:
                    db = sql.connect(
                        host='localhost', port=3306, user='root', password='1234',
                        database='TA_Fitness', cursorclass=sql.cursors.DictCursor
                    )
                    smt = db.cursor()
                    
                    today = datetime.now().date()
                    current_time = datetime.now().strftime("%H:%M:%S")
                    
                    smt.execute(f"""
                        INSERT INTO attendance (member_id, attendance_date, check_in_time, marked_by) 
                        VALUES ({member['memberid']}, '{today}', '{current_time}', 'Team')
                    """)
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
                    
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Today's attendance list
    st.markdown("---")
    st.subheader("📋 Today's Attendance")
    
    try:
        db = sql.connect(
            host='localhost', port=3306, user='root', password='1234',
            database='TA_Fitness', cursorclass=sql.cursors.DictCursor
        )
        smt = db.cursor()
        
        try:
            today = datetime.now().date()
            smt.execute(f"""
                SELECT m.membername, m.membershipplan, a.check_in_time
                FROM attendance a 
                JOIN members m ON a.member_id = m.memberid 
                WHERE a.attendance_date = '{today}' 
                ORDER BY a.check_in_time DESC
            """)
            records = smt.fetchall()
            
            if records:
                st.dataframe(records, use_container_width=True, hide_index=True)
                st.success(f"✅ Total Present Today: {len(records)}")
            else:
                st.info("📭 No attendance records for today")
        except:
            st.info("📋 Attendance will show after first check-in")
        
        db.close()
        
    except Exception as e:
        st.error(f"Error: {e}")


def team_renew_membership():
    st.title("[Renew Membership]")
    st.markdown("---")
    
    # Use a different session state key to avoid conflict
    id = st.text_input("Enter Member ID to renew:")
    
    if st.button("🔍 Search Member", use_container_width=True):
        if not id:
            st.warning("Please enter Member ID")
            return
        
        try:
            db = sql.connect(
                host='localhost', port=3306, user='root', password='1234',
                database='TA_Fitness', cursorclass=sql.cursors.DictCursor
            )
            smt = db.cursor()
            smt.execute(f"SELECT * FROM members WHERE memberid={id}")
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
            new_start_date = st.date_input("New Start Date:")
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
            if st.button("✅ Renew Membership", use_container_width=True, type="primary"):
                if not payment_received:
                    st.warning("⚠️ Please confirm payment received")
                    return
                
                try:
                    db = sql.connect(
                        host='localhost', port=3306, user='root', password='1234',
                        database='TA_Fitness', cursorclass=sql.cursors.DictCursor
                    )
                    smt = db.cursor()
                    
                    # Update membership
                    query = f"""
                        UPDATE members 
                        SET membershipstart='{new_start_date}', 
                            membershipend='{new_end_date}', 
                            membershipplan='{new_plan}' 
                        WHERE memberid={record['memberid']}
                    """
                    smt.execute(query)
                    
                    # Record payment
                    try:
                        pay_query = f"""
                            INSERT INTO payments (member_id, amount, payment_date, payment_mode, recorded_by) 
                            VALUES ({record['memberid']}, {amount}, CURDATE(), '{payment_mode}', 'Team')
                        """
                        smt.execute(pay_query)
                    except:
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
                        smt.execute(pay_query)
                    
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
            if st.button("❌ Cancel", use_container_width=True):
                del st.session_state.team_renew_data
                st.rerun()