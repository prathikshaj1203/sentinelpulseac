import streamlit as st
import os
def init_page(title, required_role=None):
    """
    Initializes a Streamlit page.
    1. Sets page config (must be first).
    2. Loads custom futuristic purple glow CSS.
    3. Checks authentication status.
    4. Enforces role access controls.
    5. Displays user profile in the sidebar.
    """
    # 1. Page Config
    st.set_page_config(
        page_title=title,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    load_css()
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Access Restricted. Please log in first.")
        st.stop()
    if required_role:
        allowed_roles = [required_role] if isinstance(required_role, str) else required_role
        allowed_roles_upper = [r.upper() for r in allowed_roles]
        if "role" not in st.session_state or st.session_state.role.upper() not in allowed_roles_upper:
            st.error("Access Denied. You do not have permissions to view this page.")
            st.stop()
            
    # Inject role-based CSS to restrict navigation access visually
    if "role" in st.session_state and st.session_state.role.upper() == "TECHNICIAN":
        st.markdown("""
        <style>
        /* Hide Home and Analytics from sidebar for Technicians */
        div[data-testid="stSidebarNav"] ul li a[href*="Home"],
        div[data-testid="stSidebarNav"] ul li a[href*="home"],
        div[data-testid="stSidebarNav"] ul li a[href*="Analytics"],
        div[data-testid="stSidebarNav"] ul li a[href*="analytics"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-profile">
            <h4 style="margin-top:0; color:#A855F7; border-bottom: 1px solid rgba(168, 85, 247, 0.2); padding-bottom:8px; margin-bottom:12px; font-weight:600;">USER PROFILE</h4>
            <div style="font-size: 14px; line-height: 1.6;">
                <div style="margin-bottom: 6px;"><b>{st.session_state.get('full_name', 'User')}</b></div>
                <div style="margin-bottom: 6px;">Role: <span class="badge-role">{st.session_state.get('role', 'N/A')}</span></div>
                <div>Dept: <span style="color:#C084FC;">{st.session_state.get('department', 'N/A')}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Logout", key="logout_btn"):
            for key in ["logged_in", "username", "role", "full_name", "department"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("Logged out successfully.")
            st.switch_page("Login.py")
def load_css():
    css_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "styles",
        "main.css"
    )
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
def page_header(title, subtitle):
    st.markdown(f"""
    <div style="margin-bottom: 30px;">
        <h1 class="main-title">{title}</h1>
        <p class="sub-title">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)
def metric_card(title, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)