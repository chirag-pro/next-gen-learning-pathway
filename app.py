"""
app.py — NGLP Main Entry Point with Back Navigation support.
Run: streamlit run app.py
"""
import os
import streamlit as st

st.set_page_config(
    page_title="NGLP — Learning Pathway",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

from modules.auth import (
    authenticate_user, register_user, is_logged_in, login, logout, get_user_info
)

# ── Navigation history for back button ────────────────────────────────────────

def navigate_to(page):
    """Navigate to a page and push current page onto history stack."""
    current = st.session_state.get("page", "dashboard")
    history = st.session_state.get("page_history", [])
    if current != page:
        history.append(current)
    st.session_state.page_history = history[-10:]  # keep last 10
    st.session_state.page = page
    st.rerun()


def go_back():
    """Go back to the previous page."""
    history = st.session_state.get("page_history", [])
    if history:
        prev = history.pop()
        st.session_state.page_history = history
        st.session_state.page = prev
    else:
        st.session_state.page = "dashboard"
    st.rerun()


# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #F4F6FB; }

input[type="text"], input[type="password"], .stTextInput input, textarea {
    background: #FFFFFF !important; color: #111827 !important;
    border: 2px solid #E5E7EB !important; border-radius: 10px !important;
    font-size: 0.95rem !important; padding: 10px 14px !important;
}
.stSelectbox > div > div {
    background: #FFFFFF !important; color: #111827 !important;
    border: 2px solid #E5E7EB !important; border-radius: 10px !important;
}
.stButton > button[kind="primary"] {
    background: #6366F1 !important; color: #FFFFFF !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
    padding: 0.6rem 1.4rem !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.3) !important;
    transition: all 0.18s !important;
}
.stButton > button[kind="primary"]:hover {
    background: #4F46E5 !important; transform: translateY(-2px) !important;
    box-shadow: 0 8px 22px rgba(99,102,241,0.4) !important;
}
.stButton > button {
    border-radius: 10px !important; font-weight: 600 !important;
    font-size: 0.9rem !important; transition: all 0.16s !important;
    border: 2px solid #E5E7EB !important; color: #374151 !important;
    background: #FFFFFF !important;
}
.stButton > button:hover {
    border-color: #6366F1 !important; color: #6366F1 !important;
    transform: translateY(-1px) !important;
}
[data-testid="stSidebar"] { background: #1C1D2E !important; border-right: none !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; color: #9CA3AF !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.92rem !important;
    text-align: left !important; padding: 11px 14px !important;
    margin-bottom: 3px !important; width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99,102,241,0.18) !important; color: #FFFFFF !important;
    border: none !important; transform: none !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #6366F1 !important; color: #FFFFFF !important; border: none !important;
}
[data-testid="stSidebar"] * { color: #9CA3AF; }
.stForm { border: none !important; padding: 0 !important; background: transparent !important; }
[data-testid="stForm"] { border: none !important; }
.stTabs [data-baseweb="tab-list"] { background: #EAECF4; border-radius: 12px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 9px !important; font-weight: 600 !important; color: #6B7280 !important; padding: 8px 20px !important; }
.stTabs [aria-selected="true"] { background: #FFFFFF !important; color: #6366F1 !important; box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important; }
[data-testid="metric-container"] { background: #FFFFFF; border: 1.5px solid #E5E7EB; border-radius: 14px; padding: 16px 20px; }
[data-testid="metric-container"] label { color: #6B7280 !important; font-weight: 600 !important; font-size: 0.78rem !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { color: #111827 !important; font-weight: 800 !important; }
.stProgress > div > div > div { background: #6366F1 !important; border-radius: 99px !important; }
.stProgress > div > div { background: #E5E7EB !important; border-radius: 99px !important; }
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1.5px solid #E5E7EB; }
.stInfo, .stSuccess, .stWarning, .stError { border-radius: 10px !important; border-left-width: 4px !important; }
details > summary { background: #FFFFFF !important; border-radius: 10px !important; border: 1.5px solid #E5E7EB !important; padding: 12px 16px !important; font-weight: 600 !important; color: #374151 !important; }
</style>
""", unsafe_allow_html=True)


# ─── Login page ───────────────────────────────────────────────────────────────

def render_login_page():
    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.markdown("""
        <div style="text-align:center;padding:40px 0 32px;">
            <div style="font-size:3.2rem;">🎓</div>
            <h1 style="font-size:1.85rem;font-weight:900;color:#111827;margin:10px 0 4px;">
                Next Gen Learning Pathway
            </h1>
            <p style="color:#6B7280;font-size:0.95rem;margin:0;">
                Your personalised AI roadmap to mastery
            </p>
        </div>""", unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["  Sign In  ", "  Create Account  "])
        with tab_login:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                uname = st.text_input("Username", placeholder="Enter your username")
                pwd   = st.text_input("Password", type="password", placeholder="Enter your password")
                if st.form_submit_button("Sign In →", type="primary", use_container_width=True):
                    if not uname.strip() or not pwd:
                        st.error("Enter both username and password.")
                    elif authenticate_user(uname.strip(), pwd):
                        login(uname.strip())
                        st.rerun()
                    else:
                        st.error("Wrong username or password.")
        with tab_reg:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            with st.form("register_form"):
                r_u = st.text_input("Username", placeholder="Min 3 characters", key="ru")
                r_e = st.text_input("Email (optional)", placeholder="you@email.com", key="re")
                r_p = st.text_input("Password", type="password", placeholder="Min 6 characters", key="rp")
                r_c = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="rc")
                if st.form_submit_button("Create Account →", type="primary", use_container_width=True):
                    if r_p != r_c:
                        st.error("Passwords don't match.")
                    else:
                        ok, msg = register_user(r_u, r_p, r_e)
                        st.success(msg) if ok else st.error(msg)
                        if ok:
                            st.info("Account created — now sign in!")


# ─── Sidebar ─────────────────────────────────────────────────────────────────

def render_sidebar():
    username  = st.session_state.get("username", "")
    user_info = get_user_info(username)
    skill     = user_info.get("current_skill") or "Not set"
    level     = user_info.get("current_level") or ""
    api_ok    = bool(os.environ.get("GROQ_API_KEY", ""))
    cur_page  = st.session_state.get("page", "dashboard")
    history   = st.session_state.get("page_history", [])

    with st.sidebar:
        st.markdown("""
        <div style="padding:24px 16px 20px;border-bottom:1px solid #2D2E42;">
            <div style="font-size:1.5rem;font-weight:900;color:#FFFFFF;letter-spacing:-0.5px;">
                🎓 NGLP
            </div>
            <div style="font-size:0.7rem;color:#4B5563;margin-top:3px;letter-spacing:0.5px;">
                NEXT GEN LEARNING PATHWAY
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        # ── Back button (only show if there's history) ─────────────────────
        if history:
            prev_page = history[-1]
            prev_labels = {
                "dashboard":"Dashboard","roadmap":"Roadmap",
                "chatbot":"AI Mentor","progress":"Progress"
            }
            prev_label = prev_labels.get(prev_page, prev_page.title())
            if st.button(f"← Back to {prev_label}", key="back_btn",
                         use_container_width=True):
                go_back()

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── User card ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="background:#2A2B3D;border-radius:12px;padding:14px 16px;
                    margin-bottom:20px;">
            <div style="color:#FFFFFF;font-weight:700;font-size:0.95rem;">
                👤 {username}
            </div>
            <div style="color:#6B7280;font-size:0.8rem;margin-top:4px;">
                {"📗 " + skill if skill != "Not set" else "No skill selected"}
                {"  ·  " + level if level else ""}
            </div>
        </div>""", unsafe_allow_html=True)

        # ── Nav ────────────────────────────────────────────────────────────
        pages = [
            ("dashboard","🏠","Dashboard"),
            ("roadmap","🗺","My Roadmap"),
            ("chatbot","🤖","AI Mentor"),
            ("progress","📈","Progress"),
        ]
        for key, ico, label in pages:
            is_active = cur_page == key
            if is_active:
                if st.button(f"{ico}  {label}", key=f"nav_{key}",
                             type="primary", use_container_width=True):
                    pass  # already on this page
            else:
                if st.button(f"{ico}  {label}", key=f"nav_{key}",
                             use_container_width=True):
                    navigate_to(key)

        st.markdown(
            "<div style='height:16px;border-top:1px solid #2D2E42;margin-top:12px;'></div>",
            unsafe_allow_html=True)

        dot   = "🟢" if api_ok else "🟡"
        txt   = "Groq AI Active" if api_ok else "Offline Mode"
        st.markdown(
            f"<div style='font-size:0.78rem;color:#4B5563;padding:6px 4px 10px;'>"
            f"{dot} {txt}</div>",
            unsafe_allow_html=True)

        if st.button("🚪  Sign Out", key="signout", use_container_width=True):
            logout()
            st.rerun()


# ─── Router ───────────────────────────────────────────────────────────────────

def main():
    if not is_logged_in():
        render_login_page()
        return

    # Initialise history stack
    if "page_history" not in st.session_state:
        st.session_state.page_history = []

    render_sidebar()
    page = st.session_state.get("page", "dashboard")

    if page == "dashboard":
        from pages.dashboard import render; render()
    elif page == "roadmap":
        from pages.roadmap import render; render()
    elif page == "chatbot":
        from pages.chatbot_page import render; render()
    elif page == "progress":
        from pages.progress import render; render()
    else:
        st.session_state.page = "dashboard"; st.rerun()


if __name__ == "__main__":
    main()
