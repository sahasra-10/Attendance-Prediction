import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from helpers import read_attendance

def student_dashboard(username):
    st.header(f"🎓 Welcome, {username}")
    data_file = "data/attendance.csv"

    if not os.path.exists(data_file):
        st.warning("Attendance data not available yet.")
        return

    df = read_attendance(data_file)
    df.columns = df.columns.str.strip()

    if 'Roll.No' not in df.columns:
        st.error("CSV does not contain 'Roll.No' column.")
        return

    student = df[df['Roll.No'].astype(str) == str(username)]
    if student.empty:
        st.info("No records found for your roll number.")
        return

    st.subheader("📘 Your Attendance Record")
    st.dataframe(student.T)

    percent = student['Percent'].values[0] if 'Percent' in df.columns else None
    total_classes = student['Total'].values[0] if 'Total' in df.columns else None
    attended_classes = (percent / 100) * total_classes if (percent is not None and total_classes is not None) else None

    if percent is not None:
        st.metric("Your Attendance %", f"{percent:.2f}%")

        # ===============================
        # 🌈 Attendance Progress Bar
        # ===============================
        st.subheader("📈 Attendance Progress Towards 75% Goal")

        progress = percent / 75
        progress = min(progress, 1.0)  # cap at 100%

        # Choose color based on percentage
        if percent < 60:
            color = "#FF4B4B"  # red
        elif 60 <= percent < 75:
            color = "#FFD700"  # yellow
        else:
            color = "#00C853"  # green

        # Custom progress bar
        st.markdown(
            f"""
            <div style='background-color:#ddd; border-radius:20px; height:25px; width:100%;'>
                <div style='width:{percent}%; background-color:{color};
                            height:25px; border-radius:20px; text-align:center;
                            color:white; font-weight:bold;'>
                    {percent:.2f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ===============================
        # ⚠️ Detention Risk Calculation
        # ===============================
        if percent < 75 and total_classes is not None:
            st.error("⚠️ You are at risk of DETENTION!")

            # Calculate required extra classes
            required_percent = 75
            if attended_classes is not None:
                needed_classes = (required_percent/100 * total_classes - attended_classes) / (1 - required_percent/100)
                needed_classes = int(np.ceil(max(0, needed_classes)))
                st.info(f"📅 You need to attend **{needed_classes}** more consecutive classes to reach 75%.")
        else:
            st.success("✅ You are maintaining safe attendance.")
    else:
        st.warning("Column 'Percent' not found in CSV.")

    # ===============================
    # 📊 Subject-wise Interactive Chart
    # ===============================
    st.subheader("📊 Subject-wise Attendance Comparison")
    exclude_cols = ['Sl.No', 'Roll.No', 'Total', 'Percent']
    subject_cols = [col for col in df.columns if col not in exclude_cols]

    if subject_cols:
        subject_data = student[subject_cols].select_dtypes(include=[np.number]).iloc[0]
        subject_df = pd.DataFrame({
            'Subject': subject_data.index,
            'Attendance': subject_data.values
        })

        fig = px.bar(
            subject_df,
            x='Subject',
            y='Attendance',
            text='Attendance',
            color='Attendance',
            color_continuous_scale='Bluered',
            labels={'Attendance': 'Marks / Percentage'},
            title="Subject-wise Attendance Performance"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, yaxis_range=[0, 100])

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No numeric subject columns found in CSV.")

