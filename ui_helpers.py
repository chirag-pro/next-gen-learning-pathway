"""UI Helpers – Custom CSS, sidebar navigation, reusable components."""

import streamlit as st


PAGES = [
    ("🏠 Dashboard",     "Overview of your learning journey"),
    ("🗺️ My Roadmap",    "View your current learning phases"),
    ("⚡ Generate Path",  "Create a personalised study plan"),
    ("🤖 AI Chatbot",    "24/7 learning assistant"),
    ("📚 Resources",     "Books, docs, courses & more"),
    ("📈 Progress",      "Charts & analytics"),
    ("👤 Profile",       "Your account & achievements"),
]


def apply_custom_css():
    st.markdown("""
    <style>
    /* ── Global ── */
    html, body, [class*="st-"] { font-family: 'Segoe UI', system-ui, sans-serif; }
    .main .block-container { padding: 1.5rem 2rem; max-width: 1100px; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] { background: #111827 !important; border-right: 1px solid #1f2937; }
    [data-testid="stSidebar"] .css-1d391kg { padding: 0; }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: #141c2e; border: 1px solid #1f2937;
        border-radius: 12px; padding: 1rem;
    }
    [data-testid="metric-container"] label { color: #9ca3af !important; font-size: 0.75rem; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1.8rem !important; color: #e8eaf0 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.75rem; }

    /* ── Buttons ── */
    .stButton > button {
        background: #4f8ef7; color: #fff; border: none;
        border-radius: 8px; font-weight: 600; transition: all 0.2s;
    }
    .stButton > button:hover { background: #3b7de8; transform: translateY(-1px); }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: #141c2e !important; border: 1px solid #1f2937 !important;
        border-radius: 8px !important; color: #e8eaf0 !important;
    }

    /* ── Text input ── */
    .stTextInput > div > div > input, .stSelectbox > div > div {
        background: #1a2234 !important; border: 1px solid #2a3550 !important;
        color: #e8eaf0 !important; border-radius: 8px;
    }

    /* ── Progress bar ── */
    .stProgress > div > div > div { background: #4f8ef7 !important; border-radius: 4px; }
    .stProgress > div > div { background: #1f2937 !important; border-radius: 4px; }

    /* ── Hide Streamlit branding ── */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }

    /* ── Custom card ── */
    .nglp-card {
        background: #141c2e; border: 1px solid #1f2937;
        border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem;
    }
    .nglp-tag {
        display: inline-block; padding: 2px 10px; border-radius: 20px;
        font-size: 0.7rem; font-weight: 700; margin: 2px;
    }
    .tag-green  { background: rgba(16,185,129,0.15); color: #10b981; }
    .tag-blue   { background: rgba(79,142,247,0.15); color: #4f8ef7; }
    .tag-amber  { background: rgba(245,158,11,0.15); color: #f59e0b; }
    .tag-purple { background: rgba(167,139,250,0.15);color: #a78bfa; }
    .tag-red    { background: rgba(239,68,68,0.15);  color: #ef4444; }

    /* ── Chat bubbles ── */
    .chat-bot  { background:#1e2840; border-radius:0 16px 16px 16px; padding:12px 16px; margin:6px 0; max-width:80%; border:1px solid #2a3550; }
    .chat-user { background:linear-gradient(135deg,#4f8ef7,#7c3aed); border-radius:16px 0 16px 16px; padding:12px 16px; margin:6px 0 6px auto; max-width:80%; color:#fff; }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar(user: dict | None) -> str:
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style='padding:16px 12px 12px; border-bottom:1px solid #1f2937; margin-bottom:12px'>
            <div style='font-size:2rem; margin-bottom:4px'>🧠</div>
            <div style='font-size:0.85rem; font-weight:700; color:#e8eaf0'>NGLP System</div>
            <div style='font-size:0.65rem; color:#6b7280'>Next Gen Learning Pathway</div>
        </div>
        """, unsafe_allow_html=True)

        # User card
        if user:
            xp     = user.get("xp", 0)
            streak = user.get("streak", 0)
            level  = "🥉 Rookie" if xp < 100 else "🥈 Learner" if xp < 300 else "🥇 Pro" if xp < 600 else "💎 Expert"
            st.markdown(f"""
            <div style='background:#1a2234;border:1px solid #2a3550;border-radius:10px;padding:10px 12px;margin-bottom:12px'>
                <div style='font-size:0.8rem; font-weight:700; color:#e8eaf0'>{user.get("name","")}</div>
                <div style='font-size:0.65rem; color:#9ca3af; margin-top:2px'>{user.get("field","")}</div>
                <div style='display:flex;gap:10px;margin-top:8px'>
                    <div style='font-size:0.65rem;color:#f59e0b'>🔥 {streak}d streak</div>
                    <div style='font-size:0.65rem;color:#a78bfa'>⭐ {xp} XP</div>
                    <div style='font-size:0.65rem;color:#10b981'>{level}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Navigation
        selected = st.session_state.get("page", "🏠 Dashboard")
        for page_name, _ in PAGES:
            active = page_name == selected
            if st.button(
                page_name,
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                selected = page_name
                st.session_state.page = page_name

        # Logout
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.messages = []
            st.rerun()

    return selected


def render_header(title: str, subtitle: str):
    st.markdown(f"""
    <div style='margin-bottom:1.5rem'>
        <h1 style='font-size:1.6rem; color:#e8eaf0; margin:0'>{title}</h1>
        <p style='color:#9ca3af; font-size:0.85rem; margin-top:4px'>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def card(content_fn, title: str = ""):
    """Render content inside a styled card."""
    with st.container():
        st.markdown(f"<div class='nglp-card'>", unsafe_allow_html=True)
        if title:
            st.markdown(f"**{title}**")
        content_fn()
        st.markdown("</div>", unsafe_allow_html=True)


def tag(label: str, color: str = "blue") -> str:
    return f"<span class='nglp-tag tag-{color}'>{label}</span>"
