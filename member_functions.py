import re
from dbconn import get_db, hash_password
from validators import valid_date
import streamlit as st
import pymysql as sql
from datetime import datetime, timedelta
from PIL import Image
from pathlib import Path
import calendar

PHOTO_DIR = Path(__file__).parent / "profile_photos"
LOGO = str(Path(__file__).parent / "gym.png")

def display_member_profile(member_id):
    st.title(":material/person: My Profile")
    st.markdown("---")

    try:
        db = get_db()
        smt = db.cursor()

        smt.execute("SELECT * FROM members WHERE memberid = %s", (member_id,))
        member = smt.fetchone()
        db.close()

        if member:
            # Profile Photo Section
            st.markdown("### :material/photo_camera: Profile Photo")

            col1, col2 = st.columns([1, 3])

            with col1:
                photo_path = PHOTO_DIR / f"{member_id}.jpg"
                if photo_path.exists():
                    st.image(str(photo_path), width=150)
                else:
                    st.image(LOGO, width=150)

            with col2:
                uploaded_file = st.file_uploader("Upload Profile Photo", type=['jpg', 'jpeg', 'png'])
                photo_key = (member_id, uploaded_file.name, uploaded_file.size) if uploaded_file is not None else None
                if uploaded_file is not None and st.session_state.get("photo_saved") != photo_key:
                    PHOTO_DIR.mkdir(exist_ok=True)
                    image = Image.open(uploaded_file).convert("RGB")
                    image = image.resize((300, 300))
                    image.save(PHOTO_DIR / f"{member_id}.jpg")
                    st.session_state.photo_saved = photo_key
                    st.success(":material/check_circle: Profile photo updated!")
                    st.rerun()

            st.markdown("---")

            # Personal Information (Read Only + Editable fields)
            st.markdown("### :material/assignment: Personal Information")

            col1, col2 = st.columns(2)

            with col1:
                # Read Only
                st.text_input("Name:", value=member['membername'], disabled=True)
                st.text_input("Gender:", value=member['gender'], disabled=True)
                st.text_input("Mobile:", value=member['mobilenumber'], disabled=True)

            with col2:
                # Read Only
                st.text_input("Membership Plan:", value=member['membershipplan'], disabled=True)

                # Editable
                new_dob = st.text_input("Date of Birth:", value=str(member['dob']) if member['dob'] else "")
                new_address = st.text_area("Address:", value=member['address'] if member['address'] else "", height=80)
                new_password = st.text_input("New Password:", type="password", placeholder="Leave blank to keep current")

            if st.button(":material/save: Save Changes", width='stretch', type="primary"):
                if new_dob.strip() and valid_date(new_dob) is None:
                    st.error(":material/cancel: Date of Birth must be a valid date in YYYY-MM-DD format")
                    return
                try:
                    db = get_db()
                    smt = db.cursor()

                    dob_value = new_dob.strip() or None
                    if new_password:
                        query = """
                            UPDATE members
                            SET dob=%s, address=%s, Password=%s
                            WHERE memberid=%s
                        """
                        params = (dob_value, new_address, hash_password(new_password), member_id)
                    else:
                        query = """
                            UPDATE members
                            SET dob=%s, address=%s
                            WHERE memberid=%s
                        """
                        params = (dob_value, new_address, member_id)

                    smt.execute(query, params)
                    db.commit()
                    db.close()

                    st.success(":material/check_circle: Profile updated successfully!")
                    import time
                    time.sleep(1)
                    st.rerun()

                except Exception as e:
                    st.error(f":material/cancel: Error updating profile: {e}")

            st.markdown("---")

            # Membership Details (Read Only)
            st.markdown("### :material/fitness_center: Membership Information")

            # Convert dates to strings for display
            end_date = member['membershipend']
            start_date = member['membershipstart']

            if isinstance(end_date, str):
                end_date_str = end_date
                end_date = datetime.strptime(str(end_date), '%Y-%m-%d').date()
            else:
                end_date_str = str(end_date)
                end_date = end_date if hasattr(end_date, 'date') else end_date

            if isinstance(start_date, str):
                start_date_str = start_date
                start_date = datetime.strptime(str(start_date), '%Y-%m-%d').date()
            else:
                start_date_str = str(start_date)
                start_date = start_date if hasattr(start_date, 'date') else start_date

            # Display metrics with STRING values
            col3, col4, col5 = st.columns(3)

            with col3:
                st.metric("Plan", str(member['membershipplan']))
            with col4:
                st.metric("Start Date", str(start_date_str))
            with col5:
                st.metric("End Date", str(end_date_str))

            # Calculate remaining days
            today = datetime.now().date()

            # Ensure dates are date objects
            if hasattr(end_date, 'date'):
                end_date = end_date.date()
            if hasattr(start_date, 'date'):
                start_date = start_date.date()

            days_left = (end_date - today).days
            total_days = (end_date - start_date).days
            elapsed_days = (today - start_date).days

            st.markdown("---")

            if days_left < 0:
                st.error(f":material/warning: Membership Expired ({abs(days_left)} days ago)")
            elif days_left <= 7:
                st.warning(f":material/warning: Membership expiring soon ({days_left} days left)")
            else:
                st.success(f":material/check_circle: Active Membership ({days_left} days remaining)")

            # Progress bar
            if total_days > 0:
                progress = min(max(elapsed_days / total_days, 0), 1)
                st.progress(progress, text=f"Membership Progress: {int(progress * 100)}%")

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"⏳ Days Elapsed: {elapsed_days}")
                with col2:
                    st.write(f":material/calendar_month: Days Remaining: {max(days_left, 0)}")
        else:
            st.error(":material/cancel: Member record not found")

    except Exception as e:
        st.error(f":material/cancel: Error loading profile: {e}")

# ---------------------------------------------------------------

def display_membership_details(member_id):
    st.title(":material/fitness_center: My Membership")
    st.markdown("---")

    try:
        db = get_db()
        smt = db.cursor()

        smt.execute("SELECT * FROM members WHERE memberid = %s", (member_id,))
        member = smt.fetchone()
        db.close()

        if member:
            st.markdown(f"### :material/fitness_center: Hello, {member['membername']}!")

            # Membership Status Card
            end_date = member['membershipend']
            start_date = member['membershipstart']

            if isinstance(end_date, str):
                end_date = datetime.strptime(str(end_date), '%Y-%m-%d').date()
            if isinstance(start_date, str):
                start_date = datetime.strptime(str(start_date), '%Y-%m-%d').date()

            today = datetime.now().date()
            days_left = (end_date - today).days
            total_days = (end_date - start_date).days

            # Status card
            if days_left < 0:
                st.error(f"### :red[:material/circle:] Membership Expired - {abs(days_left)} days ago")
            elif days_left <= 7:
                st.warning(f"### :orange[:material/circle:] Expiring Soon - {days_left} days remaining")
            elif days_left <= 30:
                st.info(f"### :blue[:material/circle:] Active - {days_left} days remaining")
            else:
                st.success(f"### :green[:material/circle:] Active - {days_left} days remaining")

            st.markdown("---")

            # Plan Details
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### :material/assignment: Current Plan")
                st.write(f"**Plan:** {member['membershipplan']}")
                st.write(f"**Start Date:** {start_date}")
                st.write(f"**End Date:** {end_date}")
                st.write(f"**Total Duration:** {total_days} days")

            with col2:
                st.markdown("#### :material/bar_chart: Progress")
                elapsed_days = (today - start_date).days
                progress_pct = min(max(elapsed_days / total_days * 100, 0), 100) if total_days > 0 else 0
                st.write(f"**Days Completed:** {elapsed_days}")
                st.write(f"**Days Remaining:** {max(days_left, 0)}")
                st.write(f"**Progress:** {progress_pct:.1f}%")

            st.markdown("---")

            # Plan Benefits
            st.markdown("#### :material/redeem: Your Plan Benefits")

            plan = member['membershipplan']
            if plan == '1 Month':
                benefits = {
                    ":material/fitness_center: Gym Access": "Basic gym floor access",
                    ":material/lock: Locker": "Daily locker facility",
                    ":material/school: Training": "1 Personal training session",
                    ":material/schedule: Timing": "6 AM - 10 PM",
                    ":material/calendar_month: Validity": "30 days"
                }
                color = "#FF6B6B"
            elif plan == '3 Months':
                benefits = {
                    ":material/fitness_center: Gym Access": "Full gym floor access",
                    ":material/lock: Locker": "Permanent locker",
                    ":material/school: Training": "3 Personal training sessions",
                    ":material/nutrition: Diet Plan": "Basic diet consultation",
                    ":material/schedule: Timing": "5 AM - 11 PM",
                    ":material/calendar_month: Validity": "90 days"
                }
                color = "#4ECDC4"
            elif plan == '6 Months':
                benefits = {
                    ":material/fitness_center: Gym Access": "Full premium access",
                    ":material/lock: Locker": "Premium locker",
                    ":material/school: Training": "6 Personal training sessions",
                    ":material/nutrition: Diet Plan": "Customized diet plan",
                    ":material/medication: Supplements": "Free supplements sample",
                    ":material/schedule: Timing": "24/7 Access",
                    ":material/calendar_month: Validity": "180 days"
                }
                color = "#45B7D1"
            else:  # 12 Months
                benefits = {
                    ":material/fitness_center: Gym Access": "VIP all access",
                    ":material/lock: Locker": "VIP locker",
                    ":material/school: Training": "12 Personal training sessions",
                    ":material/nutrition: Diet Plan": "Premium diet plan",
                    ":material/medication: Supplements": "Monthly supplements kit",
                    ":material/spa: Spa": "Free spa access",
                    ":material/directions_car: Parking": "Free valet parking",
                    ":material/schedule: Timing": "24/7 Access",
                    ":material/calendar_month: Validity": "365 days"
                }
                color = "#9B59B6"

            # Display benefits in cards
            cols = st.columns(2)
            for i, (benefit, description) in enumerate(benefits.items()):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div style='background: {color}; padding: 15px; border-radius: 10px; margin-bottom: 10px; color: white;'>
                        <strong>{re.sub(r':material/([a-z_]+):', r'<span class="ms"></span>', benefit)}</strong><br>
                        <small>{description}</small>
                    </div>
                    """, unsafe_allow_html=True)

            # Renewal Call-to-Action
            if days_left <= 15:
                st.markdown("---")
                st.warning(":material/sync: Your membership is expiring soon! Contact the front desk to renew.")
                if st.button(":material/call: Request Renewal Callback", width='stretch'):
                    st.success(":material/check_circle: Renewal request submitted! Team will contact you shortly.")

        else:
            st.error(":material/cancel: Member record not found")

    except Exception as e:
        st.error(f":material/cancel: Error: {e}")

# ---------------------------------------------------------------

def display_attendance(member_id):
    st.title(":material/bar_chart: My Attendance")
    st.markdown("---")

    try:
        db = get_db()
        smt = db.cursor()

        try:
            # Total attendance
            smt.execute("SELECT COUNT(*) as count FROM attendance WHERE member_id = %s", (member_id,))
            total_attendance = smt.fetchone()['count']

            # This month
            current_month = datetime.now().month
            current_year = datetime.now().year
            smt.execute("""
                SELECT COUNT(*) as count FROM attendance
                WHERE member_id = %s AND MONTH(attendance_date) = %s AND YEAR(attendance_date) = %s
            """, (member_id, current_month, current_year))
            month_attendance = smt.fetchone()['count']

            # This week
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            smt.execute("""
                SELECT COUNT(*) as count FROM attendance
                WHERE member_id = %s AND attendance_date >= %s
            """, (member_id, week_start))
            week_attendance = smt.fetchone()['count']

            # Streak (consecutive days)
            smt.execute("""
                SELECT attendance_date FROM attendance
                WHERE member_id = %s ORDER BY attendance_date DESC LIMIT 30
            """, (member_id,))
            dates = [row['attendance_date'] for row in smt.fetchall()]

            streak = 0
            if dates:
                check_date = today if dates[0] == today else today - timedelta(days=1)
                for d in dates:
                    if d == check_date:
                        streak += 1
                        check_date = check_date - timedelta(days=1)
                    else:
                        break

            # Metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Visits", total_attendance)
            with col2:
                st.metric("This Month", month_attendance)
            with col3:
                st.metric("This Week", week_attendance)
            with col4:
                st.metric("Day Streak :material/local_fire_department:", streak)

            st.markdown("---")

            # Last 30 days records
            st.subheader(":material/calendar_month: Recent Attendance")
            smt.execute("""
                SELECT attendance_date, check_in_time
                FROM attendance
                WHERE member_id = %s
                ORDER BY attendance_date DESC
                LIMIT 30
            """, (member_id,))
            records = smt.fetchall()

            if records:
                st.dataframe(records, width='stretch', hide_index=True)

                # Attendance calendar-like summary
                st.markdown("---")
                st.subheader(":material/bar_chart: Monthly Overview")

                # This month's attendance percentage
                days_in_month = calendar.monthrange(today.year, today.month)[1]
                attendance_pct = (month_attendance / days_in_month) * 100 if days_in_month > 0 else 0
                st.write(f"**This Month's Attendance Rate:** {attendance_pct:.1f}%")
                st.progress(min(attendance_pct / 100, 1.0))

                if attendance_pct >= 80:
                    st.success(":material/emoji_events: Excellent! You're a gym regular!")
                elif attendance_pct >= 50:
                    st.info(":material/thumb_up: Good consistency! Keep it up!")
                else:
                    st.warning(":material/fitness_center: Try to visit more often to reach your fitness goals!")
            else:
                st.info(":material/inbox: No attendance records yet. Start visiting the gym!")
        except sql.err.ProgrammingError:
            st.info(":material/inbox: Attendance tracking will be available soon")

        db.close()

    except Exception as e:
        st.error(f":material/cancel: Error: {e}")

# ---------------------------------------------------------------

def display_payment_history(member_id):
    st.title(":material/payments: Payment History")
    st.markdown("---")

    try:
        db = get_db()
        smt = db.cursor()

        try:
            smt.execute("""
                SELECT payment_date, amount, payment_mode
                FROM payments
                WHERE member_id = %s
                ORDER BY payment_date DESC
            """, (member_id,))
            payments = smt.fetchall()

            if payments:
                total_amount = sum(p['amount'] for p in payments)
                last_payment = payments[0]

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Payments", len(payments))
                with col2:
                    st.metric("Total Amount", f"₹{total_amount:,.0f}")
                with col3:
                    st.metric("Last Payment", f"₹{last_payment['amount']:,.0f}")

                st.markdown("---")
                st.subheader(":material/assignment: Transaction History")

                # Display with colored payment modes
                for payment in payments:
                    mode = payment['payment_mode']
                    if mode == "Cash":
                        emoji = ":material/payments:"
                    elif mode == "Card":
                        emoji = ":material/credit_card:"
                    elif mode == "UPI":
                        emoji = ":material/smartphone:"
                    else:
                        emoji = ":material/account_balance:"

                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"{emoji} **{payment['payment_date']}**")
                    with col2:
                        st.write(f"₹{payment['amount']:,.0f}")
                    with col3:
                        st.write(f"*{payment['payment_mode']}*")

                st.markdown("---")
                st.dataframe(payments, width='stretch', hide_index=True)
            else:
                st.info(":material/inbox: No payment records found")
        except sql.err.ProgrammingError:
            st.info(":material/inbox: Payment history will be available soon")

        db.close()

    except Exception as e:
        st.error(f":material/cancel: Error: {e}")

# ---------------------------------------------------------------

def fitness_quiz(member_id):
    st.title(":material/emoji_events: Fitness Quiz Challenge")
    st.markdown("---")

    # Quiz questions
    quiz_questions = [
        {
            "question": "How many days per week should you exercise for optimal health?",
            "options": ["1-2 days", "3-5 days", "6-7 days", "Only weekends"],
            "correct": 1,
            "points": 10
        },
        {
            "question": "What is the most important meal of the day for muscle building?",
            "options": ["Dinner", "Lunch", "Breakfast", "Post-workout meal"],
            "correct": 3,
            "points": 10
        },
        {
            "question": "How much water should an average person drink daily?",
            "options": ["1-2 glasses", "4-5 glasses", "8-10 glasses", "15+ glasses"],
            "correct": 2,
            "points": 10
        },
        {
            "question": "Which exercise is best for building chest muscles?",
            "options": ["Squats", "Bench Press", "Deadlifts", "Bicep Curls"],
            "correct": 1,
            "points": 15
        },
        {
            "question": "What does BMI stand for?",
            "options": ["Body Mass Index", "Basic Muscle Indicator", "Body Measurement Index", "Bone Mass Indicator"],
            "correct": 0,
            "points": 5
        },
        {
            "question": "How long should you rest between sets for muscle growth?",
            "options": ["30 seconds", "1-2 minutes", "5 minutes", "10 minutes"],
            "correct": 1,
            "points": 10
        },
        {
            "question": "Which nutrient is most important for muscle repair?",
            "options": ["Carbohydrates", "Fats", "Protein", "Vitamins"],
            "correct": 2,
            "points": 15
        },
        {
            "question": "What is the best time to stretch?",
            "options": ["Before workout", "After workout", "During workout", "Never"],
            "correct": 1,
            "points": 10
        },
        {
            "question": "How many calories are in 1 kg of body fat?",
            "options": ["3500", "5500", "7700", "9000"],
            "correct": 2,
            "points": 15
        },
        {
            "question": "Which exercise is known as the 'King of Exercises'?",
            "options": ["Bench Press", "Deadlift", "Squat", "Pull-up"],
            "correct": 2,
            "points": 10
        }
    ]

    # Initialize quiz state
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False

    # Welcome screen
    if not st.session_state.quiz_started:
        st.markdown("""
        ### :material/emoji_events: Welcome to the Fitness Quiz!

        **Rules:**
        - 10 questions about fitness and health
        - Each correct answer gives you points
        - Earn points to get discounts on membership renewal
        - 100+ points = 10% discount
        - 80-99 points = 5% discount
        - 60-79 points = 2% discount

        **Good luck! :material/fitness_center:**
        """)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(":material/rocket_launch: Start Quiz", width='stretch', type="primary"):
                st.session_state.quiz_started = True
                st.rerun()

    # Quiz in progress
    elif not st.session_state.quiz_completed:
        st.subheader(f"Question {len(st.session_state.quiz_answers) + 1} of {len(quiz_questions)}")

        current_q = quiz_questions[len(st.session_state.quiz_answers)]

        st.markdown(f"### {current_q['question']}")
        st.write(f"*Points: {current_q['points']}*")

        answer = st.radio(
            "Select your answer:",
            current_q['options'],
            key=f"q_{len(st.session_state.quiz_answers)}"
        )

        col1, col2 = st.columns([1, 3])

        with col1:
            if st.button(":material/check_circle: Submit Answer", width='stretch', type="primary"):
                correct_index = current_q['correct']
                selected_index = current_q['options'].index(answer)

                if selected_index == correct_index:
                    st.session_state.quiz_score += current_q['points']
                    st.success(f":material/check_circle: Correct! +{current_q['points']} points")
                else:
                    st.error(f":material/cancel: Wrong! Correct answer: {current_q['options'][correct_index]}")

                st.session_state.quiz_answers[len(st.session_state.quiz_answers)] = answer

                if len(st.session_state.quiz_answers) >= len(quiz_questions):
                    st.session_state.quiz_completed = True

                import time
                time.sleep(1)
                st.rerun()

    # Quiz completed
    else:
        score = st.session_state.quiz_score
        max_score = sum(q['points'] for q in quiz_questions)
        percentage = (score / max_score) * 100

        st.balloons()

        st.markdown(f"""
        ### :material/celebration: Quiz Completed!

        **Your Score:** {score} / {max_score} points
        **Percentage:** {percentage:.1f}%
        """)

        # Progress bar
        st.progress(percentage / 100)

        # Discount calculation
        if score >= 100:
            discount = 10
            emoji = ":material/emoji_events:"
            message = "Amazing! You're a fitness expert!"
        elif score >= 80:
            discount = 5
            emoji = ":material/military_tech:"
            message = "Great job! You know your fitness!"
        elif score >= 60:
            discount = 2
            emoji = ":material/military_tech:"
            message = "Good effort! Keep learning!"
        else:
            discount = 0
            emoji = ":material/fitness_center:"
            message = "Keep studying! Try again to earn discounts!"

        st.markdown(f"""
        ### {emoji} {message}

        **Discount Earned:** {discount}% off on next renewal
        """)

        # Save score to database (once per attempt)
        if st.session_state.get('quiz_saved'):
            st.success(":material/check_circle: Your score has been saved! Show this to the front desk for your discount.")
        else:
            try:
                db = get_db()
                smt = db.cursor()

                smt.execute("""
                    CREATE TABLE IF NOT EXISTS quiz_scores (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        member_id INT,
                        score INT,
                        max_score INT,
                        percentage DECIMAL(5,2),
                        discount INT,
                        quiz_date DATE,
                        FOREIGN KEY (member_id) REFERENCES members(memberid)
                    )
                """)

                smt.execute(
                    "INSERT INTO quiz_scores (member_id, score, max_score, percentage, discount, quiz_date) "
                    "VALUES (%s, %s, %s, %s, %s, CURDATE())",
                    (member_id, score, max_score, round(percentage, 1), discount)
                )
                db.commit()
                db.close()
                st.session_state.quiz_saved = True

                st.success(":material/check_circle: Your score has been saved! Show this to the front desk for your discount.")
            except Exception as e:
                st.error(f"Error saving score: {e}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(":material/sync: Retake Quiz", width='stretch'):
                st.session_state.quiz_started = False
                st.session_state.quiz_answers = {}
                st.session_state.quiz_score = 0
                st.session_state.quiz_completed = False
                st.session_state.quiz_saved = False
                st.rerun()

        with col2:
            st.info(f":material/confirmation_number: Your Discount Code: GYM{discount}OFF-{member_id}")