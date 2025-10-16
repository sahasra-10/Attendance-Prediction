import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
import os
from helpers import read_attendance

def faculty_dashboard(username=None):
    st.header("👩‍🏫 Faculty Dashboard")

    # -----------------------------
    # Paths to dataset in project folder
    # -----------------------------
    data_file = "data/attendance.csv"        # Summary attendance
    daily_file = "data/daily_attendance.csv"  # Daily attendance

    # -----------------------------
    # Load Summary Attendance
    # -----------------------------
    if os.path.exists(data_file):
        df_summary = read_attendance(data_file)
        df_summary.columns = df_summary.columns.str.strip()
        st.subheader("📋 Summary Attendance Preview")
        st.dataframe(df_summary.head())

        # Attendance Analytics
        if 'Percent' in df_summary.columns:
            st.subheader("📊 Attendance Analytics")
            fig, ax = plt.subplots()
            ax.hist(df_summary['Percent'], bins=10, edgecolor='black')
            ax.set_xlabel("Attendance Percentage")
            ax.set_ylabel("Number of Students")
            ax.set_title("Distribution of Attendance %")
            st.pyplot(fig)

            avg_percent = df_summary['Percent'].mean()
            st.metric("Average Attendance (%)", f"{avg_percent:.2f}")
        else:
            st.warning("Column 'Percent' not found in summary CSV.")

        # Detention Prediction
        if 'Roll.No' in df_summary.columns and 'Percent' in df_summary.columns:
            st.subheader("🤖 Detention Prediction")
            df_summary['Detained'] = (df_summary['Percent'] < 75).astype(int)
            X = df_summary[['Percent']]
            y = df_summary['Detained']
            model = LogisticRegression()
            model.fit(X, y)

            roll = st.text_input("Enter Roll No to Predict Detention Risk:", key="faculty_roll")
            if roll:
                roll = str(roll)
                if roll in df_summary['Roll.No'].astype(str).values:
                    percent = df_summary[df_summary['Roll.No'].astype(str) == roll]['Percent'].values[0]
                    pred = model.predict([[percent]])[0]
                    if pred == 1:
                        st.error(f"⚠️ Student {roll} is at risk of DETENTION!")
                    else:
                        st.success(f"✅ Student {roll} is SAFE from detention.")
                else:
                    st.warning("Roll number not found!")
        else:
            st.warning("Columns 'Roll.No' or 'Percent' not found. Cannot predict detention.")
    else:
        st.warning("Place a summary attendance CSV at `data/attendance.csv` to see analytics and predictions.")

    # -----------------------------
    # Track Daily Absentees
    # -----------------------------
    if os.path.exists(daily_file):
        st.subheader("📆 Daily Absentees Tracker")
        df_daily = pd.read_csv(daily_file)
        df_daily.columns = df_daily.columns.str.strip()

        unique_dates = df_daily['Date'].unique()
        selected_date = st.selectbox("Select Date", unique_dates)
        unique_classes = df_daily['Class'].unique()
        selected_class = st.selectbox("Select Class", unique_classes)

        df_filtered = df_daily[
            (df_daily['Date'] == selected_date) &
            (df_daily['Class'] == selected_class) &
            (df_daily['Status'] == 'A')
        ]
        st.write(f"Students absent in **{selected_class}** on **{selected_date}**:")
        if not df_filtered.empty:
            st.dataframe(df_filtered[['Roll.No', 'Class', 'Status']])
        else:
            st.success("No students were absent in this class on this date.")
    else:
        st.info("Place a daily attendance CSV at `data/daily_attendance.csv` to track absentees per class.")
