import sys
from pathlib import Path

import streamlit as st


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PAGES_DIR = PROJECT_ROOT / "pages"


# --------------------------------------------------
# Streamlit configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# Page definitions
# --------------------------------------------------

PAGES = {
    "Home": "01_home.py",
    "Company Profile": "02_profile.py",
    "Screener": "03_screener.py",
    "Peer Comparison": "04_peers.py",
    "Trend Analysis": "05_trends.py",
    "Sector Analysis": "06_sectors.py",
    "Capital Allocation": "07_capital.py",
    "Annual Reports": "08_reports.py",
}


# --------------------------------------------------
# Sidebar navigation
# --------------------------------------------------

st.sidebar.title("Navigation")

selected_page = st.sidebar.radio(
    "Go to",
    list(PAGES.keys()),
)


# --------------------------------------------------
# Load selected page
# --------------------------------------------------

page_file = PAGES_DIR / PAGES[selected_page]

if page_file.exists():
    with open(page_file, "r", encoding="utf-8") as file:
        code = compile(
            file.read(),
            str(page_file),
            "exec",
        )

    exec(code, {"__file__": str(page_file)})

else:
    st.error(
        f"Page file not found:\n\n{page_file}"
    )