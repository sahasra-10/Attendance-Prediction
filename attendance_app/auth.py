import streamlit as st
import pandas as pd
import os
from helpers import hash_password, check_login, read_attendance

def login(users_df):
    st.subheader("🔑 Login")
    st.caption("👉 Students use your Roll.No (e.g., 23E51A6601). Faculty can use your registered username.")

    username = st.text_input("Roll No / Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        role = check_login(username, password, users_df)

        if not role:
            st.error("Invalid username or password.")
            return

        # ===========================
        # Student Login Validation
        # ===========================
        if role == 'student':
            data_file = 'data/attendance.csv'
            if os.path.exists(data_file):
                try:
                    df = read_attendance(data_file)
                    rolls = df['Roll.No'].astype(str).str.strip().values
                except Exception:
                    rolls = []

                if str(username).strip() not in rolls:
                    st.warning("Your Roll.No is not found in the attendance records.")
                    st.info("Make sure you use your correct Roll.No (e.g., 23E51A6601).")
                    if len(rolls) > 0:
                        st.caption("Here are a few valid Roll.No examples:")
                        st.write(list(rolls[:10]))
                    return
            else:
                st.warning("⚠️ No attendance data found yet. Contact your faculty.")

        # ===========================
        # Faculty Login (No restriction)
        # ===========================
        elif role == 'faculty':
            st.success("✅ Faculty login successful!")

        # ===========================
        # Set session state and rerun
        # ===========================
        st.session_state['logged_in'] = True
        st.session_state['username'] = str(username)
        st.session_state['role'] = role
        st.session_state['dashboard'] = role
        st.success(f"Welcome {username} ({role.title()})!")

        try:
            st.experimental_rerun()
        except Exception:
            pass


def register(users_file):
    st.subheader("📝 Register New Account")
    st.caption("👉 Students must enter Roll.No as username. Faculty can use any unique ID.")

    username = st.text_input("Roll No / Username", key="reg_user")
    password = st.text_input("Password", type="password", key="reg_pass")
    role = st.selectbox("Role", ["student", "faculty"], key="reg_role")

    if st.button("Register"):
        hashed = hash_password(password)
        df = pd.read_csv(users_file)

        if username in df['username'].astype(str).values:
            st.error("Username already exists!")
        else:
            new_user = pd.DataFrame([[str(username), hashed, role]], columns=['username','password','role'])
            df = pd.concat([df, new_user], ignore_index=True)
            df.to_csv(users_file, index=False)
            st.success("✅ Registration successful! Please login.")
