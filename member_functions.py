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
    st.title("👤 My Profile")
    st.markdown("---")

    try:
        db = get_db()
        smt = db.cursor()

        smt.execute("SELECT * FROM members WHERE memberid = %s", (member_id,))
        member = smt.fetchone()
        db.close()

        if member:
            # Profile Photo Section
            st.markdown("### 📸 Profile Photo")

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
                    st.success("✅ Profile photo updated!")
                    st.rerun()

            st.markdown("---")

            # Personal Information (Read Only + Editable fields)
            st.markdown("### 📋 Personal Information")

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

            if st.button("💾 Save Changes", width='stretch', type="primary"):
                if new_dob.strip() and valid_date(new_dob) is None:
                    st.error("❌ Date of Birth must be a valid date in YYYY-MM-DD format")
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

                    st.success("✅ Profile updated successfully!")
                    import time
                    time.sleep(1)
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error updating profile: {e}")

            st.markdown("---")

            # Membership Details (Read Only)
            st.markdown("### 💪 Membership Information")

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
                st.error(f"⚠️ Membership Expired ({abs(days_left)} days ago)")
            elif days_left <= 7:
                st.warning(f"⚠️ Membership expiring soon ({days_left} days left)")
            else:
                st.success(f"✅ Active Membership ({days_left} days remaining)")

            # Progress bar
            if total_days > 0:
                progress = min(max(elapsed_days / total_days, 0), 1)
                st.progress(progress, text=f"Membership Progress: {int(progress * 100)}%")

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"⏳ Days Elapsed: {elapsed_days}")
                with col2:
                    st.write(f"📅 Days Remaining: {max(days_left, 0)}")
        else:
            st.error("❌ Member record not found")

    except Exception as e:
        st.error(f"❌ Error loading profile: {e}")

# ---------------------------------------------------------------

def display_membership_details(member_id):
    st.title("💪 My Membership")
    st.markdown("---")

    try:
        db = get_db()
        smt = db.cursor()

        smt.execute("SELECT * FROM members WHERE memberid = %s", (member_id,))
        member = smt.fetchone()
        db.close()

        if member:
            st.markdown(f"### 🏋️ Hello, {member['membername']}!")

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
                st.error(f"### 🔴 Membership Expired - {abs(days_left)} days ago")
            elif days_left <= 7:
                st.warning(f"### 🟠 Expiring Soon - {days_left} days remaining")
            elif days_left <= 30:
                st.info(f"### 🔵 Active - {days_left} days remaining")
            else:
                st.success(f"### 🟢 Active - {days_left} days remaining")

            st.markdown("---")

            # Plan Details
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📋 Current Plan")
                st.write(f"**Plan:** {member['membershipplan']}")
                st.write(f"**Start Date:** {start_date}")
                st.write(f"**End Date:** {end_date}")
                st.write(f"**Total Duration:** {total_days} days")

            with col2:
                st.markdown("#### 📊 Progress")
                elapsed_days = (today - start_date).days
                progress_pct = min(max(elapsed_days / total_days * 100, 0), 100) if total_days > 0 else 0
                st.write(f"**Days Completed:** {elapsed_days}")
                st.write(f"**Days Remaining:** {max(days_left, 0)}")
                st.write(f"**Progress:** {progress_pct:.1f}%")

            st.markdown("---")

            # Plan Benefits
            st.markdown("#### 🎁 Your Plan Benefits")

            plan = member['membershipplan']
            if plan == '1 Month':
                benefits = {
                    "🏋️ Gym Access": "Basic gym floor access",
                    "🔐 Locker": "Daily locker facility",
                    "👨‍🏫 Training": "1 Personal training session",
                    "⏰ Timing": "6 AM - 10 PM",
                    "📅 Validity": "30 days"
                }
                color = "#FF6B6B"
            elif plan == '3 Months':
                benefits = {
                    "🏋️ Gym Access": "Full gym floor access",
                    "🔐 Locker": "Permanent locker",
                    "👨‍🏫 Training": "3 Personal training sessions",
                    "🥗 Diet Plan": "Basic diet consultation",
                    "⏰ Timing": "5 AM - 11 PM",
                    "📅 Validity": "90 days"
                }
                color = "#4ECDC4"
            elif plan == '6 Months':
                benefits = {
                    "🏋️ Gym Access": "Full premium access",
                    "🔐 Locker": "Premium locker",
                    "👨‍🏫 Training": "6 Personal training sessions",
                    "🥗 Diet Plan": "Customized diet plan",
                    "💊 Supplements": "Free supplements sample",
                    "⏰ Timing": "24/7 Access",
                    "📅 Validity": "180 days"
                }
                color = "#45B7D1"
            else:  # 12 Months
                benefits = {
                    "🏋️ Gym Access": "VIP all access",
                    "🔐 Locker": "VIP locker",
                    "👨‍🏫 Training": "12 Personal training sessions",
                    "🥗 Diet Plan": "Premium diet plan",
                    "💊 Supplements": "Monthly supplements kit",
                    "💆 Spa": "Free spa access",
                    "🚗 Parking": "Free valet parking",
                    "⏰ Timing": "24/7 Access",
                    "📅 Validity": "365 days"
                }
                color = "#9B59B6"

            # Display benefits in cards
            cols = st.columns(2)
            for i, (benefit, description) in enumerate(benefits.items()):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div style='background: {color}; padding: 15px; border-radius: 10px; margin-bottom: 10px; color: white;'>
                        <strong>{benefit}</strong><br>
                        <small>{description}</small>
                    </div>
                    """, unsafe_allow_html=True)

            # Renewal Call-to-Action
            if days_left <= 15:
                st.markdown("---")
                st.warning("🔄 Your membership is expiring soon! Contact the front desk to renew.")
                if st.button("📞 Request Renewal Callback", width='stretch'):
                    st.success("✅ Renewal request submitted! Team will contact you shortly.")

        else:
            st.error("❌ Member record not found")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ---------------------------------------------------------------

def display_attendance(member_id):
    st.title("📊 My Attendance")
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
                st.metric("Day Streak 🔥", streak)

            st.markdown("---")

            # Last 30 days records
            st.subheader("📅 Recent Attendance")
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
                st.subheader("📊 Monthly Overview")

                # This month's attendance percentage
                days_in_month = calendar.monthrange(today.year, today.month)[1]
                attendance_pct = (month_attendance / days_in_month) * 100 if days_in_month > 0 else 0
                st.write(f"**This Month's Attendance Rate:** {attendance_pct:.1f}%")
                st.progress(min(attendance_pct / 100, 1.0))

                if attendance_pct >= 80:
                    st.success("🏆 Excellent! You're a gym regular!")
                elif attendance_pct >= 50:
                    st.info("👍 Good consistency! Keep it up!")
                else:
                    st.warning("💪 Try to visit more often to reach your fitness goals!")
            else:
                st.info("📭 No attendance records yet. Start visiting the gym!")
        except sql.err.ProgrammingError:
            st.info("📭 Attendance tracking will be available soon")

        db.close()

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ---------------------------------------------------------------

def display_payment_history(member_id):
    st.title("💰 Payment History")
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
                st.subheader("📋 Transaction History")

                # Display with colored payment modes
                for payment in payments:
                    mode = payment['payment_mode']
                    if mode == "Cash":
                        emoji = "💵"
                    elif mode == "Card":
                        emoji = "💳"
                    elif mode == "UPI":
                        emoji = "📱"
                    else:
                        emoji = "🏦"

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
                st.info("📭 No payment records found")
        except sql.err.ProgrammingError:
            st.info("📭 Payment history will be available soon")

        db.close()

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ---------------------------------------------------------------

def fitness_quiz(member_id):
    st.title("🏆 Fitness Quiz Challenge")
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
        ### 🏆 Welcome to the Fitness Quiz!

        **Rules:**
        - 10 questions about fitness and health
        - Each correct answer gives you points
        - Earn points to get discounts on membership renewal
        - 100+ points = 10% discount
        - 80-99 points = 5% discount
        - 60-79 points = 2% discount

        **Good luck! 💪**
        """)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Quiz", width='stretch', type="primary"):
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
            if st.button("✅ Submit Answer", width='stretch', type="primary"):
                correct_index = current_q['correct']
                selected_index = current_q['options'].index(answer)

                if selected_index == correct_index:
                    st.session_state.quiz_score += current_q['points']
                    st.success(f"✅ Correct! +{current_q['points']} points")
                else:
                    st.error(f"❌ Wrong! Correct answer: {current_q['options'][correct_index]}")

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
        ### 🎉 Quiz Completed!

        **Your Score:** {score} / {max_score} points
        **Percentage:** {percentage:.1f}%
        """)

        # Progress bar
        st.progress(percentage / 100)

        # Discount calculation
        if score >= 100:
            discount = 10
            emoji = "🏆"
            message = "Amazing! You're a fitness expert!"
        elif score >= 80:
            discount = 5
            emoji = "🥈"
            message = "Great job! You know your fitness!"
        elif score >= 60:
            discount = 2
            emoji = "🥉"
            message = "Good effort! Keep learning!"
        else:
            discount = 0
            emoji = "💪"
            message = "Keep studying! Try again to earn discounts!"

        st.markdown(f"""
        ### {emoji} {message}

        **Discount Earned:** {discount}% off on next renewal
        """)

        # Save score to database (once per attempt)
        if st.session_state.get('quiz_saved'):
            st.success("✅ Your score has been saved! Show this to the front desk for your discount.")
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

                st.success("✅ Your score has been saved! Show this to the front desk for your discount.")
            except Exception as e:
                st.error(f"Error saving score: {e}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Retake Quiz", width='stretch'):
                st.session_state.quiz_started = False
                st.session_state.quiz_answers = {}
                st.session_state.quiz_score = 0
                st.session_state.quiz_completed = False
                st.session_state.quiz_saved = False
                st.rerun()

        with col2:
            st.info(f"🎫 Your Discount Code: GYM{discount}OFF-{member_id}")