"""Sample Sheet Tracker — Streamlit entry point."""
from __future__ import annotations

import streamlit as st

from ui.sidebar import inject_theme_css, render_sidebar
from ui.page_load import render_page_load
from ui.page_configure import render_page_configure
from ui.page_results import render_page_results
from ui.page_userguide import render_page_userguide


# ---------------------------------------------------------------------------
# Page config — must be the FIRST Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Sample Sheet Tracker",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session defaults
# ---------------------------------------------------------------------------
if "current_step" not in st.session_state:
    st.session_state["current_step"] = 1
if "theme" not in st.session_state:
    st.session_state["theme"] = "Light"
if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = "Wizard"

# ---------------------------------------------------------------------------
# Inject theme CSS + render sidebar
# ---------------------------------------------------------------------------
inject_theme_css()
render_sidebar()

# ---------------------------------------------------------------------------
# Top-level tab navigation
# ---------------------------------------------------------------------------
tab_app, tab_guide = st.tabs(["Main App", "User Guide"])

with tab_app:
    app_mode = st.session_state.get("app_mode", "Wizard")
    if app_mode == "Expert":
        render_page_results(expert_mode=True)
    else:
        step = st.session_state.get("current_step", 1)
        if step == 1:
            render_page_load()
        elif step == 2:
            render_page_configure()
        elif step == 3:
            render_page_results()
        else:
            st.error(f"Unknown step: {step}. Click 'Start Over' to reset.")

with tab_guide:
    render_page_userguide()
