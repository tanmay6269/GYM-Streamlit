# TA Fitness Gym - Membership Management System

A complete gym membership management system with role-based access for Admin, Team, and Members.

## Features

### Admin
- Add, Edit, Delete members
- Add and Edit staff accounts
- View analytics dashboard with charts
- Membership renewal
- Payment management
- View reports (Dashboard, Membership, Revenue, Attendance, Expiring)

### Team
- Search members
- Edit member details
- Mark attendance
- Renew memberships

### Member
- View and edit profile with photo upload
- View membership details and benefits
- View attendance history
- View payment history
- Take fitness quiz to earn discount points

## Tech Stack

- Python 3.10+
- Streamlit
- MySQL
- Plotly (for charts)

## Installation

### 1. Clone the repository-----------------------------
```bash
git clone https://github.com/yourusername/TA_Fitness_Gym.git
cd TA_Fitness_Gym

2. Install dependencies---------------------------------
bash
pip install -r requirements.txt

3. Setup MySQL Database---------------------------------
Create database and tables:

sql
CREATE DATABASE TA_fitness;
USE TA_fitness;

-- Members table
CREATE TABLE members (
    memberid INT PRIMARY KEY,
    membername VARCHAR(100),
    dob VARCHAR(20),
    gender VARCHAR(10),
    address VARCHAR(255),
    membershipstart DATE,
    membershipend DATE,
    membershipplan VARCHAR(20),
    mobilenumber VARCHAR(15),
    Password VARCHAR(50)
);

-- User login table
CREATE TABLE user_login (
    User_id INT PRIMARY KEY,
    User_Name VARCHAR(100),
    Password VARCHAR(50),
    Role VARCHAR(20),
    Email VARCHAR(100),
    Phone VARCHAR(15)
);

-- Attendance table
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    attendance_date DATE,
    check_in_time TIME,
    marked_by VARCHAR(100),
    FOREIGN KEY (member_id) REFERENCES members(memberid)
);

-- Payments table
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    amount DECIMAL(10,2),
    payment_date DATE,
    payment_mode VARCHAR(50),
    recorded_by VARCHAR(100),
    FOREIGN KEY (member_id) REFERENCES members(memberid)
);

-- Quiz scores table
CREATE TABLE quiz_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    score INT,
    max_score INT,
    percentage DECIMAL(5,2),
    discount INT,
    quiz_date DATE,
    FOREIGN KEY (member_id) REFERENCES members(memberid)
);

-- Add default users
INSERT INTO user_login VALUES (1, 'Admin', 'admin123', 'Admin', 'admin@tafitness.com', '9876543210');
INSERT INTO user_login VALUES (2, 'Team', 'team123', 'Team', 'team@tafitness.com', '9876543211');

4. Update database credentials-------------------------------
In all Python files, update the database connection:

python
db = sql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='your_password',  # Change this
    database='TA_fitness'
)

5. Create profile photos folder--------------------------------
bash
mkdir profile_photos

6. Run the application-----------------------------------------
bash
streamlit run app.py
Default Login Credentials
Role	User ID	Password
Admin	1	admin123
Team	2	team123
Member	(create in system)	(set during creation)
Project Structure
text
TA_Fitness_Gym/
├── app.py                 # Main application
├── login.py               # Login system
├── GYM.py                 # Layout and routing
├── admin_functions.py     # Admin dashboard
├── team_functions.py      # Team dashboard
├── member_functions.py    # Member dashboard
├── code1.py               # Insert member
├── code2.py               # Display all members
├── code3.py               # Search member
├── code4.py               # Edit member
├── code5.py               # Delete member
├── background.jpg         # Background image
├── gym.png                # Gym logo
├── leftgym.png            # Left header image
├── rightgym.png           # Right header image
├── profile_photos/        # Member photos folder
├── requirements.txt       # Dependencies
└── README.md              # This file
Requirements
text
streamlit
streamlit-option-menu
streamlit-cookies-manager
pymysql
python-dateutil
pandas
plotly
Pillow
Membership Plans
Plan	Price	Duration
1 Month	₹1,000	30 days
3 Months	₹2,400	90 days (Save ₹600)
6 Months	₹4,200	180 days (Save ₹1,800)
12 Months	₹7,000	365 days (Save ₹5,000)
Fitness Quiz Rewards
Score	Discount
100+ points	10% off
80-99 points	5% off
60-79 points	2% off
Screenshots
Login screen with role selection

Admin dashboard with analytics charts

Member profile with photo upload

Attendance marking system

Membership renewal with auto-calculated dates

Payment history tracking

Fitness quiz with discount rewards

text

---
