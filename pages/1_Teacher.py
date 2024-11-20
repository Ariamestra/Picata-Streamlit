import streamlit as st
from datetime import datetime
from canvasapi import Canvas
import os
from canvasapi.exceptions import ResourceDoesNotExist
import pandas as pd

# ----------- Canvas Config -----------------

# Initializes the Canvas API.
def setup_canvas_api():
    API_URL = os.getenv("CANVAS_URL")
    API_KEY = os.getenv("CANVAS_TOKEN")
    if not (API_URL and API_KEY):
        raise Exception("'CANVAS_' environment variables not set - see installation instructions to resolve this")
    return Canvas(API_URL, API_KEY)

canvas = setup_canvas_api()

# ----------- Functions -----------------

# Get quizzes for a given course.
def get_course_quizzes(course):
    try:
        return course.get_quizzes()
    except ResourceDoesNotExist:
        st.error("Error: The selected course does not have quizzes or could not be found.")
        return []

# Organizes courses into past and current' based on their dates.
def organize_courses(courses):
    past_courses = []
    current_courses = []
    current_date = datetime.now()

    for course in courses:
        try:
            start_date = datetime.strptime(course.start_at, '%Y-%m-%dT%H:%M:%SZ') if course.start_at else None
            end_date = datetime.strptime(course.end_at, '%Y-%m-%dT%H:%M:%SZ') if course.end_at else None
            course_name = getattr(course, 'name', None) or getattr(course, 'course_code', None) or 'Unknown Course'

            if end_date and current_date > end_date:
                past_courses.append((course, course_name))
            elif not end_date or current_date <= end_date:
                current_courses.append((course, course_name))

        except Exception as e:
            st.error(f"Error processing course: {e}")

    return past_courses, current_courses

# Displays and handle attendance.
def mark_attendance(students, selected_quiz, selected_course):
    st.write("### Mark Attendance")
    col1, col2 = st.columns(2)
    attendance = {}

    for idx, student in enumerate(students):
        col = col1 if idx % 2 == 0 else col2
        with col:
            status = st.radio(
                f"{student.name}",
                options=["Here", "Absent"],
                index=1,  # Default is absent
                key=f"attendance_{student.id}"
            )
            attendance[student.name] = status

    if st.button("Submit Attendance"):
        attendance_data = [{"Student Name": name, "Status": status} for name, status in attendance.items()]
        attendance_df = pd.DataFrame(attendance_data)

        # Generate CSV
        quiz_title = selected_quiz.title if selected_quiz else "Quiz"
        class_name = selected_course.name if selected_course else "Class"
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{class_name}_{quiz_title}_attendance_{current_date}.csv".replace(" ", "_")

        # Display and download CSV
        st.write("### Attendance Record")
        st.table(attendance_df)
        st.download_button(
            label="Download Attendance as CSV",
            data=attendance_df.to_csv(index=False),
            file_name=file_name,
            mime="text/csv"
        )

# ----------- Teacher Portal -----------------

# Main function for the teacher portal.
def teacher_portal(canvas):
    st.title("Welcome to the Teacher Portal")

    # Initialize button states
    buttons = {
        "create_partners_clicked": False,
        "view_grade_clicked": False,
        "add_points_clicked": False,
        "current_courses_clicked": False,
        "past_courses_clicked": False
    }
    for key in buttons:
        if key not in st.session_state:
            st.session_state[key] = buttons[key]

    # Layout the main buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Create Partners"):
            st.session_state.create_partners_clicked = True
    with col2:
        if st.button("View Grades"):
            st.session_state.view_grade_clicked = True
    with col3:
        if st.button("Add Points"):
            st.session_state.add_points_clicked = True

    # Call functionality based on state
    if st.session_state.create_partners_clicked:
        create_partners(canvas)
    elif st.session_state.view_grade_clicked:
        st.write("Grade viewing functionality triggered.")
    elif st.session_state.add_points_clicked:
        st.write("Add points functionality triggered.")

# Functionality to create quiz partners.
def create_partners(canvas):
    st.write("Create partners for quizzes.")
    courses = canvas.get_courses()
    past_courses, current_courses = organize_courses(courses)

    current_col, past_col = st.columns(2)
    with current_col:
        if st.button("Current Courses"):
            st.session_state.current_courses_clicked = True
            st.session_state.past_courses_clicked = False
    with past_col:
        if st.button("Past Courses"):
            st.session_state.past_courses_clicked = True
            st.session_state.current_courses_clicked = False


# ----------- Main Application -----------------

if __name__ == "__main__":
    teacher_portal(canvas)
