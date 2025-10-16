import streamlit as st
import os
import pandas as pd
from auth import login, register
from student_dashboard import student_dashboard
from faculty_dashboard import faculty_dashboard

# ===========================
# Setup Directories & Files
# ===========================
os.makedirs("auth", exist_ok=True)
os.makedirs("data", exist_ok=True)

users_file = "auth/users.csv"
if not os.path.exists(users_file):
    pd.DataFrame(columns=['username', 'password', 'role']).to_csv(users_file, index=False)

users_df = pd.read_csv(users_file)

# ===========================
# Initialize Session State
# ===========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "dashboard" not in st.session_state:
    st.session_state.dashboard = None

# ===========================
# Page Setup
# ===========================
st.set_page_config(page_title="AI Attendance System", page_icon="🎯", layout="wide")
st.title("🎯 AI-Based Attendance & Detention Prediction System")

# ===========================
# Debug / Session State
# ===========================
with st.sidebar.expander("Debug / Session State", expanded=False):
    if st.checkbox("Show session_state", key="dbg_show_state"):
        st.json({k: v for k, v in st.session_state.items()})

# ===========================
# If Logged In → Show Dashboard
# ===========================
if st.session_state.logged_in and st.session_state.dashboard is not None:
    if st.session_state.dashboard == "faculty":
        faculty_dashboard(st.session_state.username)
    elif st.session_state.dashboard == "student":
        student_dashboard(st.session_state.username)

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.dashboard = None
        st.success("Logged out successfully.")
        try:
            st.experimental_rerun()  # fallback for older Streamlit
        except Exception:
            pass

# ===========================
# Else → Login or Register
# ===========================
else:
    choice = st.sidebar.radio("Menu", ["Login", "Register"])
    if choice == "Login":
        login(users_df)   # ✅ Pass DataFrame, not string path
    elif choice == "Register":
        register(users_file)
