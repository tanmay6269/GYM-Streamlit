"""One real page (with its own URL) for every menu option, per role.

Because each option has its own address (for example /payments), the browser's
back and forward arrows move between options instead of leaving the site, and
every link in the footer can point straight at a page.
"""
import streamlit as st


def _member_id():
    return st.session_state.user["UserID"]


# ---------------- Admin ----------------
def _insert_member():
    from code1 import insert_member
    insert_member()


def _display_all():
    from code2 import display_all_members
    display_all_members()


def _search_member():
    from code3 import search_memberById
    search_memberById()


def _edit_member():
    from code4 import edit_member
    edit_member()


def _delete_member():
    from code5 import delete_member
    delete_member()


def _add_staff():
    from admin_functions import add_staff
    add_staff()


def _edit_staff():
    from admin_functions import edit_staff
    edit_staff()


def _reports():
    from admin_functions import view_reports
    view_reports()


def _admin_renew():
    from admin_functions import admin_renew_membership
    admin_renew_membership()


def _payments():
    from admin_functions import manage_payments
    manage_payments()


# ---------------- Team ----------------
def _attendance():
    from team_functions import mark_attendance
    mark_attendance()


def _team_renew():
    from team_functions import team_renew_membership
    team_renew_membership()


# ---------------- Member ----------------
def _my_profile():
    from member_functions import display_member_profile
    display_member_profile(_member_id())


def _my_membership():
    from member_functions import display_membership_details
    display_membership_details(_member_id())


def _my_attendance():
    from member_functions import display_attendance
    display_attendance(_member_id())


def _payment_history():
    from member_functions import display_payment_history
    display_payment_history(_member_id())


def _quiz():
    from member_functions import fitness_quiz
    fitness_quiz(_member_id())


# ---------------- Shared ----------------
def _home():
    from GYM import render_home
    render_home()


def _feedback():
    from footer import feedback_page
    feedback_page()


# key -> (function, title, material icon, url path)
_ADMIN = [
    ("home", _home, "Home", ":material/home:", ""),
    ("insert", _insert_member, "Insert Member", ":material/person_add:", "insert-member"),
    ("all", _display_all, "Display All Members", ":material/groups:", "all-members"),
    ("search", _search_member, "Search Member By ID", ":material/search:", "search-member"),
    ("edit", _edit_member, "Edit Member", ":material/edit:", "edit-member"),
    ("delete", _delete_member, "Delete Member", ":material/delete:", "delete-member"),
    ("add_staff", _add_staff, "Add Staff", ":material/person_add_alt:", "add-staff"),
    ("edit_staff", _edit_staff, "Edit Staff", ":material/manage_accounts:", "edit-staff"),
    ("reports", _reports, "View Reports", ":material/monitoring:", "reports"),
    ("renew", _admin_renew, "Membership Renewal", ":material/autorenew:", "renewal"),
    ("payments", _payments, "Payments", ":material/payments:", "payments"),
    ("feedback", _feedback, "Feedback", ":material/forum:", "feedback"),
]
_TEAM = [
    ("home", _home, "Home", ":material/home:", ""),
    ("search", _search_member, "Search Member", ":material/search:", "search-member"),
    ("edit", _edit_member, "Edit Member", ":material/edit:", "edit-member"),
    ("attendance", _attendance, "Attendance", ":material/fact_check:", "attendance"),
    ("renew", _team_renew, "Renew Membership", ":material/autorenew:", "renewal"),
    ("feedback", _feedback, "Feedback", ":material/forum:", "feedback"),
]
_MEMBER = [
    ("home", _home, "Home", ":material/home:", ""),
    ("profile", _my_profile, "My Profile", ":material/account_circle:", "my-profile"),
    ("membership", _my_membership, "My Membership", ":material/calendar_month:", "my-membership"),
    ("attendance", _my_attendance, "My Attendance", ":material/fact_check:", "my-attendance"),
    ("payments", _payment_history, "Payment History", ":material/credit_card:", "payment-history"),
    ("quiz", _quiz, "Fitness Quiz", ":material/emoji_events:", "fitness-quiz"),
    ("feedback", _feedback, "Feedback", ":material/forum:", "feedback"),
]

_ROLES = {"Admin": _ADMIN, "Team": _TEAM, "Member": _MEMBER}

# footer layout: which pages appear under which heading, per role
_FOOTER = {
    "Admin": {
        "plan_page": "renew",
        "GYM": ["all", "search", "renew", "payments"],
        "ACCOUNT": ["add_staff", "edit_staff", "reports", "feedback"],
    },
    "Team": {
        "plan_page": "renew",
        "GYM": ["search", "edit", "attendance", "renew"],
        "ACCOUNT": ["feedback"],
    },
    "Member": {
        "plan_page": "membership",
        "GYM": ["attendance", "payments", "quiz"],
        "ACCOUNT": ["profile", "membership", "feedback"],
    },
}


def build_pages(role):
    """Return (list of st.Page in menu order, dict key -> st.Page). Unknown roles get no pages."""
    spec = _ROLES.get(role, [])
    pages = {}
    ordered = []
    for i, (key, fn, title, icon, path) in enumerate(spec):
        page = st.Page(fn, title=title, icon=icon, url_path=path, default=(i == 0))
        pages[key] = page
        ordered.append(page)
    return ordered, pages


def all_url_paths():
    """Every page address used by any role (e.g. "my-attendance"), without the home page."""
    return sorted({path for spec in _ROLES.values() for (_, _, _, _, path) in spec if path})


def footer_layout(role):
    return _FOOTER[role]
