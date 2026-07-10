import streamlit as st
import base64

# --------------------------------------------------------------Home Function--------------------------------------------------------------------------------------

def Home():
    # Get user role from session state
    user_cookie = st.session_state.user.get("Role", "Team") if "user" in st.session_state else "Team"
    
    # --------------------------------------------------------------Admin Page--------------------------------------------------------------------------------------
    if user_cookie == 'Admin':
        with open("background.jpg", "rb") as f:
            data = base64.b64encode(f.read()).decode()
        
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{data}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        .main .block-container {{
            background: rgba(255,255,255,0.5);
            border-radius: 20px;
            backdrop-filter: blur(20px);
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # ---------------- CUSTOM CSS ---------------- #
        st.markdown("""
        <style>
        /* Main Heading */
        h1{
            color:#ff4500 !important;
            text-align:center;
            font-size:55px !important;
            text-shadow:2px 2px 8px #ffd700;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"]{
            background: linear-gradient(
        180deg,
        #111111,
        #2b0000,
        #b30000
        );
        }
        
        /* Sidebar Text */
        [data-testid="stSidebar"] *{
            color:white;
        }
        
        /* Input Boxes */
        div[data-testid="stTextInput"] input{
            background:white;
            color:black;
            border:2px solid #ff512f;
            border-radius:15px;
        }
        
        /* Selectbox */
        div[data-baseweb="select"]{
            color:black;
        }
        
        /* Buttons */
        .stButton>button{
            background:linear-gradient(45deg,#ff512f,#f09819);
            color:white;
            border:none;
            border-radius:15px;
            height:50px;
            font-size:18px;
            font-weight:bold;
        }
        
        /* Button Hover */
        .stButton>button:hover{
            background:linear-gradient(45deg,#ffd700,#ff512f);
            color:black;
        }
        
        /* Main Container */
        .block-container{
            background:rgba(255,255,255,0.55);
            border-radius:20px;
            padding:20px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # ---------------- HEADER ---------------- #
        col1, col2, col3 = st.columns([1,3,1])
        
        with col1:
            st.image("leftgym.png", use_container_width=True)
        
        with col2:
            st.markdown("""
            <div style = 'display:flex;flex-direction:column;'>
            <h1>💪 TA FITNESS GYM 🏋️‍♂️</h1>
            <div style='text-align:center;
            font-size:22px;
            color:black;
            margin-bottom:25px;'>
            
            🔥 Build Strength • 💪 Stay Fit • 🏆 Transform Yourself 🔥
            
            </div>
            
            <h3 style='text-align:center;color:#6127F5'>
            Welcome to TA Fitness Membership Management System 💪
            </h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.image("rightgym.png", use_container_width=True)
        
        # ================= OFFERS MARQUEE =================
        st.markdown("""
        <marquee behavior="scroll" direction="left" scrollamount="8"
        style="
        background:linear-gradient(90deg,#FFD700,#FFA500);
        color:black;
        padding:12px;
        border-radius:10px;
        font-size:22px;
        font-weight:bold;
        margin-top:10px;
        margin-bottom:20px;
        ">
        
        🔥 SPECIAL FITNESS OFFER 🔥 |
        💪 1 Month Plan = ₹1000 |
        🏋️ 3 Months Plan = ₹2400 (Save ₹600) |
        🏆 6 Months Plan = ₹4200 (Save ₹1800) |
        👑 12 Months Plan = ₹7000 (Save ₹5000) |
        📞 Join Today & Transform Yourself!
        
        </marquee>
        """, unsafe_allow_html=True)
        
        # ================= MEMBERSHIP CARDS =================
        st.markdown("""
        <div style='display:flex;justify-content:space-around;gap:15px;margin-bottom:20px;'>
        
        <div style='background:#FF6B6B;padding:15px;border-radius:15px;width:22%;text-align:center;color:white'>
        <h3>💪 1 Month</h3>
        <h2>₹1000</h2>
        </div>
        
        <div style='background:#4ECDC4;padding:15px;border-radius:15px;width:22%;text-align:center;color:white'>
        <h3>🏋️ 3 Months</h3>
        <h2>₹2400</h2>
        <p>Save ₹600</p>
        </div>
        
        <div style='background:#45B7D1;padding:15px;border-radius:15px;width:22%;text-align:center;color:white'>
        <h3>🏆 6 Months</h3>
        <h2>₹4200</h2>
        <p>Save ₹1800</p>
        </div>
        
        <div style='background:#9B59B6;padding:15px;border-radius:15px;width:22%;text-align:center;color:white'>
        <h3>👑 12 Months</h3>
        <h2>₹7000</h2>
        <p>Save ₹5000</p>
        </div>
        
        </div>
        """, unsafe_allow_html=True)
        
        # ---------------- SIDEBAR ---------------- #
        st.sidebar.image("gym.png", width=150, use_container_width=True)
        
        from admin_functions import admin_dashboard
        admin_dashboard()
        
        # ---------------- FOOTER ---------------- #
        st.markdown("""
        <br><br>
        <hr>
        <center>
        <h4 style='color:dark blue'>
        🏆 TA FITNESS GYM | Strength • Discipline • Results 💪
        </h4>
        </center>
        """, unsafe_allow_html=True)
    
    # --------------------------------------------------------------Member Page--------------------------------------------------------------------------------------
    elif user_cookie == 'Member':
        with open("background.jpg", "rb") as f:
            data = base64.b64encode(f.read()).decode()
        
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{data}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        .main .block-container {{
            background: rgba(255,255,255,0.5);
            border-radius: 20px;
            backdrop-filter: blur(20px);
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # ---------------- CUSTOM CSS ---------------- #
        st.markdown("""
        <style>
        /* Main Heading */
        h1{
            color:#ff4500 !important;
            text-align:center;
            font-size:55px !important;
            text-shadow:2px 2px 8px #ffd700;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"]{
            background: linear-gradient(
        180deg,
        #111111,
        #2b0000,
        #b30000
        );
        }
        
        /* Sidebar Text */
        [data-testid="stSidebar"] *{
            color:white;
        }
        
        /* Input Boxes */
        div[data-testid="stTextInput"] input{
            background:white;
            color:black;
            border:2px solid #ff512f;
            border-radius:15px;
        }
        
        /* Selectbox */
        div[data-baseweb="select"]{
            color:black;
        }
        
        /* Buttons */
        .stButton>button{
            background:linear-gradient(45deg,#ff512f,#f09819);
            color:white;
            border:none;
            border-radius:15px;
            height:50px;
            font-size:18px;
            font-weight:bold;
        }
        
        /* Button Hover */
        .stButton>button:hover{
            background:linear-gradient(45deg,#ffd700,#ff512f);
            color:black;
        }
        
        /* Main Container */
        .block-container{
            background:rgba(255,255,255,0.55);
            border-radius:20px;
            padding:20px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # ---------------- HEADER ---------------- #
        col1, col2, col3 = st.columns([1,3,1])
        
        with col1:
            st.image("leftgym.png", use_container_width=True)
        
        with col2:
            st.markdown("""
            <div style = 'display:flex;flex-direction:column;'>
            <h1>💪 TA FITNESS GYM 🏋️‍♂️</h1>
            <div style='text-align:center;
            font-size:22px;
            color:black;
            margin-bottom:25px;'>
            
            🔥 Build Strength • 💪 Stay Fit • 🏆 Transform Yourself 🔥
            
            </div>
            
            <h3 style='text-align:center;color:#6127F5'>
            Welcome to TA Fitness Membership Management System 💪
            </h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.image("rightgym.png", use_container_width=True)
        
        # ================= OFFERS MARQUEE =================
        st.markdown("""
        <marquee behavior="scroll" direction="left" scrollamount="8"
        style="
        background:linear-gradient(90deg,#FFD700,#FFA500);
        color:black;
        padding:12px;
        border-radius:10px;
        font-size:22px;
        font-weight:bold;
        margin-top:10px;
        margin-bottom:20px;
        ">
        
        🔥 SPECIAL FITNESS OFFER 🔥 |
        💪 1 Month Plan = ₹1000 |
        🏋️ 3 Months Plan = ₹2400 (Save ₹600) |
        🏆 6 Months Plan = ₹4200 (Save ₹1800) |
        👑 12 Months Plan = ₹7000 (Save ₹5000) |
        📞 Join Today & Transform Yourself!
        
        </marquee>
        """, unsafe_allow_html=True)
        
        # ================= MEMBERSHIP CARDS =================
        st.markdown("""
        <div style='display:flex;justify-content:space-around;gap:15px;margin-bottom:20px;'>
        
        <div style='background:#FF6B6B;padding:15px;border-radius:15px;width:22%;text-align:center;color:white'>
        <h3>💪 1 Month</h3>
        <h2>₹1000</h2>
        </div>
        
        <div style='background:#4ECDC4;padding:15px;border-radius:15px;width:22%;text-align:center;color:white'>
        <h3>🏋️ 3 Months</h3>
        <h2>₹2400</h2>
        <p>Save ₹600</p>
        </div>
        
        <div style='background:#45B7D1;padding:15px;border-radius:15px;width:22%;text-align:center;color:white'>
        <h3>🏆 6 Months</h3>
        <h2>₹4200</h2>
        <p>Save ₹1800</p>
        </div>
        
        <div style='background:#9B59B6;padding:15px;border-radius:15px;width:22%;text-align:center;color:white'>
        <h3>👑 12 Months</h3>
        <h2>₹7000</h2>
        <p>Save ₹5000</p>
        </div>
        
        </div>
        """, unsafe_allow_html=True)
        
        # ---------------- SIDEBAR ---------------- #
        st.sidebar.image("gym.png", width=150, use_container_width=True)
        
        from member_functions import member_dashboard
        member_dashboard()
        
        # ---------------- FOOTER ---------------- #
        st.markdown("""
        <br><br>
        <hr>
        <center>
        <h4 style='color:dark blue'>
        🏆 TA FITNESS GYM | Strength • Discipline • Results 💪
        </h4>
        </center>
        """, unsafe_allow_html=True)
    
    # --------------------------------------------------------------Team Page--------------------------------------------------------------------------------------
    else:
        with open("background.jpg", "rb") as f:
            data = base64.b64encode(f.read()).decode()
        
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{data}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        .main .block-container {{
            background: rgba(255,255,255,0.5);
            border-radius: 20px;
            backdrop-filter: blur(20px);
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # ---------------- CUSTOM CSS ---------------- #
        st.markdown("""
        <style>
        /* Main Heading */
        h1{
            color:#ff4500 !important;
            text-align:center;
            font-size:55px !important;
            text-shadow:2px 2px 8px #ffd700;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"]{
            background: linear-gradient(
        180deg,
        #111111,
        #2b0000,
        #b30000
        );
        }
        
        /* Sidebar Text */
        [data-testid="stSidebar"] *{
            color:white;
        }
        
        /* Input Boxes */
        div[data-testid="stTextInput"] input{
            background:white;
            color:black;
            border:2px solid #ff512f;
            border-radius:15px;
        }
        
        /* Selectbox */
        div[data-baseweb="select"]{
            color:black;
        }
        
        /* Buttons */
        .stButton>button{
            background:linear-gradient(45deg,#ff512f,#f09819);
            color:white;
            border:none;
            border-radius:15px;
            height:50px;
            font-size:18px;
            font-weight:bold;
        }
        
        /* Button Hover */
        .stButton>button:hover{
            background:linear-gradient(45deg,#ffd700,#ff512f);
            color:black;
        }
        
        /* Main Container */
        .block-container{
            background:rgba(255,255,255,0.55);
            border-radius:20px;
            padding:20px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # ---------------- HEADER ---------------- #
        col1, col2, col3 = st.columns([1,3,1])
        
        with col1:
            st.image("leftgym.png", use_container_width=True)
        
        with col2:
            st.markdown("""
            <div style = 'display:flex;flex-direction:column;'>
            <h1>💪 TA FITNESS GYM 🏋️‍♂️</h1>
            <div style='text-align:center;
            font-size:22px;
            color:black;
            margin-bottom:25px;'>
            
            🔥 Build Strength • 💪 Stay Fit • 🏆 Transform Yourself 🔥
            
            </div>
            
            <h3 style='text-align:center;color:#6127F5'>
            Welcome to TA Fitness Membership Management System 💪
            </h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.image("rightgym.png", use_container_width=True)
        
        # ================= OFFERS MARQUEE =================
        st.markdown("""
        <marquee behavior="scroll" direction="left" scrollamount="8"
        style="
        background:linear-gradient(90deg,#FFD700,#FFA500);
        color:black;
        padding:12px;
        border-radius:10px;
        font-size:22px;
        font-weight:bold;
        margin-top:10px;
        margin-bottom:20px;
        ">
        
        🔥 SPECIAL FITNESS OFFER 🔥 |
        💪 1 Month Plan = ₹1000 |
        🏋️ 3 Months Plan = ₹2400 (Save ₹600) |
        🏆 6 Months Plan = ₹4200 (Save ₹1800) |
        👑 12 Months Plan = ₹7000 (Save ₹5000) |
        📞 Join Today & Transform Yourself!
        
        </marquee>
        """, unsafe_allow_html=True)
        
        # ================= MEMBERSHIP CARDS =================
        st.markdown("""
        <div style='display:flex;justify-content:space-around;gap:15px;margin-bottom:20px;'>
        
        <div style='background:#FF6B6B;padding:15px;border-radius:15px;width:22%;text-align:center;color:white'>
        <h3>💪 1 Month</h3>
        <h2>₹1000</h2>
        </div>
        
        <div style='background:#4ECDC4;padding:15px;border-radius:15px;width:22%;text-align:center;color:white'>
        <h3>🏋️ 3 Months</h3>
        <h2>₹2400</h2>
        <p>Save ₹600</p>
        </div>
        
        <div style='background:#45B7D1;padding:15px;border-radius:15px;width:22%;text-align:center;color:white'>
        <h3>🏆 6 Months</h3>
        <h2>₹4200</h2>
        <p>Save ₹1800</p>
        </div>
        
        <div style='background:#9B59B6;padding:15px;border-radius:15px;width:22%;text-align:center;color:white'>
        <h3>👑 12 Months</h3>
        <h2>₹7000</h2>
        <p>Save ₹5000</p>
        </div>
        
        </div>
        """, unsafe_allow_html=True)
        
        # ---------------- SIDEBAR ---------------- #
        st.sidebar.image("gym.png", width=150, use_container_width=True)
        
        from team_functions import team_dashboard
        team_dashboard()
        
        # ---------------- FOOTER ---------------- #
        st.markdown("""
        <br><br>
        <hr>
        <center>
        <h4 style='color:dark blue'>
        🏆 TA FITNESS GYM | Strength • Discipline • Results 💪
        </h4>
        </center>
        """, unsafe_allow_html=True)