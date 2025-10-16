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

    # ===========================================
    # 🧾 Redesigned Attendance Card Section
    # ===========================================
    st.markdown(
        """
        <style>
        .attendance-card {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            text-align: center;
            margin-bottom: 30px;
        }
        .attendance-header {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }
        .attendance-info {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        .info-box {
            background-color: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 15px 25px;
            margin: 10px;
            width: 180px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }
        .info-value {
            font-size: 24px;
            font-weight: bold;
            color: #00E676;
        }
        .info-label {
            font-size: 14px;
            opacity: 0.8;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    percent = student['Percent'].values[0] if 'Percent' in df.columns else None
    total_classes = student['Total'].values[0] if 'Total' in df.columns else None
    attended_classes = (percent / 100) * total_classes if (percent is not None and total_classes is not None) else None

    st.markdown(
        f"""
        <div class="attendance-card">
            <div class="attendance-header">📘 Your Attendance Record</div>
            <div class="attendance-info">
                <div class="info-box">
                    <div class="info-value">{percent:.2f}%</div>
                    <div class="info-label">Attendance %</div>
                </div>
                <div class="info-box">
                    <div class="info-value">{attended_classes:.0f}</div>
                    <div class="info-label">Classes Attended</div>
                </div>
                <div class="info-box">
                    <div class="info-value">{total_classes}</div>
                    <div class="info-label">Total Classes</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ===========================================
    # 🌈 Attendance Progress Bar
    # ===========================================
    st.subheader("📈 Attendance Progress Towards 75% Goal")
    if percent is not None:
        progress = percent / 75
        progress = min(progress, 1.0)
        color = "#FF4B4B" if percent < 60 else "#FFD700" if percent < 75 else "#00C853"

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

        if percent < 75 and total_classes is not None:
            st.error("⚠️ You are at risk of DETENTION!")
            required_percent = 75
            if attended_classes is not None:
                needed_classes = (required_percent/100 * total_classes - attended_classes) / (1 - required_percent/100)
                needed_classes = int(np.ceil(max(0, needed_classes)))
                st.info(f"📅 You need to attend **{needed_classes}** more consecutive classes to reach 75%.")
        else:
            st.success("✅ You are maintaining safe attendance.")
    else:
        st.warning("Column 'Percent' not found in CSV.")

    # ===========================================
    # 📊 Subject-wise Chart
    # ===========================================
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
