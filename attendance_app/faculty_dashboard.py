import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# -------------------------
# Helper function for readable text color
# -------------------------
def readable_text_color(bg_color):
    """
    Returns 'black' or 'white' based on background brightness
    """
    bg_color = bg_color.lstrip('#')
    r, g, b = int(bg_color[:2], 16), int(bg_color[2:4], 16), int(bg_color[4:], 16)
    brightness = (r*299 + g*587 + b*114) / 1000
    return 'black' if brightness > 125 else 'white'

# Page config
st.set_page_config(
    page_title="Faculty Dashboard",
    page_icon="👩‍🏫",
    layout="wide"
)

def faculty_dashboard(username=None):
    st.markdown("<h1 style='text-align:center;color:#4B0082;'>👩‍🏫 Faculty Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("---")

    data_file = "data/faculty_attendance_20days.csv"

    # -----------------------------
    # Upload CSV
    # -----------------------------
    with st.expander("📤 Upload Attendance CSV", expanded=False):
        uploaded = st.file_uploader("Upload CSV File", type=['csv'])
        if uploaded is not None:
            df = pd.read_csv(uploaded)
            os.makedirs("data", exist_ok=True)
            df.to_csv(data_file, index=False)
            st.success("✅ Attendance data uploaded successfully!")

    if not os.path.exists(data_file):
        st.warning("No attendance file found. Please upload one.")
        return

    # -----------------------------
    # Load CSV
    # -----------------------------
    df = pd.read_csv(data_file)
    df.columns = df.columns.str.strip()

    st.subheader("📋 Attendance Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    # -----------------------------
    # Subject & Date Selection
    # -----------------------------
    subject_cols = [col for col in df.columns if col not in ['Date', 'Roll.No']]
    col1, col2 = st.columns(2)
    with col1:
        selected_subject = st.selectbox("📘 Select Subject", subject_cols)
    with col2:
        selected_date = st.selectbox("📅 Select Date", sorted(df['Date'].unique()))

    # -----------------------------
    # Students who bunked
    # -----------------------------
    st.markdown(f"### 🚫 Students Who Bunked {selected_subject} on {selected_date}")
    bunked = df[(df['Date'] == selected_date) & (df[selected_subject] == 'A')]
    if not bunked.empty:
        st.dataframe(bunked[['Roll.No', selected_subject]], use_container_width=True)
    else:
        st.success(f"✅ No one bunked {selected_subject} on {selected_date}!")

    # -----------------------------
    # Attendance summary
    # -----------------------------
    df['Classes_Attended'] = df[subject_cols].apply(lambda x: (x == 'P').sum(), axis=1)
    total_classes_per_day = len(subject_cols)
    total_classes = total_classes_per_day * df['Date'].nunique()

    student_summary = df.groupby('Roll.No')['Classes_Attended'].sum().reset_index()
    student_summary['Percent'] = (student_summary['Classes_Attended'] / total_classes) * 100
    student_summary['Detained'] = (student_summary['Percent'] < 75).astype(int)

    # -----------------------------
    # Attendance chart card
    # -----------------------------
    st.markdown("### 📊 Overall Attendance % per Student")
    fig, ax = plt.subplots(figsize=(14, 5))
    colors = ['#FF4B4B' if d else '#4CAF50' for d in student_summary['Detained']]
    ax.bar(student_summary['Roll.No'], student_summary['Percent'], color=colors, edgecolor='black')
    ax.set_ylabel("Attendance %")
    ax.set_xlabel("Roll.No")
    ax.set_ylim(0, 100)
    ax.set_title("Overall Attendance Percentage per Student")
    plt.xticks(rotation=90)
    st.pyplot(fig)

    # -----------------------------
    # Student Detention & Bunked Classes Card
    # -----------------------------
    st.markdown("### 🤖 Student Detention Risk & Bunked Classes")
    roll = st.text_input("Enter Roll No to Check Details:")

    if roll:
        if roll in student_summary['Roll.No'].values:
            percent = student_summary.loc[student_summary['Roll.No'] == roll, 'Percent'].values[0]
            detained = student_summary.loc[student_summary['Roll.No'] == roll, 'Detained'].values[0]

            # =========================
            # Metric cards with background & readable text
            # =========================
            col1, col2 = st.columns(2)

            bg_color1 = "#E0E0E0"
            text_color1 = readable_text_color(bg_color1)
            with col1:
                st.markdown(f"<div style='background-color:{bg_color1};padding:20px;border-radius:10px;text-align:center;'>"
                            f"<h3 style='color:{text_color1}'>Attendance %</h3>"
                            f"<h2 style='color:#4B0082;'>{percent:.2f}%</h2></div>", unsafe_allow_html=True)

            bg_color2 = "#FFCDD2" if detained else "#C8E6C9"
            text_color2 = readable_text_color(bg_color2)
            with col2:
                st.markdown(f"<div style='background-color:{bg_color2};padding:20px;border-radius:10px;text-align:center;'>"
                            f"<h3 style='color:{text_color2}'>Detention Risk</h3>"
                            f"<h2 style='color:{text_color2};'>{'⚠️ At Risk' if detained else '✅ Safe'}</h2></div>", unsafe_allow_html=True)

            # =========================
            # Bunked classes table
            # =========================
            st.markdown(f"#### 📌 Classes Bunked by {roll}")
            student_data = df[df['Roll.No'] == roll]
            bunked_classes = student_data.melt(id_vars=['Date', 'Roll.No'], value_vars=subject_cols,
                                               var_name='Subject', value_name='Status')
            bunked_classes = bunked_classes[bunked_classes['Status'] == 'A']
            if not bunked_classes.empty:
                st.dataframe(bunked_classes[['Date', 'Subject']], use_container_width=True)
            else:
                st.success("✅ Student has not bunked any classes!")
        else:
            st.warning("Roll number not found!")
