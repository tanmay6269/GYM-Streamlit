from dbconn import get_db, hash_password
import streamlit as st
from streamlit_option_menu import option_menu
from code1 import insert_member
from code2 import display_all_members
from code3 import search_memberById
from code4 import edit_member
from code5 import delete_member
import pymysql as sql
import pandas as pd
from dateutil.relativedelta import relativedelta

def admin_dashboard():
    with st.sidebar:
        menu = option_menu(
            "🏋️ GYM MANAGEMENT",
            [
                "Insert Member",
                "Display All Members",
                "Search Member By ID",
                "Edit Member",
                "Delete Member",
                "Add Staff",
                "Edit Staff",
                "View Reports",
                "Membership Renewal",
                "Payments",
                "Feedback"
            ],
            icons=[
                "person-plus-fill",
                "people-fill",
                "search",
                "pencil-square",
                "trash-fill",
                "person-plus",
                "person-gear",
                "graph-up",
                "arrow-repeat",
                "cash-coin",
                "chat-dots"
            ],
            menu_icon="activity",
            default_index=0
        )

    if menu == "Insert Member":
        insert_member()

    elif menu == "Display All Members":
        display_all_members()

    elif menu == "Search Member By ID":
        search_memberById()

    elif menu == "Edit Member":
        edit_member()

    elif menu == "Delete Member":
        delete_member()

    elif menu == "Add Staff":
        add_staff()

    elif menu == "Edit Staff":
        edit_staff()

    elif menu == "View Reports":
        view_reports()

    elif menu == "Membership Renewal":
        admin_renew_membership()

    elif menu == "Payments":
        manage_payments()

    elif menu == "Feedback":
        from footer import feedback_page
        feedback_page()

def add_staff():
    st.title("[Add Staff Member]")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        user_id = st.text_input("Staff ID:")
        user_name = st.text_input("Staff Name:")
        password = st.text_input("Password:", type="password")

    with col2:
        role = st.selectbox("Role:", ["Team", "Admin"])
        email = st.text_input("Email:")
        phone = st.text_input("Phone:")

    if st.button("Add Staff Member", width='stretch'):
        if not all([user_id, user_name, password, role]):
            st.warning("Please fill all required fields")
            return

        try:
            db = get_db()
            smt = db.cursor()

            query = """
                INSERT INTO user_login (User_id, User_Name, Password, Role, Email, Phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            smt.execute(query, (user_id, user_name, hash_password(password), role, email, phone))
            db.commit()
            db.close()

            st.success(f"Staff Member {user_name} added successfully!")

        except Exception as e:
            st.error(f"Error: {e}")

def edit_staff():
    st.title("[Edit Staff Member]")
    st.markdown("---")

    try:
        db = get_db()
        smt = db.cursor()
        smt.execute("SELECT User_id, User_Name, Role, Email, Phone FROM user_login")
        staff_list = smt.fetchall()
        db.close()

        if staff_list:
            st.dataframe(staff_list, width='stretch', hide_index=True)

            st.markdown("---")
            staff_id = st.selectbox("Select Staff to Edit:", [s['User_id'] for s in staff_list])

            if staff_id:
                selected_staff = next((s for s in staff_list if s['User_id'] == staff_id), None)

                if selected_staff:
                    col1, col2 = st.columns(2)

                    with col1:
                        new_name = st.text_input("Name:", value=selected_staff['User_Name'])
                        new_password = st.text_input("New Password:", type="password", placeholder="Leave blank to keep current")

                    with col2:
                        new_role = st.selectbox("Role:", ["Team", "Admin"], index=0 if selected_staff['Role'] == "Team" else 1)
                        new_email = st.text_input("Email:", value=selected_staff.get('Email') or '')
                        new_phone = st.text_input("Phone:", value=selected_staff.get('Phone') or '')

                    if st.button("Save Changes", width='stretch'):
                        try:
                            db = get_db()
                            smt = db.cursor()

                            if new_password:
                                query = """
                                    UPDATE user_login
                                    SET User_Name=%s, Password=%s, Role=%s,
                                        Email=%s, Phone=%s
                                    WHERE User_id=%s
                                """
                                params = (new_name, hash_password(new_password), new_role, new_email, new_phone, staff_id)
                            else:
                                query = """
                                    UPDATE user_login
                                    SET User_Name=%s, Role=%s,
                                        Email=%s, Phone=%s
                                    WHERE User_id=%s
                                """
                                params = (new_name, new_role, new_email, new_phone, staff_id)

                            smt.execute(query, params)
                            db.commit()
                            db.close()
                            st.success("✅ Staff member updated successfully!")

                            import time
                            time.sleep(1)
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error: {e}")
        else:
            st.info("No staff members found")

    except Exception as e:
        st.error(f"Error loading staff: {e}")

from datetime import datetime
import plotly.express as px

def view_reports():
    st.title("📊 Gym Analytics & Reports")

    # Report type selector with icons
    report_type = st.selectbox(
        "Select Report Type",
        [
            "📈 Dashboard Overview",
            "👥 Membership Analytics",
            "💰 Revenue Reports",
            "📋 Attendance Analytics",
            "⚠️ Expiring Memberships"
        ]
    )

    st.markdown("---")

    # ==================== DASHBOARD OVERVIEW ====================
    if report_type == "📈 Dashboard Overview":
        dashboard_overview()

    # ==================== MEMBERSHIP ANALYTICS ====================
    elif report_type == "👥 Membership Analytics":
        membership_analytics()

    # ==================== REVENUE REPORTS ====================
    elif report_type == "💰 Revenue Reports":
        revenue_reports()

    # ==================== ATTENDANCE ANALYTICS ====================
    elif report_type == "📋 Attendance Analytics":
        attendance_analytics()

    # ==================== EXPIRING MEMBERSHIPS ====================
    elif report_type == "⚠️ Expiring Memberships":
        expiring_memberships()

# ---------------------------------------------------------------

def dashboard_overview():
    try:
        db = get_db()
        smt = db.cursor()

        # Total Members
        smt.execute("SELECT COUNT(*) as count FROM members")
        total_members = smt.fetchone()['count']

        # Active Members
        smt.execute("SELECT COUNT(*) as count FROM members WHERE membershipend >= CURDATE()")
        active_members = smt.fetchone()['count']

        # Expired Members
        smt.execute("SELECT COUNT(*) as count FROM members WHERE membershipend < CURDATE()")
        expired_members = smt.fetchone()['count']

        # Today's new members
        smt.execute("SELECT COUNT(*) as count FROM members WHERE DATE(membershipstart) = CURDATE()")
        today_members = smt.fetchone()['count']

        # This month new members
        smt.execute("SELECT COUNT(*) as count FROM members WHERE MONTH(membershipstart) = MONTH(CURDATE()) AND YEAR(membershipstart) = YEAR(CURDATE())")
        month_members = smt.fetchone()['count']

        # Expiring this month
        smt.execute("SELECT COUNT(*) as count FROM members WHERE membershipend BETWEEN CURDATE() AND LAST_DAY(CURDATE())")
        expiring_soon = smt.fetchone()['count']

        # Today's attendance
        try:
            smt.execute("SELECT COUNT(DISTINCT member_id) as count FROM attendance WHERE attendance_date = CURDATE()")
            today_attendance = smt.fetchone()['count']
        except sql.err.ProgrammingError:
            today_attendance = 0

        db.close()

        # Metrics Row 1
        st.subheader("📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Members", total_members, delta=f"+{today_members} today", delta_color="normal")
        with col2:
            st.metric("Active Members", active_members, delta=f"{round(active_members/total_members*100)}% of total" if total_members > 0 else "0%")
        with col3:
            st.metric("Expired", expired_members, delta=f"{expiring_soon} expiring soon", delta_color="inverse")
        with col4:
            st.metric("Today's Check-ins", today_attendance)

        # Metrics Row 2
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("New This Month", month_members)
        with col2:
            active_rate = round(active_members/total_members*100) if total_members > 0 else 0
            st.metric("Retention Rate", f"{active_rate}%")
        with col3:
            st.metric("Expiring Soon", expiring_soon)
        with col4:
            try:
                _db = get_db()
                _c = _db.cursor()
                _c.execute("SELECT COUNT(*) AS paid, SUM(n > 1) AS repeat_paid FROM (SELECT COUNT(*) AS n FROM payments GROUP BY member_id) t")
                _r = _c.fetchone()
                _db.close()
                renewal_rate = round((_r['repeat_paid'] or 0) / _r['paid'] * 100) if _r['paid'] else 0
            except sql.err.ProgrammingError:
                renewal_rate = 0
            st.metric("Renewal Rate", f"{renewal_rate}%")

        st.markdown("---")

        # Plan Distribution Pie Chart
        db = get_db()
        smt = db.cursor()

        smt.execute("""
            SELECT membershipplan as Plan, COUNT(*) as Count
            FROM members WHERE membershipend >= CURDATE()
            GROUP BY membershipplan
        """)
        plan_data = smt.fetchall()
        db.close()

        if plan_data:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 Active Members by Plan")
                df_plans = pd.DataFrame(plan_data)
                fig = px.pie(df_plans, values='Count', names='Plan',
                            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#9B59B6'],
                            hole=0.4)
                fig.update_traces(textinfo='percent+value')
                fig.update_layout(height=400)
                st.plotly_chart(fig, width='stretch')

            with col2:
                st.subheader("📈 Plan Distribution")
                fig = px.bar(df_plans, x='Plan', y='Count',
                            color='Plan',
                            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#9B59B6'],
                            text='Count')
                fig.update_layout(height=400, showlegend=False)
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, width='stretch')

        # Revenue Overview
        st.markdown("---")
        st.subheader("💰 Revenue Overview (Active Members)")

        if plan_data:
            revenue_data = []
            for p in plan_data:
                plan = p['Plan']
                count = p['Count']
                if plan == '1 Month':
                    revenue = count * 1000
                elif plan == '3 Months':
                    revenue = count * 2400
                elif plan == '6 Months':
                    revenue = count * 4200
                elif plan == '12 Months':
                    revenue = count * 7000
                else:
                    revenue = 0
                revenue_data.append({'Plan': plan, 'Revenue': revenue})

            df_revenue = pd.DataFrame(revenue_data)
            total_revenue = df_revenue['Revenue'].sum()

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Active Revenue", f"₹{total_revenue:,.0f}")
                st.dataframe(df_revenue, width='stretch', hide_index=True)

            with col2:
                fig = px.bar(df_revenue, x='Plan', y='Revenue',
                            color='Plan',
                            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#9B59B6'])
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, width='stretch')

    except Exception as e:
        st.error(f"Error generating dashboard: {e}")

# ---------------------------------------------------------------

def membership_analytics():
    st.subheader("👥 Membership Analytics")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        plan_filter = st.selectbox("Filter by Plan", ["All", "1 Month", "3 Months", "6 Months", "12 Months"])

    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Active", "Expiring Soon", "Expired"])

    with col3:
        gender_filter = st.selectbox("Filter by Gender", ["All", "Male", "Female", "Other"])

    try:
        db = get_db()
        smt = db.cursor()

        # Build query based on filters
        query = "SELECT * FROM members WHERE 1=1"

        if plan_filter != "All":
            query += f" AND membershipplan = '{plan_filter}'"

        if status_filter == "Active":
            query += " AND membershipend >= CURDATE()"
        elif status_filter == "Expiring Soon":
            query += " AND membershipend BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)"
        elif status_filter == "Expired":
            query += " AND membershipend < CURDATE()"

        if gender_filter != "All":
            query += f" AND gender = '{gender_filter}'"

        query += " ORDER BY memberid"

        smt.execute(query)
        members = smt.fetchall()
        db.close()

        if members:
            st.metric("Filtered Members", len(members))

            # Convert to DataFrame for analysis
            df = pd.DataFrame(members)

            # Gender Distribution
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("⚥ Gender Distribution")
                gender_counts = df['gender'].value_counts()
                fig = px.pie(values=gender_counts.values, names=gender_counts.index,
                            color_discrete_sequence=['#3498db', '#e74c3c', '#2ecc71'])
                fig.update_traces(textinfo='percent+value')
                fig.update_layout(height=350)
                st.plotly_chart(fig, width='stretch')

            with col2:
                st.subheader("💪 Plan Distribution")
                plan_counts = df['membershipplan'].value_counts()
                fig = px.bar(x=plan_counts.index, y=plan_counts.values,
                            color=plan_counts.index,
                            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#9B59B6'])
                fig.update_layout(height=350, showlegend=False, xaxis_title="Plan", yaxis_title="Count")
                st.plotly_chart(fig, width='stretch')

            # Age Distribution (if DOB available)
            st.markdown("---")
            st.subheader("📅 Membership Join Trend")

            try:
                df['join_date'] = pd.to_datetime(df['membershipstart'])
                monthly_joins = df.groupby(df['join_date'].dt.to_period('M')).size().reset_index(name='count')
                monthly_joins['join_date'] = monthly_joins['join_date'].astype(str)

                fig = px.line(monthly_joins, x='join_date', y='count', markers=True,
                             title='Monthly New Members')
                fig.update_layout(height=400, xaxis_title="Month", yaxis_title="New Members")
                st.plotly_chart(fig, width='stretch')
            except Exception:
                st.info("Date analysis not available")

            # Detailed Table
            st.markdown("---")
            st.subheader("📋 Member Details")

            # Show only relevant columns
            display_df = df[['memberid', 'membername', 'gender', 'membershipplan', 'membershipstart', 'membershipend', 'mobilenumber']]
            st.dataframe(display_df, width='stretch', hide_index=True)

        else:
            st.info("No members found with selected filters")

    except Exception as e:
        st.error(f"Error: {e}")

# ---------------------------------------------------------------

def revenue_reports():
    st.subheader("💰 Revenue Reports")

    # Time period selector
    col1, col2 = st.columns(2)

    with col1:
        time_period = st.selectbox("Time Period", ["This Month", "Last Month", "This Year", "All Time"])

    with col2:
        view_type = st.selectbox("View", ["Summary", "By Plan", "Monthly Trend"])

    try:
        db = get_db()
        smt = db.cursor()

        period_sql = {
            "This Month": "AND YEAR(membershipstart) = YEAR(CURDATE()) AND MONTH(membershipstart) = MONTH(CURDATE())",
            "Last Month": "AND YEAR(membershipstart) = YEAR(CURDATE() - INTERVAL 1 MONTH) AND MONTH(membershipstart) = MONTH(CURDATE() - INTERVAL 1 MONTH)",
            "This Year": "AND YEAR(membershipstart) = YEAR(CURDATE())",
            "All Time": "",
        }[time_period]
        smt.execute(f"""
            SELECT membershipplan, COUNT(*) as count,
            CASE
                WHEN membershipplan = '1 Month' THEN COUNT(*) * 1000
                WHEN membershipplan = '3 Months' THEN COUNT(*) * 2400
                WHEN membershipplan = '6 Months' THEN COUNT(*) * 4200
                WHEN membershipplan = '12 Months' THEN COUNT(*) * 7000
                ELSE 0
            END as revenue
            FROM members WHERE membershipend >= CURDATE() {period_sql}
            GROUP BY membershipplan
        """)
        plan_revenue = smt.fetchall()
        db.close()

        if plan_revenue:
            total_revenue = sum(p['revenue'] for p in plan_revenue)

            # Revenue Summary
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Active Revenue", f"₹{total_revenue:,.0f}")
            with col2:
                avg_revenue = total_revenue / sum(p['count'] for p in plan_revenue) if sum(p['count'] for p in plan_revenue) > 0 else 0
                st.metric("Avg Per Member", f"₹{avg_revenue:,.0f}")
            with col3:
                st.metric("Total Active Members", sum(p['count'] for p in plan_revenue))
            with col4:
                max_plan = max(plan_revenue, key=lambda x: x['revenue'])
                st.metric("Top Plan", f"{max_plan['membershipplan']} (₹{max_plan['revenue']:,.0f})")

            st.markdown("---")

            if view_type == "Summary":
                df = pd.DataFrame(plan_revenue)
                df.columns = ['Plan', 'Members', 'Revenue']
                st.dataframe(df, width='stretch', hide_index=True)

            elif view_type == "By Plan":
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("📊 Revenue by Plan")
                    df = pd.DataFrame(plan_revenue)
                    fig = px.bar(df, x='membershipplan', y='revenue',
                                color='membershipplan',
                                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#9B59B6'],
                                text='revenue')
                    fig.update_layout(height=400, showlegend=False)
                    fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
                    st.plotly_chart(fig, width='stretch')

                with col2:
                    st.subheader("🥧 Revenue Share")
                    fig = px.pie(df, values='revenue', names='membershipplan',
                                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#9B59B6'])
                    fig.update_traces(textinfo='percent+label')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width='stretch')

            elif view_type == "Monthly Trend":
                st.subheader("📈 Monthly Revenue Trend")
                # This would need payment history table
                try:
                    db = get_db()
                    smt = db.cursor()
                    smt.execute("""
                        SELECT DATE_FORMAT(payment_date, '%Y-%m') as month, SUM(amount) as total
                        FROM payments GROUP BY month ORDER BY month
                    """)
                    monthly_data = smt.fetchall()
                    db.close()

                    if monthly_data:
                        df = pd.DataFrame(monthly_data)
                        fig = px.line(df, x='month', y='total', markers=True)
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, width='stretch')
                    else:
                        st.info("No monthly data available yet")
                except sql.err.ProgrammingError:
                    st.info("Payment history tracking will show trends over time")
        else:
            st.info("No active members found")

    except Exception as e:
        st.error(f"Error: {e}")

# ---------------------------------------------------------------

def attendance_analytics():
    st.subheader("📋 Attendance Analytics")

    try:
        db = get_db()
        smt = db.cursor()

        # Check if attendance table exists
        try:
            smt.execute("""
                SELECT COUNT(DISTINCT member_id) as total_checked_in,
                       COUNT(*) as total_checkins
                FROM attendance WHERE attendance_date = CURDATE()
            """)
            today_stats = smt.fetchone()

            smt.execute("""
                SELECT COUNT(DISTINCT member_id) as total_checked_in,
                       COUNT(*) as total_checkins
                FROM attendance WHERE MONTH(attendance_date) = MONTH(CURDATE())
                AND YEAR(attendance_date) = YEAR(CURDATE())
            """)
            month_stats = smt.fetchone()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Today's Check-ins", today_stats['total_checked_in'] or 0)
            with col2:
                st.metric("Today's Total Entries", today_stats['total_checkins'] or 0)
            with col3:
                st.metric("This Month Unique", month_stats['total_checked_in'] or 0)
            with col4:
                st.metric("This Month Total", month_stats['total_checkins'] or 0)

            st.markdown("---")

            # Weekly attendance trend
            st.subheader("📈 Last 7 Days Attendance")
            smt.execute("""
                SELECT attendance_date, COUNT(DISTINCT member_id) as count
                FROM attendance
                WHERE attendance_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY attendance_date
                ORDER BY attendance_date
            """)
            weekly_data = smt.fetchall()

            if weekly_data:
                df = pd.DataFrame(weekly_data)
                fig = px.bar(df, x='attendance_date', y='count',
                            title='Daily Attendance (Last 7 Days)')
                fig.update_layout(height=400)
                st.plotly_chart(fig, width='stretch')

            # Peak hours
            st.markdown("---")
            st.subheader("⏰ Peak Hours")
            smt.execute("""
                SELECT HOUR(check_in_time) as hour, COUNT(*) as count
                FROM attendance
                GROUP BY HOUR(check_in_time)
                ORDER BY hour
            """)
            hourly_data = smt.fetchall()

            if hourly_data:
                df = pd.DataFrame(hourly_data)
                fig = px.line(df, x='hour', y='count', markers=True,
                             title='Check-in Time Distribution')
                fig.update_layout(height=350, xaxis_title="Hour of Day", yaxis_title="Check-ins")
                st.plotly_chart(fig, width='stretch')

        except sql.err.ProgrammingError:
            st.info("📋 Attendance tracking will show data after members start checking in")
            st.info("Use the Team panel to mark attendance")

        db.close()

    except Exception as e:
        st.error(f"Error: {e}")

# ---------------------------------------------------------------

def expiring_memberships():
    st.subheader("⚠️ Expiring Memberships")

    # Time filter
    time_frame = st.selectbox("Show memberships expiring in:", ["7 Days", "15 Days", "30 Days", "All Expired"])

    try:
        db = get_db()
        smt = db.cursor()

        if time_frame == "7 Days":
            query = """
                SELECT * FROM members
                WHERE membershipend BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
                ORDER BY membershipend ASC
            """
        elif time_frame == "15 Days":
            query = """
                SELECT * FROM members
                WHERE membershipend BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 15 DAY)
                ORDER BY membershipend ASC
            """
        elif time_frame == "30 Days":
            query = """
                SELECT * FROM members
                WHERE membershipend BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
                ORDER BY membershipend ASC
            """
        else:
            query = """
                SELECT * FROM members
                WHERE membershipend < CURDATE()
                ORDER BY membershipend DESC
            """

        smt.execute(query)
        members = smt.fetchall()
        db.close()

        if members:
            count = len(members)

            if time_frame == "All Expired":
                st.warning(f"🚨 {count} members have expired memberships")
            else:
                st.warning(f"⚠️ {count} memberships expiring within {time_frame.lower()}")

            # Create summary
            # Display with days remaining
            st.markdown("---")

            for i, member in enumerate(members):
                end_date = member['membershipend']
                if isinstance(end_date, str):
                    end_date = datetime.strptime(str(end_date), '%Y-%m-%d').date()

                days_left = (end_date - datetime.now().date()).days

                if days_left < 0:
                    status = "🔴 Expired"
                    days_text = f"{abs(days_left)} days ago"
                elif days_left == 0:
                    status = "🟡 Expires Today"
                    days_text = "Today"
                elif days_left <= 7:
                    status = "🟠 Expiring Soon"
                    days_text = f"{days_left} days left"
                else:
                    status = "🟢 Active"
                    days_text = f"{days_left} days left"

                with st.expander(f"{status} | {member['membername']} | {member['membershipplan']} | {days_text}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(f"**ID:** {member['memberid']}")
                        st.write(f"**Name:** {member['membername']}")
                        st.write(f"**Gender:** {member['gender']}")

                    with col2:
                        st.write(f"**Plan:** {member['membershipplan']}")
                        st.write(f"**Start:** {member['membershipstart']}")
                        st.write(f"**End:** {member['membershipend']}")

                    with col3:
                        st.write(f"**Mobile:** {member['mobilenumber']}")
                        st.write(f"**Address:** {member['address']}")
                        if days_left <= 0:
                            st.error("Membership Expired!")
                        elif days_left <= 7:
                            st.warning("Renewal Needed!")

            # Pie chart
            st.markdown("---")
            st.subheader("📊 Expiry Status Distribution")

            expired_count = len([m for m in members if (m['membershipend'] if isinstance(m['membershipend'], datetime) else datetime.strptime(str(m['membershipend']), '%Y-%m-%d').date()) < datetime.now().date()])
            expiring_7 = len([m for m in members if 0 <= ((m['membershipend'] if isinstance(m['membershipend'], datetime) else datetime.strptime(str(m['membershipend']), '%Y-%m-%d').date()) - datetime.now().date()).days <= 7])
            expiring_30 = len([m for m in members if 7 < ((m['membershipend'] if isinstance(m['membershipend'], datetime) else datetime.strptime(str(m['membershipend']), '%Y-%m-%d').date()) - datetime.now().date()).days <= 30])

            pie_data = pd.DataFrame({
                'Status': ['Expired', 'Expiring (7 days)', 'Expiring (30 days)'],
                'Count': [expired_count, expiring_7, expiring_30]
            })

            fig = px.pie(pie_data, values='Count', names='Status',
                        color_discrete_sequence=['#e74c3c', '#f39c12', '#3498db'])
            fig.update_traces(textinfo='percent+value')
            st.plotly_chart(fig, width='stretch')

        else:
            if time_frame == "All Expired":
                st.success("✅ No expired memberships!")
            else:
                st.success(f"✅ No memberships expiring in {time_frame.lower()}!")

    except Exception as e:
        st.error(f"Error: {e}")

def admin_renew_membership():
    st.title("[Renew Membership]")
    st.markdown("---")

    # Step 1: Search for member
    st.subheader("1: Search Member")
    id = st.text_input("Enter Member ID to renew:")

    if st.button("🔍 Search Member", width='stretch'):
        if not id:
            st.warning("Please enter a Member ID")
            return

        try:
            db = get_db()
            smt = db.cursor()
            smt.execute("SELECT * FROM members WHERE memberid=%s", (id,))
            record = smt.fetchone()
            db.close()

            if record:
                st.session_state.renew_record = record
                st.success(f"✅ Member Found: {record['membername']}")
                st.rerun()
            else:
                st.error("❌ Member not found")
                if 'renew_record' in st.session_state:
                    del st.session_state.renew_record
        except Exception as e:
            st.error(f"Error: {e}")

    # Step 2: Show renewal form if member is found
    if 'renew_record' in st.session_state:
        record = st.session_state.renew_record

        st.markdown("---")
        st.subheader("2: Renew Membership")

        # Show current member details
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Name:** {record['membername']}")
            st.write(f"**Current Plan:** {record['membershipplan']}")
        with col2:
            st.write(f"**Start:** {record['membershipstart']}")
            st.write(f"**End:** {record['membershipend']}")
        with col3:
            st.write(f"**Mobile:** {record['mobilenumber']}")
            st.write(f"**Gender:** {record['gender']}")

        st.markdown("---")

        # Renewal form
        col1, col2 = st.columns(2)

        with col1:
            current_end = record['membershipend']
            if isinstance(current_end, str):
                current_end = datetime.strptime(current_end, '%Y-%m-%d').date()
            new_start_date = st.date_input("New Start Date:", value=max(current_end, datetime.now().date()))
            new_plan = st.selectbox(
                "New Plan:",
                ['1 Month', '3 Months', '6 Months', '12 Months']
            )

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

        st.markdown("---")
        st.subheader("3: Payment Details")

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
                        pay_params = (record['memberid'], amount, payment_mode, st.session_state.user.get('Name', 'Admin'))
                        smt.execute(pay_query, pay_params)
                    except sql.err.ProgrammingError:
                        # Create payments table if not exists
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

                    import time
                    time.sleep(1.5)
                    del st.session_state.renew_record
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {e}")

        with col2:
            if st.button("❌ Cancel", width='stretch'):
                del st.session_state.renew_record
                st.rerun()


def manage_payments():
    st.title("[Manage Payments]")
    st.markdown("---")

    # Tabs for record payment and view history
    tab1, tab2 = st.tabs(["💳 Record Payment", "📋 Payment History"])

    with tab1:
        st.subheader("Record New Payment")

        col1, col2 = st.columns(2)

        with col1:
            member_id = st.text_input("Member ID:", key="pay_member_id")
            amount = st.number_input("Amount (₹):", min_value=0, step=100, key="pay_amount")

        with col2:
            payment_date = st.date_input("Payment Date:", key="pay_date")
            payment_mode = st.selectbox("Payment Mode:", ["Cash", "Card", "UPI", "Bank Transfer"], key="pay_mode")

        if st.button("💳 Record Payment", width='stretch', type="primary"):
            if not member_id or amount == 0:
                st.warning("⚠️ Please fill all fields")
                return

            try:
                db = get_db()
                smt = db.cursor()

                # Create table if not exists
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

                # Check if member exists
                smt.execute("SELECT membername FROM members WHERE memberid=%s", (member_id,))
                member = smt.fetchone()

                if not member:
                    st.error("❌ Member ID not found")
                    db.close()
                    return

                query = """
                    INSERT INTO payments (member_id, amount, payment_date, payment_mode, recorded_by)
                    VALUES (%s, %s, %s, %s, %s)
                """
                smt.execute(query, (member_id, amount, payment_date, payment_mode, st.session_state.user.get('Name', 'Admin')))
                db.commit()
                db.close()

                st.success(f"✅ Payment of ₹{amount} recorded for {member['membername']} (ID: {member_id})")
                st.balloons()

            except Exception as e:
                st.error(f"❌ Error: {e}")

    with tab2:
        st.subheader("Recent Payments")

        try:
            db = get_db()
            smt = db.cursor()

            try:
                smt.execute("""
                    SELECT p.payment_id, p.member_id, m.membername, p.amount,
                           p.payment_date, p.payment_mode, p.recorded_by
                    FROM payments p
                    JOIN members m ON p.member_id = m.memberid
                    ORDER BY p.payment_date DESC
                    LIMIT 50
                """)
                payments = smt.fetchall()

                if payments:
                    smt.execute("SELECT COUNT(*) AS cnt, COALESCE(SUM(amount), 0) AS total FROM payments")
                    totals = smt.fetchone()
                    st.metric("Total Payments", totals['cnt'])
                    st.metric("Total Amount", f"₹{totals['total']:,.0f}")

                    st.markdown("---")
                    st.dataframe(payments, width='stretch', hide_index=True)
                else:
                    st.info("📭 No payments recorded yet")
            except sql.err.ProgrammingError:
                st.info("📭 Payment tracking will be available after first payment is recorded")

            db.close()

        except Exception as e:
            st.error(f"❌ Error loading payments: {e}")