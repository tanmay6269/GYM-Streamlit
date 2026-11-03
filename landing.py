"""Public pages shown before login: Home, Store and Arnold, the fitness companion.

Nothing here reads member data. Only the plan prices, the product catalogue and the
public star reviews are shown. Icons are Material Symbols (the icon font Streamlit
already ships), written as <span class="ms">name</span>.
"""
import html
import re
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

import advisor
import gemini

BASE_DIR = Path(__file__).parent

# product catalogue (generic names; the store only lists products, it takes no orders)
PRODUCTS = [
    ("Supplements", "nutrition", "Whey Protein Blend, 1 kg", "Powder for shakes, chocolate flavour.", 2199),
    ("Supplements", "science", "Creatine Monohydrate, 250 g", "Unflavoured powder, 83 servings.", 899),
    ("Supplements", "sports_bar", "BCAA Drink Mix, 300 g", "Fruit-flavoured drink mix.", 1099),
    ("Supplements", "medication", "Daily Multivitamin, 60 tablets", "One tablet a day.", 549),
    ("Equipment", "fitness_center", "Adjustable Dumbbell Pair, 10 kg", "Two dumbbells with plates and collars.", 1999),
    ("Equipment", "sports_gymnastics", "Skipping Rope", "Speed rope with ball bearings.", 249),
    ("Equipment", "cable", "Resistance Band Set", "Five bands of different strength.", 499),
    ("Equipment", "self_improvement", "Yoga Mat, 6 mm", "Non-slip mat for floor work.", 699),
    ("Accessories", "back_hand", "Lifting Gloves", "Padded palm, wrist wrap.", 449),
    ("Accessories", "local_drink", "Shaker Bottle, 700 ml", "Leak-proof lid with mixing ball.", 299),
    ("Accessories", "backpack", "Gym Duffel Bag", "Main compartment and shoe pocket.", 799),
    ("Accessories", "health_and_safety", "Weight Lifting Belt", "Support belt for heavy lifts.", 899),
]
CATEGORY_STYLE = {  # gradient for the icon tile, icon for the tab
    "Supplements": ("linear-gradient(135deg,#ff512f,#f09819)", "nutrition"),
    "Equipment": ("linear-gradient(135deg,#0abde3,#2e86de)", "fitness_center"),
    "Accessories": ("linear-gradient(135deg,#10ac84,#1dd1a1)", "backpack"),
}

FEATURES = [
    ("group", "Three logins", "Separate logins for the owner, the trainer and team, and the members."),
    ("event_repeat", "Automatic dates", "Plan end dates and renewal amounts are worked out for you."),
    ("fact_check", "Daily attendance", "The front desk marks attendance in seconds."),
    ("monitoring", "Owner reports", "Active members, revenue and plans about to expire at a glance."),
    ("emoji_events", "Fitness quiz", "Members can take the quiz and earn a discount on renewal."),
    ("lock", "Secure by design", "Hashed passwords, checked inputs and a login lockout."),
]

STEPS = [("1", "Pick a plan", "Choose 1, 3, 6 or 12 months. Longer plans cost less per month."),
         ("2", "Log in", "Use the user ID from your gym team to open your own Admin, Team or Member page."),
         ("3", "Stay on track", "Members follow their plan and progress. The gym team handles renewals and attendance.")]

QUICK_QUESTIONS = [
    ("payments", "Which plan is best value?"),
    ("flag", "I am a beginner, where do I start?"),
    ("healing", "My muscles are sore"),
    ("nutrition", "Do I need protein?"),
    ("monitor_heart", "I have high blood pressure"),
    ("water_drop", "How much water should I drink?"),
]


def ic(name, size=22, color="currentColor"):
    """Inline Material Symbols icon."""
    return f"<span class='ms' style='font-size:{size}px;color:{color}'>{name}</span>"


def _css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"], [data-testid="stHeader"], [data-testid="stToolbar"]{display:none !important;}
[data-testid="stMainBlockContainer"], .main .block-container, .block-container{padding-top:.4rem !important;padding-bottom:1.5rem !important;max-width:1250px;background:rgba(255,255,255,.62) !important;}
[data-testid="stAppViewContainer"] > .main{padding-top:0 !important;}
.st-key-topbar{margin-top:6px !important;}
/* the theme CSS blocks are invisible but each one still takes a gap: hide those empty slots */
[data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] style){display:none !important;}
/* the cookie component is an invisible iframe: take it out of the flow but keep it running */
[data-testid="stElementContainer"]:has(iframe[title^="streamlit_cookies_manager"]){position:absolute !important;width:0 !important;height:0 !important;overflow:hidden !important;margin:0 !important;}
.pub, .pub *{font-family:'Poppins','Segoe UI',sans-serif;}
.pub .ms, .ms{font-family:'Material Symbols Rounded' !important;font-weight:normal;font-style:normal;line-height:1;
  display:inline-block;vertical-align:middle;letter-spacing:normal;text-transform:none;white-space:nowrap;
  font-feature-settings:'liga';-webkit-font-feature-settings:'liga';-webkit-font-smoothing:antialiased;}
/* ticker */
.pub-ticker{background:#111;color:#fff;border-radius:12px;padding:9px 0;font-size:15px;font-weight:600;border-bottom:3px solid #ff4500;}
.pub-ticker b{color:#ffb703;}
/* top bar */
.st-key-topbar{background:rgba(255,255,255,.92);border-radius:16px;padding:8px 16px;margin:10px 0 12px 0;box-shadow:0 4px 18px rgba(0,0,0,.12);}
.pub-brand{font-size:26px;font-weight:800;color:#ff4500;line-height:1.1;letter-spacing:.5px;}
.pub-brand small{display:block;font-size:12px;font-weight:600;color:#475569;letter-spacing:.3px;}
.st-key-topbar a[data-testid="stPageLink-NavLink"]{border-radius:999px;font-weight:600;}
.st-key-topbar a[data-testid="stPageLink-NavLink"]:hover{background:#fff1e8;}
/* hero */
.st-key-hero{background:radial-gradient(circle at 20% 0%,#7a1c0a 0%,#2b0000 45%,#0d0d0d 100%);border-radius:24px;padding:26px 26px;margin:6px 0 18px 0;box-shadow:0 10px 34px rgba(0,0,0,.35);border:1px solid #ff4500;}
.st-key-hero img{border-radius:20px;border:3px solid #ff4500;box-shadow:0 0 28px rgba(255,69,0,.55);}
.pub-hero-text{text-align:center;color:#fff;}
.pub-hero-text .tag{display:inline-block;background:#ff4500;color:#fff;border-radius:999px;padding:5px 16px;font-size:12px;font-weight:700;letter-spacing:1.5px;}
.pub-hero-text h2{margin:14px 0 10px 0;font-size:46px;line-height:1.12;font-weight:800;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.6);}
.pub-hero-text h2 span{color:#ffb703;}
.pub-hero-text p{margin:0 auto 16px auto;font-size:17px;opacity:.92;max-width:640px;line-height:1.6;}
.pub-stats{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin:8px 0 16px 0;}
.pub-stat{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.25);border-radius:14px;padding:8px 18px;color:#fff;}
.pub-stat b{display:block;font-size:22px;color:#ffb703;}
.pub-stat span{font-size:12px;opacity:.85;}
.st-key-hero .stButton>button{height:52px;font-size:17px;border-radius:14px;box-shadow:0 4px 14px rgba(255,69,0,.5);}
.st-key-hero a[data-testid="stPageLink-NavLink"]{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.4);border-radius:14px;height:52px;justify-content:center;}
.st-key-hero a[data-testid="stPageLink-NavLink"] *{color:#fff !important;font-weight:700;}
/* section titles */
.pub-title{font-size:30px;font-weight:800;color:#111;margin:26px 0 4px 0;}
.pub-title:after{content:"";display:block;width:64px;height:5px;border-radius:99px;background:linear-gradient(90deg,#ff4500,#ffb703);margin-top:6px;}
.pub-sub{color:#475569;margin:0 0 14px 0;font-size:15px;}
.pub-page-title{display:flex;align-items:center;justify-content:center;gap:12px;font-size:40px;font-weight:800;color:#ff4500;text-shadow:2px 2px 8px #ffd700;margin:6px 0 12px 0;}
/* plan cards */
.pub-plan{position:relative;border-radius:20px;padding:22px 16px 18px 16px;text-align:center;color:#fff;box-shadow:0 8px 22px rgba(0,0,0,.2);transition:transform .2s;}
.pub-plan:hover{transform:translateY(-6px);}
.pub-plan h3{margin:0;color:#fff;font-size:20px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:8px;}
.pub-plan .amt{font-size:38px;font-weight:800;margin:6px 0 2px 0;}
.pub-plan .per{font-size:13px;opacity:.92;}
.pub-plan .save{display:inline-block;margin-top:8px;background:rgba(0,0,0,.25);border-radius:999px;padding:3px 12px;font-size:12px;font-weight:700;}
.pub-ribbon{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:#ffb703;color:#111;font-size:11px;font-weight:800;letter-spacing:1px;border-radius:999px;padding:4px 14px;box-shadow:0 3px 8px rgba(0,0,0,.3);}
/* feature + product cards */
.pub-card{min-height:150px;background:#fff;border:1px solid #f1f5f9;border-radius:18px;padding:18px;height:100%;box-shadow:0 4px 16px rgba(0,0,0,.08);color:#1f2937;transition:transform .2s,box-shadow .2s;}
.pub-card:hover{transform:translateY(-5px);box-shadow:0 12px 28px rgba(255,69,0,.22);border-color:#ffd6c2;}
.pub-card .ico{width:56px;height:56px;border-radius:16px;background:linear-gradient(135deg,#ff512f,#f09819);display:flex;align-items:center;justify-content:center;color:#fff;box-shadow:0 4px 12px rgba(255,81,47,.4);}
.pub-card h4{margin:12px 0 4px 0;color:#111;font-size:17px;font-weight:700;}
.pub-card p{margin:0;font-size:14px;color:#4b5563;line-height:1.55;}
.pub-price{font-size:22px;font-weight:800;color:#ff4500;margin-top:10px;}
.pub-tag{display:inline-block;font-size:10px;font-weight:700;letter-spacing:1px;color:#9a3412;background:#ffedd5;border-radius:999px;padding:2px 10px;margin-top:10px;}
.pub-cat{font-size:11px;font-weight:700;letter-spacing:1px;color:#64748b;text-transform:uppercase;margin-top:12px;}
.pub-prod{min-height:318px;}
/* steps and call-to-action */
.pub-step{background:#fff;border-radius:18px;padding:18px;text-align:center;box-shadow:0 4px 16px rgba(0,0,0,.08);height:100%;}
.pub-step .n{width:42px;height:42px;border-radius:50%;background:#111;color:#ffb703;font-weight:800;font-size:20px;display:flex;align-items:center;justify-content:center;margin:0 auto 8px auto;}
.pub-step h4{margin:4px 0;font-size:17px;color:#111;} .pub-step p{margin:0;font-size:14px;color:#4b5563;}
.pub-cta{background:linear-gradient(135deg,#ff512f,#f09819);border-radius:22px;padding:28px;text-align:center;color:#fff;margin:26px 0 10px 0;box-shadow:0 8px 24px rgba(255,81,47,.4);}
.pub-cta h3{margin:0 0 6px 0;color:#fff;font-size:28px;font-weight:800;} .pub-cta p{margin:0;font-size:16px;opacity:.95;}
.pub-note{display:flex;gap:10px;align-items:flex-start;border:1px solid #fed7aa;background:rgba(255,247,237,.95);border-radius:12px;padding:10px 14px;font-size:13px;color:#7c2d12;margin:10px 0;}
/* AI helper */
.bot-head{display:flex;align-items:center;gap:14px;background:linear-gradient(135deg,#111,#7a1c0a 70%,#ff4500);border-radius:18px;padding:16px 20px;color:#fff;margin-bottom:12px;box-shadow:0 6px 20px rgba(0,0,0,.25);}
.bot-av{width:54px;height:54px;border-radius:50%;background:linear-gradient(135deg,#ff512f,#f09819);display:flex;align-items:center;justify-content:center;border:3px solid #fff;color:#fff;}
.bot-head b{font-size:20px;display:block;line-height:1.2;} .bot-head span.s{font-size:13px;opacity:.9;}
.bot-dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:#22c55e;margin-right:6px;box-shadow:0 0 8px #22c55e;}
.bot-pill{margin-left:auto;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);border-radius:999px;padding:4px 12px;font-size:12px;}
.st-key-chatbox [data-testid="stChatMessage"]{background:#fff;border:1px solid #f1f5f9;border-radius:18px;box-shadow:0 3px 12px rgba(0,0,0,.07);padding:12px 16px;margin-bottom:10px;}
.st-key-chatbox [data-testid="stChatMessage"] p, .st-key-chatbox [data-testid="stChatMessage"] li{color:#1f2937;}
.side-card{background:#fff;border-radius:18px;padding:16px;box-shadow:0 3px 12px rgba(0,0,0,.07);margin-bottom:12px;color:#1f2937;}
.side-card h5{margin:0 0 6px 0;font-size:15px;color:#111;display:flex;align-items:center;gap:8px;} .side-card p{margin:0;font-size:13px;color:#475569;line-height:1.5;}
.res{display:flex;gap:14px;align-items:flex-start;border-radius:16px;padding:16px 18px;margin:10px 0;}
.res.ok{background:#ecfdf5;border:1px solid #6ee7b7;color:#065f46;} .res.warn{background:#fff7ed;border:1px solid #fdba74;color:#9a3412;}
.res b{font-size:17px;display:block;margin-bottom:4px;} .res ul{margin:6px 0 0 18px;padding:0;}
.qrow{display:flex;gap:10px;align-items:flex-start;padding:6px 0;}
.tool-head{display:flex;align-items:center;gap:14px;background:linear-gradient(135deg,#111,#7a1c0a 70%,#ff4500);color:#fff;border-radius:18px;padding:16px 20px;margin:4px 0 14px 0;box-shadow:0 6px 20px rgba(0,0,0,.25);}
.tool-head b{font-size:20px;display:block;line-height:1.2;} .tool-head span{font-size:13px;opacity:.9;}
.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:12px 0;}
.metric{background:#fff;border-radius:18px;padding:16px;box-shadow:0 3px 12px rgba(0,0,0,.08);border-top:5px solid #ff4500;color:#1f2937;}
.metric .k{display:flex;align-items:center;gap:6px;font-size:13px;color:#64748b;font-weight:600;}
.metric b{display:block;font-size:30px;color:#111;margin:6px 0 4px 0;line-height:1.1;}
.metric .note{display:block;font-size:12px;color:#64748b;} .metric .badge{display:inline-block;color:#fff;font-size:12px;font-weight:700;border-radius:999px;padding:3px 12px;}
.bmi-bar{position:relative;display:flex;height:16px;border-radius:99px;overflow:hidden;margin:12px 0 4px 0;}
.bmi-bar i{display:block;height:100%;} .bmi-bar .mark{position:absolute;top:-3px;width:6px;height:22px;background:#111;border:2px solid #fff;border-radius:4px;transform:translateX(-50%);}
.bmi-scale{position:relative;height:16px;font-size:11px;color:#64748b;margin-bottom:8px;}
.bmi-scale span{position:absolute;transform:translateX(-50%);}
.bmi-scale span:first-child{transform:none;} .bmi-scale span:last-child{transform:translateX(-100%);}
.qrow{display:flex;gap:12px;align-items:center;font-size:15px;color:#1f2937;} .qn{flex:0 0 30px;height:30px;border-radius:50%;background:#111;color:#ffb703;font-weight:800;display:flex;align-items:center;justify-content:center;}
.wk{display:flex;gap:12px;align-items:center;padding:8px 0;border-bottom:1px solid #f1f5f9;font-size:14px;color:#334155;} .wk .d{flex:0 0 48px;font-weight:800;color:#ff4500;}
@media (max-width:900px){.metric-grid{grid-template-columns:repeat(2,1fr);}}
/* Arnold chat card */
.st-key-arnold{background:#fff;border:1px solid #f1f5f9;border-radius:26px;box-shadow:0 10px 34px rgba(0,0,0,.14);padding:0 0 14px 0;overflow:hidden;max-width:980px;margin:6px auto 14px auto;}
.ar-head{position:relative;text-align:center;padding:22px 20px 14px 20px;background:linear-gradient(180deg,#fff3ea,#ffffff);border-bottom:1px solid #f1f5f9;}
.ar-name{font-size:34px;font-weight:800;color:#111;display:flex;align-items:center;justify-content:center;gap:8px;line-height:1.15;}
.ar-sub{color:#64748b;font-size:14px;margin-top:2px;}
.ar-online{position:absolute;right:20px;top:18px;display:inline-flex;align-items:center;gap:6px;border:1px solid #e2e8f0;border-radius:999px;padding:4px 12px;font-size:12px;font-weight:600;color:#334155;background:#fff;}
.ar-online i{width:8px;height:8px;border-radius:50%;background:#22c55e;display:inline-block;}
.st-key-arnold_body{padding:6px 24px 0 24px;}
.ar-h{font-size:16px;font-weight:600;color:#111;margin:18px 0 8px 0;} .ar-p{color:#64748b;font-size:14px;margin-bottom:6px;}
.ar-disc{text-align:center;color:#94a3b8;font-size:11px;padding:6px 26px 0 26px;}
.st-key-cta_health{padding:0 24px;margin-top:14px;}
.st-key-cta_health button{background:linear-gradient(90deg,#ffe9dc,#fff4ec) !important;color:#9a3412 !important;border:1px solid #fdba74 !important;border-radius:16px !important;height:56px !important;font-size:17px !important;justify-content:flex-start !important;padding-left:18px !important;box-shadow:none !important;}
.st-key-cta_health button:hover{background:#ffd9c2 !important;color:#7c2d12 !important;}
[class*="st-key-chip_"] button{background:#fff7f0 !important;color:#9a3412 !important;border:1px solid #fed7aa !important;border-radius:999px !important;height:auto !important;min-height:42px;font-size:14px !important;font-weight:600 !important;padding:6px 14px !important;box-shadow:none !important;}
[class*="st-key-chip_"] button:hover{background:#ffe4d2 !important;border-color:#fb923c !important;color:#7c2d12 !important;}
.st-key-new_chat button{height:38px !important;font-size:14px !important;}
.st-key-arnold [data-testid="stChatInput"]{border-radius:999px;border:1px solid #fdba74;margin:10px 24px 0 24px;width:calc(100% - 48px);}
.st-key-arnold [data-testid="stChatMessage"]{background:#fff7f0;border:1px solid #ffedd5;border-radius:18px;padding:12px 16px;margin-bottom:10px;}
.st-key-arnold [data-testid="stChatMessage"] p, .st-key-arnold [data-testid="stChatMessage"] li{color:#1f2937;}
.st-key-helper_view{max-width:980px;margin:0 auto;}
.sc-badges{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:2px 0 10px 0;}
.sc-badges span{display:inline-flex;align-items:center;gap:6px;background:#fff7f0;border:1px solid #fed7aa;color:#9a3412;border-radius:999px;padding:5px 12px;font-size:13px;font-weight:600;}
.sc-group{display:flex;align-items:center;gap:8px;font-size:16px;font-weight:700;color:#111;margin:16px 0 6px 0;padding-bottom:4px;border-bottom:2px solid #ffedd5;}
.nx-h{display:flex;align-items:center;gap:8px;font-size:18px;font-weight:700;color:#111;margin:18px 0 8px 0;}
.nx-card{background:#fff;border-left:5px solid #f97316;border-radius:14px;padding:12px 16px;margin-bottom:10px;box-shadow:0 2px 10px rgba(0,0,0,.06);color:#334155;font-size:14px;line-height:1.55;}
.nx-card .q{font-weight:700;color:#111;margin-bottom:4px;}
.nx-box{background:#fff;border-radius:18px;padding:6px 18px 12px 18px;box-shadow:0 3px 12px rgba(0,0,0,.07);color:#334155;font-size:14px;height:100%;}
.nx-box ol, .nx-box ul, .nx-red ul{margin:4px 0 8px 20px;padding:0;line-height:1.6;} .nx-box p{margin:6px 0 0 0;font-size:12px;color:#64748b;}
.nx-ok{display:flex;align-items:center;gap:6px;font-weight:700;color:#059669;margin-top:6px;} .nx-no{display:flex;align-items:center;gap:6px;font-weight:700;color:#dc2626;margin-top:6px;}
.nx-red{background:#fef2f2;border:1px solid #fca5a5;border-radius:18px;padding:4px 18px 10px 18px;margin-top:14px;color:#7f1d1d;font-size:14px;}
/* every Ask Arnold section is the same white card with the same header */
[class*="st-key-tool_"]{background:#fff;border:1px solid #f1f5f9;border-radius:26px;box-shadow:0 10px 34px rgba(0,0,0,.14);padding:0 24px 18px 24px;overflow:hidden;max-width:980px;margin:6px auto 14px auto;}
[class*="st-key-tool_"] .ar-head{margin:0 -24px 14px -24px;}
.st-key-arnold .ar-p{color:#475569;}
[data-testid="stFormSubmitButton"] button, [data-testid="stDownloadButton"] button{background:linear-gradient(45deg,#ff512f,#f09819) !important;color:#fff !important;border:none !important;border-radius:14px !important;min-height:46px;font-weight:700 !important;box-shadow:0 4px 12px rgba(255,81,47,.3);}
[data-testid="stFormSubmitButton"] button:hover, [data-testid="stDownloadButton"] button:hover{background:linear-gradient(45deg,#ffd700,#ff512f) !important;color:#111 !important;}
.st-key-arnold [data-testid="stExpander"]{border-radius:16px;border:1px solid #fed7aa;background:#fffaf5;}
@media (max-width:640px){
  .ar-online{position:static;display:inline-flex;margin-bottom:6px;}
  .ar-name{font-size:26px;} .ar-head{padding:16px 12px 12px 12px;}
  .st-key-arnold_body{padding:6px 12px 0 12px;}
  .st-key-arnold [data-testid="stChatInput"]{margin:10px 12px 0 12px;width:calc(100% - 24px);}
  .st-key-cta_health{padding:0;}
  [class*="st-key-tool_"]{padding:0 12px 14px 12px;border-radius:20px;}
  [class*="st-key-tool_"] .ar-head{margin:0 -12px 12px -12px;}
  .metric b{font-size:24px;} .plan-big .amt{font-size:36px;}
}
.plan-big{border-radius:22px;padding:24px;color:#fff;background:linear-gradient(135deg,#ff512f,#f09819);box-shadow:0 8px 24px rgba(255,81,47,.4);text-align:center;margin-top:10px;}
.plan-big h3{margin:0;color:#fff;font-size:26px;font-weight:800;} .plan-big .amt{font-size:44px;font-weight:800;margin:4px 0;}
</style>
""", unsafe_allow_html=True)


def _open_login(role="Admin"):
    """Open the login box. role is the option that starts selected (the demo uses Member)."""
    from login import login
    login(role)


def _top(active):
    """Offer ticker, logo, page links and the Login button."""
    from GYM import apply_theme
    apply_theme()
    _css()
    if st.session_state.pop("_expired", False):
        st.warning("Session expired. Please login again.", icon=":material/timer:")
    st.markdown(f"""
<div class="pub pub-ticker"><marquee behavior="scroll" direction="left" scrollamount="7">
{ic('local_fire_department', 20, '#ffb703')} <b>SPECIAL FITNESS OFFER</b> &nbsp;|&nbsp; 1 Month = ₹1000 &nbsp;|&nbsp;
3 Months = ₹2400 (Save ₹600) &nbsp;|&nbsp; 6 Months = ₹4200 (Save ₹1800) &nbsp;|&nbsp;
12 Months = ₹7000 (Save ₹5000) &nbsp;|&nbsp; {ic('smart_toy', 20, '#ffb703')} Ask Arnold, our fitness companion
&nbsp;|&nbsp; {ic('star', 20, '#ffb703')} Rate us after you join
</marquee></div>""", unsafe_allow_html=True)
    pages = st.session_state.get("_public_pages", {})
    with st.container(key="topbar"):
        widths = [0.7, 2.2] + [1.15] * len(pages) + [1.2]
        cols = st.columns(widths, vertical_alignment="center")
        cols[0].image(str(BASE_DIR / "gym.png"), width=64)
        cols[1].markdown("<div class='pub pub-brand'>TA FITNESS GYM<small>Build Strength • Stay Fit • Transform Yourself</small></div>",
                         unsafe_allow_html=True)
        for col, (key, page) in zip(cols[2:], pages.items()):
            col.page_link(page, label=page.title, icon=page.icon, width="stretch", disabled=(key == active))
        if cols[-1].button("Login", key=f"login_{active}", icon=":material/login:", width="stretch"):
            _open_login()


def _reviews():
    """Latest public reviews. The page still works when the database is unreachable."""
    st.markdown(f'<div class="pub pub-title">{ic("forum", 30, "#ff4500")} What our members say</div>', unsafe_allow_html=True)
    try:
        import footer
        rows, stats = footer._load_feedback(limit=3)
    except Exception:
        st.info("Reviews will appear here when the gym database is online.")
        return
    footer._css()
    if not rows:
        st.info("No reviews yet. Log in and be the first to rate TA Fitness!")
        return
    st.markdown(footer._hero_html(stats), unsafe_allow_html=True)
    for r in rows:
        st.markdown(footer._card_html(r, show_private=False), unsafe_allow_html=True)


def _plan_cards():
    styles = ["linear-gradient(135deg,#ff6b6b,#ee5253)", "linear-gradient(135deg,#1dd1a1,#10ac84)",
              "linear-gradient(135deg,#48dbfb,#0abde3)", "linear-gradient(135deg,#a55eea,#6c3fc4)"]
    icons = ["fitness_center", "sports_gymnastics", "emoji_events", "workspace_premium"]
    for col, row, style, icon in zip(st.columns(4), advisor.plan_rows(), styles, icons):
        ribbon = "<div class='pub-ribbon'>BEST VALUE</div>" if row["months"] == 12 else ""
        saving = f"<div class='save'>Save ₹{row['saving']:,}</div>" if row["saving"] else "<div class='save'>Try it out</div>"
        col.markdown(f"<div class='pub pub-plan' style='background:{style}'>{ribbon}<h3>{ic(icon, 26)} {row['name']}</h3>"
                     f"<div class='amt'>₹{row['price']:,}</div><div class='per'>₹{row['per_month']} per month</div>{saving}</div>",
                     unsafe_allow_html=True)
        if "join" in st.session_state.get("_public_pages", {}):
            if col.button("Join now", key=f"join_{row['months']}", icon=":material/how_to_reg:", width="stretch"):
                st.session_state["join_plan"] = row["name"]
                st.switch_page(st.session_state["_public_pages"]["join"])


def _product_html(category, icon, name, desc, price):
    grad = CATEGORY_STYLE[category][0]
    return (f"<div class='pub pub-card pub-prod'><div class='ico' style='background:{grad}'>{ic(icon, 30)}</div>"
            f"<div class='pub-cat'>{category}</div><h4>{html.escape(name)}</h4>"
            f"<p>{html.escape(desc)}</p><div class='pub-price'>₹{price:,}</div></div>")


def public_footer(active):
    """Footer at the bottom of every public page: brand, links, plans and credits."""
    import footer
    footer._css()
    pages = st.session_state.get("_public_pages", {})
    st.markdown("---")
    brand, explore, plans, account = st.columns([1.7, 1, 1.1, 1])
    with brand:
        st.markdown(f"""
<div class="ta-footer"><div class="ta-footer-brand">
<div class="name"><img src="data:image/png;base64,{footer._logo_b64()}" alt="TA Fitness"> TA <span>Fitness</span></div>
<p>Manage memberships, attendance, renewals and payments for your gym in one place.</p>
<div class="ta-badge"><i></i> Gym membership platform</div>
</div></div>""", unsafe_allow_html=True)
    with explore:
        st.markdown('<div class="ta-footer-col"><h5>EXPLORE</h5></div>', unsafe_allow_html=True)
        for key, page in pages.items():
            st.page_link(page, label=page.title, icon=page.icon, disabled=(key == active))
    with plans:
        st.markdown('<div class="ta-footer-col"><h5>MEMBERSHIP</h5></div>', unsafe_allow_html=True)
        for row in advisor.plan_rows():
            st.markdown(f"<div class='pub' style='font-size:14px;color:#334155;margin:2px 0'>{row['name']} - ₹{row['price']:,}</div>",
                        unsafe_allow_html=True)
    with account:
        st.markdown('<div class="ta-footer-col"><h5>ACCOUNT</h5></div>', unsafe_allow_html=True)
        if st.button("Login", key=f"footer_login_{active}", icon=":material/login:"):
            _open_login()
    st.markdown("""
<div class="ta-bottom">
<span>© 2026 TA Fitness. All rights reserved.</span>
<span>Created by Tanmay Agrawal</span>
<span>Train • Track • Transform</span>
</div>""", unsafe_allow_html=True)


# ---------------------------------------------------------------- pages
def home_page():
    _top("home")
    pages = st.session_state.get("_public_pages", {})
    with st.container(key="hero"):
        left, mid, right = st.columns([1.05, 2.7, 1.05], vertical_alignment="center")
        left.image(str(BASE_DIR / "leftgym.jpg"), width="stretch")
        right.image(str(BASE_DIR / "rightgym.jpg"), width="stretch")
        with mid:
            st.markdown("""
<div class="pub pub-hero-text"><span class="tag">GYM MEMBERSHIP PLATFORM</span>
<h2>Train Hard. <span>Stay Consistent.</span><br>Transform Yourself.</h2>
<p>One customizable system for the gym owner, the trainer and every member. Browse the plans,
ask the fitness helper, then log in to manage your gym or your own fitness journey.</p>
<div class="pub-stats"><div class="pub-stat"><b>3</b><span>role logins</span></div>
<div class="pub-stat"><b>4</b><span>flexible plans</span></div>
<div class="pub-stat"><b>12</b><span>admin tools</span></div></div></div>""", unsafe_allow_html=True)
            b0, b1, b2, b3 = st.columns(4)
            if "join" in pages:
                b0.page_link(pages["join"], label="Join Now", icon=":material/how_to_reg:", width="stretch")
            if b1.button("Login", key="hero_login", icon=":material/login:", width="stretch"):
                _open_login()
            if b2.button("Try the Demo", key="hero_demo", icon=":material/play_circle:", width="stretch"):
                _open_login("Member")
            if "advisor" in pages:
                b3.page_link(pages["advisor"], label="Ask Arnold", icon=":material/smart_toy:", width="stretch")

    st.markdown('<div class="pub pub-title">Membership plans</div><div class="pub pub-sub">Pick the plan that fits your goal. '
                'The longer the plan, the lower the cost per month.</div>', unsafe_allow_html=True)
    _plan_cards()

    st.markdown('<div class="pub pub-title">Why TA Fitness</div>', unsafe_allow_html=True)
    for start in range(0, len(FEATURES), 3):
        for col, (icon, title, text) in zip(st.columns(3), FEATURES[start:start + 3]):
            col.markdown(f"<div class='pub pub-card'><div class='ico'>{ic(icon, 30)}</div><h4>{title}</h4><p>{text}</p></div>",
                         unsafe_allow_html=True)
        st.write("")

    st.markdown('<div class="pub pub-title">How it works</div>', unsafe_allow_html=True)
    for col, (n, title, text) in zip(st.columns(3), STEPS):
        col.markdown(f"<div class='pub pub-step'><div class='n'>{n}</div><h4>{title}</h4><p>{text}</p></div>",
                     unsafe_allow_html=True)

    _reviews()
    st.markdown('<div class="pub pub-cta"><h3>Ready to transform yourself?</h3>'
                '<p>Log in to your Admin, Team or Member page and get started.</p></div>', unsafe_allow_html=True)
    _, mid_btn, _ = st.columns([2, 1.2, 2])
    if mid_btn.button("Login now", key="cta_login", icon=":material/login:", width="stretch"):
        _open_login()
    public_footer("home")


def store_page():
    _top("store")
    st.markdown(f'<div class="pub pub-page-title">{ic("shopping_cart", 44)} TA Fitness Store</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pub pub-note">{ic("info", 20, "#c2410c")}<span>Supplements do not replace a balanced diet. Check with a doctor or '
                'dietitian before you start any supplement, especially if you have a health condition.</span></div>', unsafe_allow_html=True)
    search = st.text_input("Search products", placeholder="Search protein, rope, bag...", icon=":material/search:").strip().lower()
    cats = ["All"] + list(CATEGORY_STYLE)
    tabs = st.tabs([f":material/{CATEGORY_STYLE[c][1]}: {c}" if c in CATEGORY_STYLE else ":material/apps: All" for c in cats])
    for tab, cat in zip(tabs, cats):
        with tab:
            items = [p for p in PRODUCTS if (cat == "All" or p[0] == cat)
                     and (not search or search in p[2].lower() or search in p[3].lower())]
            st.caption(f"{len(items)} product{'s' if len(items) != 1 else ''}")
            if not items:
                st.info("No products match your search.")
            for start in range(0, len(items), 4):
                for col, (category, icon, name, desc, price) in zip(st.columns(4), items[start:start + 4]):
                    col.markdown(_product_html(category, icon, name, desc, price), unsafe_allow_html=True)
                st.write("")
    public_footer("store")


# ---------------------------------------------------------------- Arnold, the fitness companion
HELPER_NAME = "Arnold"
SAFE_CHECK = "Safe-to-Train Check"
VIEWS = ["Arnold", "Health checker", SAFE_CHECK, "Plan finder"]
GREETING = (f"Namaste! I am **{HELPER_NAME}**, your fitness companion, and I am happy to help. Type or speak your question "
            "above, in English or Hindi, or pick one below: plans, workouts, food, recovery or how a health condition affects "
            "exercise.")

# (heading, [(chip text, kind, value)]) kind "ask" sends the question, kind "go" opens a tool
CHIP_GROUPS = [
    ("Explore gym options", [("Which plan is best value?", "ask", None), ("Suggest a beginner routine", "ask", None),
                             ("What should I eat before a workout?", "ask", None), ("Do I need protein?", "ask", None)]),
    ("Your body, your questions", [("Why are my muscles sore?", "ask", None), ("Weight loss tips", "ask", None),
                                   ("How to build muscle", "ask", None), ("How much water should I drink?", "ask", None)]),
    ("Try something new", [("Check my BMI", "go", "Health checker"), ("Am I safe to start training?", "go", SAFE_CHECK),
                           ("Build my weekly plan", "go", "Plan finder"), ("I have back pain", "ask", None)]),
]


MAX_AI_QUESTIONS = 25      # Gemini questions per visitor session (the free quota is shared by everyone)
MIN_SECONDS_BETWEEN = 2


def _ask(question, fallback=None):
    """Answer a question: emergency words first, then Gemini, then a fallback (with a note saying why).

    fallback is a ready-made answer for this question; without one the built-in answers are used.
    """
    chat = st.session_state.setdefault("_helper_chat", [])
    q = gemini.clean_question(question)
    if not q:
        return
    if gemini.is_emergency(q):  # never depend on the network for an emergency
        chat.append((q, gemini.EMERGENCY_REPLY))
        st.session_state["_type_last"] = True
        return
    reply, why = None, ""
    used = st.session_state.get("_ai_calls", 0)
    if not gemini.is_configured():
        why = "The AI service is not connected, so this is a quick built-in answer."
    elif used >= MAX_AI_QUESTIONS:
        why = "You have reached the AI question limit for this visit, so this is a quick built-in answer."
    elif time.time() - st.session_state.get("_ai_last", 0) < MIN_SECONDS_BETWEEN:
        why = "Please wait a moment between questions. This is a quick built-in answer."
    else:
        try:
            reply = gemini.ask_gemini(q, chat)
            st.session_state["_ai_calls"] = used + 1
            st.session_state["_ai_last"] = time.time()
        except Exception:
            why = "The AI service is busy right now, so this is a quick built-in answer. Please ask again in a moment."
    if reply is None:
        reply = (fallback or advisor.answer(q)) + f"\n\n*{why}*"
    chat.append((q, reply))
    st.session_state["_type_last"] = True  # the new answer is shown with the typing effect once


def _clear_chat():
    st.session_state["_helper_chat"] = []


def _go(view):
    st.session_state["helper_view"] = view


def _queue(question, fallback=None, fresh=False):
    """Hand a question to Arnold. It is answered on the Arnold screen, under a "thinking" indicator."""
    if fresh:
        _clear_chat()
    st.session_state["_pending_q"] = (question, fallback)
    _go("Arnold")


def _suggestions(chat, n=4):
    """Suggested follow-up questions that have not been asked yet in this chat."""
    asked = {q.lower() for q, _ in chat}
    pool = [text for _, chips in CHIP_GROUPS for text, kind, _ in chips if kind == "ask"]
    return [t for t in pool if t.lower() not in asked][:n]


def _typing(text, delay=0.025):
    """Yield the answer word by word, so it appears as if Arnold is typing it."""
    for piece in re.split(r"(\s+)", text):
        yield piece
        if piece.strip():
            time.sleep(delay)


def _message(question, reply, typing=False):
    with st.chat_message("user", avatar=":material/person:"):
        st.write(question)
    with st.chat_message("assistant", avatar=":material/auto_awesome:"):
        if typing:
            st.write_stream(_typing(reply))
        else:
            st.markdown(reply)


# Voice typing: a small button that uses the visitor's own browser speech-to-text (Chrome and Edge) and puts the
# words in the question box for them to check and send. The app never records, stores or sends any audio.
MIC_HTML = """
<div id="wrap">
  <button id="mic" type="button" title="Speak your question">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <rect x="9" y="2" width="6" height="12" rx="3"></rect>
      <path d="M5 11a7 7 0 0 0 14 0h-2a5 5 0 0 1-10 0H5z"></path>
      <rect x="11" y="18" width="2" height="4"></rect>
    </svg>
    <span id="label">Speak</span>
  </button>
  <select id="lang" title="Voice language">
    <option value="en-IN">English</option>
    <option value="hi-IN">हिन्दी</option>
  </select>
  <span id="status">Tap Speak, ask your question, then check it and press send.</span>
</div>
<style>
  body{margin:0;background:transparent;font-family:'Poppins','Segoe UI',sans-serif;}
  #wrap{display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;padding:4px;}
  #mic{display:inline-flex;align-items:center;gap:6px;border:none;border-radius:999px;padding:7px 16px;font-weight:700;
       font-size:14px;color:#fff;background:linear-gradient(45deg,#ff512f,#f09819);cursor:pointer;box-shadow:0 3px 10px rgba(255,81,47,.35);}
  #mic:disabled{opacity:.5;cursor:not-allowed;}
  #mic.on{background:#dc2626;animation:pulse 1.2s infinite;}
  @keyframes pulse{0%{box-shadow:0 0 0 0 rgba(220,38,38,.5);}70%{box-shadow:0 0 0 10px rgba(220,38,38,0);}100%{box-shadow:0 0 0 0 rgba(220,38,38,0);}}
  #lang{border:1px solid #fdba74;border-radius:999px;padding:6px 10px;font-size:13px;color:#9a3412;background:#fff7f0;}
  #status{font-size:12px;color:#64748b;}
</style>
<script>
(function () {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const mic = document.getElementById('mic'), label = document.getElementById('label');
  const lang = document.getElementById('lang'), status = document.getElementById('status');
  try { const saved = window.localStorage.getItem('arnold_voice_lang'); if (saved) lang.value = saved; } catch (e) {}
  lang.addEventListener('change', function () { try { window.localStorage.setItem('arnold_voice_lang', lang.value); } catch (e) {} });

  function box() {
    try {
      const doc = window.parent.document;
      return doc.querySelector('.st-key-arnold [data-testid="stChatInputTextArea"]') || doc.querySelector('[data-testid="stChatInputTextArea"]');
    } catch (e) { return null; }
  }
  function fill(text) {  // put the words in Arnold's question box, the same way typing would
    const ta = box();
    if (!ta) return false;
    const setter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, 'value').set;
    setter.call(ta, text);
    ta.dispatchEvent(new window.parent.Event('input', { bubbles: true }));
    ta.focus();
    return true;
  }
  window.fillQuestion = fill;

  if (!SR) { mic.disabled = true; status.textContent = 'Voice typing works in Chrome or Edge.'; return; }
  let rec = null, listening = false, finalText = '';
  mic.addEventListener('click', function () {
    if (listening) { if (rec) rec.stop(); return; }
    rec = new SR();
    rec.lang = lang.value; rec.interimResults = true; rec.continuous = false; rec.maxAlternatives = 1;
    finalText = '';
    rec.onstart = function () { listening = true; mic.classList.add('on'); label.textContent = 'Listening... tap to stop'; status.textContent = ''; };
    rec.onresult = function (ev) {
      let interim = '';
      for (let i = ev.resultIndex; i < ev.results.length; i++) {
        const t = ev.results[i][0].transcript;
        if (ev.results[i].isFinal) { finalText += t; } else { interim += t; }
      }
      fill((finalText + ' ' + interim).trim());
    };
    rec.onerror = function (ev) {
      if (ev.error === 'not-allowed' || ev.error === 'service-not-allowed') status.textContent = 'Please allow the microphone for this site.';
      else if (ev.error === 'no-speech') status.textContent = 'No speech heard. Please try again.';
      else status.textContent = 'Voice typing stopped. Please try again.';
    };
    rec.onend = function () {
      listening = false; mic.classList.remove('on'); label.textContent = 'Speak';
      if (finalText.trim()) status.textContent = 'Check the words, then press send.';
    };
    try { rec.start(); } catch (e) { status.textContent = 'Voice typing could not start.'; }
  });
})();
</script>
"""


def _card_header(icon, title, subtitle, online=False):
    """Shared header of every Ask Arnold card."""
    pill = "<span class='ar-online'><i></i>Online</span>" if online else ""
    st.markdown(f"<div class='pub ar-head'>{pill}<div class='ar-name'>{title} {ic(icon, 28, '#ff4500')}</div>"
                f"<div class='ar-sub'>{subtitle}</div></div>", unsafe_allow_html=True)


def _arnold_view():
    chat = st.session_state.setdefault("_helper_chat", [])
    with st.container(key="arnold"):
        _card_header("auto_awesome", HELPER_NAME, "Your AI Fitness Companion", online=True)
        prompt = st.chat_input(f"Ask {HELPER_NAME} anything, in English or Hindi...", key="arnold_input")
        components.html(MIC_HTML, height=48)
        st.markdown("<div class='pub ar-disc'>Answers are written by AI and can be wrong. Do not share personal or medical details "
                    "here. Voice typing uses your browser's own speech service; this app never records audio. "
                    + html.escape(advisor.DISCLAIMER) + "</div>", unsafe_allow_html=True)
        _, rcol, _ = st.columns([1, 1.6, 1])
        rcol.button("Check a health report (PDF)", key="arnold_report", icon=":material/description:",
                    on_click=_open_report_tool, width="stretch")
        pending = st.session_state.pop("_pending_q", None)
        if prompt:
            pending = (prompt, None)
        if pending:
            with st.spinner(f"{HELPER_NAME} is thinking..."):
                _ask(*pending)
            st.rerun()
        with st.container(key="arnold_body"):
            if chat:
                h1, h2 = st.columns([5, 1.3], vertical_alignment="center")
                h1.markdown("<div class='pub ar-h'>Latest answer</div>", unsafe_allow_html=True)
                h2.button("New chat", key="new_chat", icon=":material/add_comment:", on_click=_clear_chat, width="stretch")
                _message(*chat[-1], typing=st.session_state.pop("_type_last", False))
                suggestions = _suggestions(chat)
                if suggestions:
                    st.markdown("<div class='pub ar-h'>Suggested questions</div>", unsafe_allow_html=True)
                    for i, (col, text) in enumerate(zip(st.columns(len(suggestions)), suggestions)):
                        col.button(text, key=f"chip_s_{i}", on_click=_queue, args=(text,), width="stretch")
                older = chat[:-1]
                if older:
                    with st.expander(f"Earlier in this chat ({len(older)})", icon=":material/history:"):
                        for question, reply in reversed(older[-8:]):
                            _message(question, reply)
            else:
                st.markdown(f"<div class='pub ar-p' style='margin-top:12px'>{GREETING.replace('**', '')}</div>", unsafe_allow_html=True)
                st.button("Check my BMI and health", key="cta_health", icon=":material/monitor_heart:",
                          on_click=_go, args=("Health checker",), width="stretch")
                for gi, (heading, chips) in enumerate(CHIP_GROUPS):
                    st.markdown(f"<div class='pub ar-h'>{heading}</div>", unsafe_allow_html=True)
                    for ci, (col, (text, kind, value)) in enumerate(zip(st.columns(len(chips)), chips)):
                        if kind == "ask":
                            col.button(text, key=f"chip_{gi}_{ci}", on_click=_queue, args=(text,), width="stretch")
                        else:
                            col.button(text, key=f"chip_{gi}_{ci}", on_click=_go, args=(value,), width="stretch")


def _ask_about_results(answers):
    """Open a fresh Arnold chat that asks about the readiness result (no name, age or ID is sent).

    If the AI cannot answer, Arnold shows a summary of the person's own next steps instead of a general tip.
    """
    r = advisor.parq_report(answers)
    lines = ["Here is a summary of your next steps.", "", "**Questions to ask your doctor**"]
    lines += [f"- {q}" for q in r["doctor_questions"]]
    lines += ["", "**Until you see your doctor:** " + "; ".join(r["do"]).lower() + ".",
              "", "**Avoid for now:** " + "; ".join(dict.fromkeys(r["avoid"])).lower() + ".",
              "", "Stop and call 112 if you get chest pain, fainting, severe breathlessness or a racing heartbeat."]
    _queue(r["arnold_question"], "\n".join(lines), fresh=True)


def _readiness_result(answers):
    """Results of the readiness check: next steps for every Yes, or a starter plan when all answers are No."""
    r = advisor.parq_report(answers)
    download = dict(label="Download my next steps", data=advisor.parq_text(answers), file_name="TA_Fitness_Safe_to_Train.txt",
                    mime="text/plain", icon=":material/download:", key="dl_steps", width="stretch")
    if not r["needs_doctor"]:
        steps = "".join(f"<li>{html.escape(t)}</li>" for t in r["steps"])
        st.markdown(f"<div class='pub res ok'>{ic('check_circle', 38, '#059669')}<div><b>No warning signs in your answers</b>"
                    "You answered No to every question, so these answers do not show a reason to wait. This is not a medical check."
                    f"<br><br><b>Your starter plan</b><ol style='margin:6px 0 0 18px;padding:0'>{steps}</ol></div></div>",
                    unsafe_allow_html=True)
        st.download_button(**download)
        st.caption(advisor.DISCLAIMER)
        return

    n = len(r["flagged"])
    st.markdown(f"<div class='pub res warn'>{ic('warning', 38, '#ea580c')}<div><b>Please see a doctor before you start</b>"
                f"You answered Yes to {n} of 7 questions. That does not mean you cannot exercise. It means a doctor should "
                "check first and tell you what is safe for you. Below are your next steps.</div></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='pub nx-h'>{ic('info', 22, '#ff4500')} Why this matters</div>", unsafe_allow_html=True)
    for f in r["flagged"]:
        st.markdown(f"<div class='pub nx-card'><div class='q'>{html.escape(f['question'])}</div><div>{html.escape(f['why'])}</div></div>",
                    unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")
    with left:
        qs = "".join(f"<li>{html.escape(q)}</li>" for q in r["doctor_questions"])
        st.markdown(f"<div class='pub nx-box'><div class='nx-h'>{ic('stethoscope', 22, '#ff4500')} Questions to ask your doctor</div>"
                    f"<ol>{qs}</ol><p>Take this list, and your answers to the seven questions, to your appointment.</p></div>",
                    unsafe_allow_html=True)
    with right:
        do = "".join(f"<li>{html.escape(t)}</li>" for t in r["do"])
        avoid = "".join(f"<li>{html.escape(t)}</li>" for t in dict.fromkeys(r["avoid"]))
        st.markdown(f"<div class='pub nx-box'><div class='nx-h'>{ic('schedule', 22, '#ff4500')} Until you see your doctor</div>"
                    f"<div class='nx-ok'>{ic('check_circle', 18, '#059669')} Usually fine</div><ul>{do}</ul>"
                    f"<div class='nx-no'>{ic('block', 18, '#dc2626')} Avoid for now</div><ul>{avoid}</ul></div>",
                    unsafe_allow_html=True)

    flags = "".join(f"<li>{html.escape(t)}</li>" for t in r["red_flags"])
    st.markdown(f"<div class='pub nx-red'><div class='nx-h' style='color:#b91c1c'>{ic('emergency', 22, '#dc2626')} Stop and get help now (call 112) if you have</div>"
                f"<ul>{flags}</ul></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='pub nx-h'>{ic('auto_awesome', 22, '#ff4500')} What next?</div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        st.download_button(**download)
    b2.button(f"Ask {HELPER_NAME} about my results", key="ask_results", icon=":material/auto_awesome:",
              on_click=_ask_about_results, args=(answers,), width="stretch")
    st.caption(f"The download stays on your device. Asking {HELPER_NAME} sends only the topics above "
               f"({'; '.join(f['topic'] for f in r['flagged'])}) to an AI service, with no name, age or ID. " + advisor.DISCLAIMER)


def _health_view():
    with st.container(key="tool_health"):
        _card_header("monitor_heart", "Health checker", "Check your BMI, daily calories, water and protein in a minute.")
        with st.form("health_form", border=False):
            c1, c2, c3 = st.columns(3)
            age = c1.number_input("Age (years)", min_value=18, max_value=80, value=25, step=1)
            gender = c2.radio("Gender", ["Male", "Female"], horizontal=True)
            activity = c3.selectbox("Activity level", list(advisor.ACTIVITY))
            c4, c5, c6 = st.columns(3)
            height = c4.number_input("Height (cm)", min_value=120, max_value=220, value=170, step=1)
            weight = c5.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=65.0, step=0.5)
            goal = c6.selectbox("Your goal", advisor.GOALS)
            go = st.form_submit_button("Check my health", icon=":material/monitor_heart:", width="stretch")
        if go:
            st.session_state["_hc"] = (advisor.health_check(age, gender, height, weight, activity, goal), goal, height, weight)
        if "_hc" not in st.session_state:
            st.info("Fill in your details and press Check my health.", icon=":material/info:")
            return
        r, goal_used, h_used, w_used = st.session_state["_hc"]
        if r["to_healthy"] == 0:
            range_note = ". You are in this range."
        else:
            range_note = f". You are about {abs(r['to_healthy'])} kg {'above' if r['to_healthy'] > 0 else 'below'} it."
        st.markdown(f"""
<div class='pub metric-grid'>
<div class='metric'><span class='k'>{ic('speed', 18)} Your BMI</span><b>{r['bmi']}</b><span class='badge' style='background:{r['colour']}'>{r['category']}</span></div>
<div class='metric'><span class='k'>{ic('local_fire_department', 18)} Daily calories</span><b>{r['target']:,}</b><span class='note'>kcal, {r['target_note']}</span></div>
<div class='metric'><span class='k'>{ic('water_drop', 18)} Water per day</span><b>{r['water_l']} L</b><span class='note'>more on training days</span></div>
<div class='metric'><span class='k'>{ic('nutrition', 18)} Protein per day</span><b>{r['protein_low']}-{r['protein_high']} g</b><span class='note'>if you train regularly</span></div>
</div>
<div class='pub side-card'><h5>{ic('straighten', 20, '#ff4500')} Where you are on the BMI scale</h5>
<div class='bmi-bar'><i style='width:14%;background:#0ea5e9'></i><i style='width:26%;background:#16a34a'></i><i style='width:20%;background:#f59e0b'></i><i style='width:40%;background:#dc2626'></i>
<span class='mark' style='left:{advisor.bmi_marker_percent(r['bmi']):.1f}%'></span></div>
<div class='bmi-scale'><span style='left:0'>15</span><span style='left:14%'>18.5</span><span style='left:40%'>25</span><span style='left:60%'>30</span><span style='left:100%'>40</span></div>
<p>A healthy weight for {h_used} cm is about <b>{r['healthy_low']} to {r['healthy_high']} kg</b>{range_note}</p></div>
""", unsafe_allow_html=True)
        tips = advisor.health_advice(r)
        advice = "".join(f"<li>{html.escape(t)}</li>" for t in tips)
        st.markdown(f"<div class='pub side-card'><h5>{ic('lightbulb', 20, '#ff4500')} What this means</h5>"
                    f"<ul style='margin:6px 0 0 18px;padding:0;font-size:14px;color:#334155'>{advice}</ul></div>", unsafe_allow_html=True)
        question = (f"My BMI category is {r['category'].lower()} and my goal is: {goal_used.lower()}. What training and eating "
                    "habits would help me most, and what should I be careful about?")
        fallback = "Here are general tips for your result:\n\n" + "\n".join(f"- {t}" for t in tips)
        st.button(f"Ask {HELPER_NAME} about my results", key="ask_health", icon=":material/auto_awesome:",
                  on_click=_queue, args=(question, fallback, True), width="stretch")
        st.caption(f"Asking {HELPER_NAME} sends only your BMI category ({r['category'].lower()}) and your goal to an AI service, "
                   "never your age, height, weight or other numbers. BMI: WHO adult categories. Calories: Mifflin-St Jeor "
                   "estimate. Water and protein are general ranges. " + advisor.DISCLAIMER)


# the seven PAR-Q questions, grouped by topic: (heading, icon, question indexes)
SAFE_GROUPS = [("Heart and chest", "cardiology", [0, 1, 2]), ("Balance", "accessibility_new", [3]),
               ("Bones and joints", "orthopedics", [4]), ("Medicines and other reasons", "medication", [5, 6])]


RC_FIELDS = [("sys", "Blood pressure: upper (systolic), mmHg", 60.0, 260.0, 1.0),
             ("dia", "Blood pressure: lower (diastolic), mmHg", 30.0, 160.0, 1.0),
             ("sugar", "Fasting blood sugar, mg/dL", 20.0, 600.0, 1.0),
             ("hba1c", "HbA1c, %", 3.0, 20.0, 0.1),
             ("chol", "Total cholesterol, mg/dL", 50.0, 500.0, 1.0),
             ("ldl", "LDL cholesterol, mg/dL", 10.0, 400.0, 1.0),
             ("hb", "Haemoglobin, g/dL", 3.0, 25.0, 0.1)]
MAX_REPORT_MB = 5


def _open_report_tool():
    """From Arnold: open the Safe-to-Train page with the report check shown first."""
    st.session_state["_report_first"] = True
    _go(SAFE_CHECK)


def _report_section():
    """Optional health report check. The PDF is read only inside this app: it is not sent to any AI service and not saved."""
    import report_check as rc
    with st.container(border=True, key="report_box"):
        st.markdown(f"<div class='pub sc-group' style='margin-top:4px'>{ic('description', 22, '#ff4500')} Check my health report "
                    "(optional)</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pub pub-note'>{ic('lock', 20, '#c2410c')}<span>Your report is read only inside this app to find a "
                    "few values. It is <b>not sent to any AI service</b> and <b>not saved</b>; it is forgotten when you close the page. "
                    "Asking Arnold later sends only topic words such as \"high blood pressure\": no numbers, no name, no report.</span></div>",
                    unsafe_allow_html=True)
        up = st.file_uploader("Upload a PDF report from your computer", type=["pdf"], key="rc_file",
                              help=f"Typed PDF reports work best (up to {MAX_REPORT_MB} MB). For a photo of a report, type the values below.")
        if up is not None and st.session_state.get("_rc_file_id") != up.file_id:
            st.session_state["_rc_file_id"] = up.file_id
            if up.size > MAX_REPORT_MB * 1024 * 1024:
                st.session_state["_rc_found"] = -1
            else:
                found = rc.find_values(rc.pdf_text(up.getvalue()))
                for key, *_ in RC_FIELDS:
                    st.session_state[f"rc_{key}"] = found.get(key)
                st.session_state["_rc_found"] = sum(1 for key, *_ in RC_FIELDS if found.get(key) is not None)
        n = st.session_state.get("_rc_found")
        if n == -1:
            st.error(f"That file is larger than {MAX_REPORT_MB} MB. Please upload a smaller PDF or type the values below.")
        elif n == 0:
            st.warning("No values could be read from this report (it may be a scanned photo). Please type the values below.",
                       icon=":material/edit:")
        elif n:
            st.success(f"Found {n} of {len(RC_FIELDS)} values in your report. Please check them below and correct anything that is wrong.",
                       icon=":material/fact_check:")

        st.markdown("<div class='pub ar-p'>Leave a box empty if that test is not in your report.</div>", unsafe_allow_html=True)
        gender = st.radio("Gender (used for the haemoglobin range)", ["Male", "Female"], horizontal=True, key="rc_gender")
        cols = st.columns(2)
        for i, (key, label, lo, hi, step) in enumerate(RC_FIELDS):
            st.session_state.setdefault(f"rc_{key}", None)
            cols[i % 2].number_input(label, min_value=lo, max_value=hi, step=step, key=f"rc_{key}", placeholder="not tested")
        if st.button("Check these values", key="rc_check", icon=":material/monitor_heart:", width="stretch"):
            values = {key: st.session_state.get(f"rc_{key}") for key, *_ in RC_FIELDS}
            if all(v is None for v in values.values()):
                st.warning("Please enter at least one value.")
            else:
                st.session_state["_rc_result"] = rc.assess(values, gender)
        if "_rc_result" in st.session_state:
            _report_result(*st.session_state["_rc_result"])


def _report_result(findings, urgent):
    import report_check as rc
    if urgent:
        st.markdown(f"<div class='pub res warn' style='background:#fef2f2;border-color:#fca5a5;color:#7f1d1d'>{ic('emergency', 38, '#dc2626')}"
                    "<div><b>Please get medical help today</b>Your blood pressure is in the very high range. Do not exercise. "
                    "If you also have chest pain, breathlessness, a severe headache or blurred vision, call 112 now.</div></div>",
                    unsafe_allow_html=True)
        return
    rows = "".join(f"<div class='wk'><span class='d' style='flex:0 0 150px;color:{'#dc2626' if f['flag'] else '#059669'}'>{html.escape(f['label'])}</span>"
                   f"<span style='flex:0 0 110px'><b>{html.escape(f['value'])}</b></span><span>{html.escape(f['category'])}"
                   f"<br><small style='color:#64748b'>Range: {html.escape(f['source'])}</small></span></div>" for f in findings)
    flagged = [f for f in findings if f["flag"]]
    if flagged:
        st.markdown(f"<div class='pub res warn'>{ic('warning', 38, '#ea580c')}<div><b>Please see a doctor before you start training</b>"
                    f"{len(flagged)} of your values are outside the usual range. That does not mean you cannot exercise; a doctor "
                    "should tell you what is safe for you first.</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='pub res ok'>{ic('check_circle', 38, '#059669')}<div><b>These values do not flag anything</b>"
                    "They are within the usual adult ranges. This is not a medical check and does not mean you are fit for any "
                    "exercise; start gradually.</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='pub side-card'><h5>{ic('lab_profile', 20, '#ff4500')} Your values</h5>{rows}"
                "<p style='margin-top:8px'>Your report's own lab range is the one to trust if it differs from these general adult ranges.</p></div>",
                unsafe_allow_html=True)
    if flagged:
        qs = "".join(f"<li>{html.escape(q)}</li>" for f in flagged for q in f["questions"])
        st.markdown(f"<div class='pub nx-box'><div class='nx-h'>{ic('stethoscope', 22, '#ff4500')} Questions to ask your doctor</div>"
                    f"<ol>{qs}</ol></div>", unsafe_allow_html=True)
        question = rc.arnold_question(findings)
        fallback = "Here are the questions to take to your doctor:\n\n" + "\n".join(f"- {q}" for f in flagged for q in f["questions"])
        st.button(f"Ask {HELPER_NAME} about this", key="rc_ask", icon=":material/auto_awesome:",
                  on_click=_queue, args=(question, fallback, True), width="stretch")
        st.caption(f"Asking {HELPER_NAME} sends only these topic words: " + "; ".join(f["topic"] for f in flagged) + ". " + advisor.DISCLAIMER)
    else:
        st.caption(advisor.DISCLAIMER)


def _readiness_view():
    report_first = st.session_state.get("_report_first", False)  # opened from Arnold's "Check a health report"
    with st.container(key="tool_ready"):
        _card_header("health_and_safety", SAFE_CHECK, "Find out in one minute whether you should see a doctor before you start training.")
        if report_first:
            _report_section()
        st.markdown(f"<div class='pub sc-badges'><span>{ic('checklist', 18)} 7 questions</span><span>{ic('timer', 18)} 1 minute</span>"
                    f"<span>{ic('lock', 18)} Answers are not saved</span><span>{ic('verified', 18)} Based on the PAR-Q</span></div>"
                    "<div class='pub ar-p' style='text-align:center'>Answer Yes or No. The PAR-Q (Physical Activity Readiness "
                    "Questionnaire) is a standard screening used before starting exercise.</div>", unsafe_allow_html=True)
        with st.form("parq_form", border=False):
            answers = {}
            for heading, icon, indexes in SAFE_GROUPS:
                st.markdown(f"<div class='pub sc-group'>{ic(icon, 22, '#ff4500')} {heading}</div>", unsafe_allow_html=True)
                for i in indexes:
                    with st.container(border=True):
                        q1, q2 = st.columns([5, 1.4], vertical_alignment="center")
                        q1.markdown(f"<div class='pub qrow'><span class='qn'>{i + 1}</span><span>{html.escape(advisor.PARQ[i])}</span></div>",
                                    unsafe_allow_html=True)
                        answers[i] = q2.radio(f"Question {i + 1}", ["No", "Yes"], horizontal=True, key=f"parq_{i + 1}",
                                              label_visibility="collapsed")
            answers = [answers[i] for i in range(len(advisor.PARQ))]
            done = st.form_submit_button("See my result", icon=":material/fact_check:", width="stretch")
        if done:
            st.session_state["_parq"] = [a == "Yes" for a in answers]
        if "_parq" in st.session_state:
            _readiness_result(st.session_state["_parq"])
        if not report_first:
            _report_section()


def _plan_view():
    with st.container(key="tool_plan"):
        _card_header("target", "Plan finder", "Tell us about yourself and get a membership plan with a starter week.")
        left, right = st.columns([1, 1.15], gap="large")
        with left:
            goal = st.segmented_control("Your goal", advisor.GOALS, default=advisor.GOALS[2], key="pf_goal") or advisor.GOALS[2]
            experience = st.selectbox("Your experience", advisor.EXPERIENCE, key="pf_exp")
            days = st.slider("Days you can train each week", 2, 6, 3, key="pf_days")
            commit = st.segmented_control("How long will you train?", ["Not sure yet", "3 months", "6 months", "12 months"],
                                          default="Not sure yet", key="pf_commit") or "Not sure yet"
        months = {"Not sure yet": 0, "3 months": 3, "6 months": 6, "12 months": 12}[commit]
        row, why = advisor.plan_for(goal, months)
        saving = f"Save ₹{row['saving']:,}" if row["saving"] else "Best way to start"
        with right:
            st.markdown(f"<div class='pub plan-big'><div style='opacity:.9;font-size:13px;letter-spacing:1.5px;font-weight:700'>RECOMMENDED FOR YOU</div>"
                        f"<h3>{row['name']}</h3><div class='amt'>₹{row['price']:,}</div>"
                        f"<div>₹{row['per_month']} per month • {saving}</div>"
                        f"<div style='margin-top:10px;font-size:15px;opacity:.95'>{html.escape(why)}</div></div>", unsafe_allow_html=True)
        week = advisor.weekly_plan(experience, days, goal)
        rows_html = "".join(f"<div class='wk'><span class='d'>{d}</span><span>{html.escape(t)}</span></div>" for d, t in week)
        st.markdown(f"<div class='pub side-card' style='margin-top:14px'><h5>{ic('calendar_month', 20, '#ff4500')} Your starter week</h5>{rows_html}"
                    "<p style='margin-top:8px'>Rest on the other days. This is general guidance; ask a trainer to adjust it for you.</p></div>",
                    unsafe_allow_html=True)
        level = experience.split(" (")[0].lower()
        week_text = "; ".join(f"{d}: {t}" for d, t in week)
        question = (f"I am a {level} and my goal is: {goal.lower()}. I can train {days} days a week. My starter week is: "
                    f"{week_text}. Please adjust it with specific exercises, sets, reps and rest times.")
        fallback = ("Here is your starter week again:\n\n" + "\n".join(f"- **{d}:** {t}" for d, t in week)
                    + "\n\nAsk a trainer at the gym to add specific exercises for you.")
        b1, b2 = st.columns(2)
        pages = st.session_state.get("_public_pages", {})
        if "join" in pages and b1.button(f"Join with the {row['name']} plan", key="pf_join", icon=":material/how_to_reg:", width="stretch"):
            st.session_state["join_plan"] = row["name"]
            st.switch_page(pages["join"])
        b2.button(f"Ask {HELPER_NAME} to adjust my week", key="pf_ask", icon=":material/auto_awesome:",
                  on_click=_queue, args=(question, fallback, True), width="stretch")
        st.caption(f"Asking {HELPER_NAME} sends only your goal, experience level, training days and starter week to an AI service.")


def advisor_page():
    _top("advisor")
    if st.session_state.get("helper_view") not in (None, *VIEWS):  # e.g. a section name from an older version
        st.session_state["helper_view"] = "Arnold"
    view = st.segmented_control("Tools", VIEWS, default="Arnold", key="helper_view", label_visibility="collapsed") or "Arnold"
    if view == "Arnold":
        _arnold_view()
    elif view == "Health checker":
        _health_view()
    elif view == SAFE_CHECK:
        _readiness_view()
    else:
        _plan_view()
    public_footer("advisor")
