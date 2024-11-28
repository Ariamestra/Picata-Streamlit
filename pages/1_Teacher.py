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

# ----------- Teacher Portal Functions -----------------
def select_course(canvas):
    past_courses = []
    current_courses = []
    current_date = datetime.now()
    for course in canvas.get_courses():
        try:
            # Check for start and end dates
            start_date = datetime.strptime(course.start_at, '%Y-%m-%dT%H:%M:%SZ') if hasattr(course, 'start_at') and course.start_at else None
            end_date = datetime.strptime(course.end_at, '%Y-%m-%dT%H:%M:%SZ') if hasattr(course, 'end_at') and course.end_at else None
            # Attempt to get the course name from several attributes
            course_name = getattr(course, 'name', None) or getattr(course, 'course_code', None) or getattr(course, 'sis_course_id', 'Unknown Course')
            if end_date and current_date > end_date:
                past_courses.append((course, course_name))
            elif not end_date or current_date <= end_date:
                current_courses.append((course, course_name))
        except Exception as e:
            st.write(f"Error processing course: {e}")
    # Layout with two columns for current and past courses buttons
    current_col, past_col = st.columns(2)
    with current_col:
        current_courses_button = st.button("Current Courses", key="current_courses")
    with past_col:
        past_courses_button = st.button("Past Courses", key="past_courses")
    # Update session state based on button clicks
    if current_courses_button:
        st.session_state.current_courses_clicked = True
        st.session_state.past_courses_clicked = False
    elif past_courses_button:
        st.session_state.past_courses_clicked = True
        st.session_state.current_courses_clicked = False
    selected_course = None
    selected_quiz = None  
    if st.session_state.get("current_courses_clicked"):
        filtered_current_courses = [(course, name) for course, name in current_courses if name != "Unknown Course"]
        course_options = [name for _, name in filtered_current_courses]
       
        selected_course_name = st.selectbox("Select a Current Course:", course_options, index=None, key="course_selectbox")
        selected_course = next((course for course, name in filtered_current_courses if name == selected_course_name), None)
        # Quiz selection
        if selected_course:
            quizzes = selected_course.get_quizzes()
            quiz_options = [quiz.title for quiz in quizzes]
            selected_quiz_title = st.selectbox("Select a Quiz:", quiz_options, index=None, key="quiz_selectbox")
            selected_quiz = next((quiz for quiz in quizzes if quiz.title == selected_quiz_title), None)
        if selected_quiz:
            st.write(f"Selected Quiz: {selected_quiz.title}")
            students = selected_course.get_users(enrollment_type=['student'])
            attendance = {}
            # Display each student 
            st.write("### Mark Attendance")
            
            
            col1, col2 = st.columns(2)
            for idx, student in enumerate(students):
                # Alternate between columns
                if idx % 2 == 0:
                    with col1:
                        attendance_status = st.radio(
                            f"{student.name}",
                            options=["Here", "Absent"],
                            index=1,  # Default to "Absent"
                            key=f"attendance_{student.id}"
                        )
                else:
                    with col2:
                        attendance_status = st.radio(
                            f"{student.name}",
                            options=["Here", "Absent"],
                            index=1,  # Default to "Absent"
                            key=f"attendance_{student.id}"
                        )
                
                attendance[student.name] = attendance_status
        if st.button("Submit Attendance"):
            attendance_data = [{"Student Name": student_name, "Status": status} for student_name, status in attendance.items()]
            attendance_df = pd.DataFrame(attendance_data)
            st.write("### Attendance Record")
            st.table(attendance_df)
                
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
            
def create_partners(canvas):
    st.write("Create partners for quizzes.")
    selected_course = select_course(canvas)
    
    if selected_course:
        st.write(f"You selected the course: {selected_course.name}")
# ----------- Teacher Portal -----------------
selected = "Teacher" 
if selected == "Teacher":
    st.title(f"Welcome to the {selected} Portal")
    # Initialize button click states in session state if not already set
    for state_key in [
        "create_partners_clicked",
        "view_grade_clicked",
        "add_points_clicked",
        "current_courses_clicked",
        "past_courses_clicked"
    ]:
        if state_key not in st.session_state:
            st.session_state[state_key] = False
    # Layout the main buttons in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        create_partners_button = st.button("Create Partners", key="create_partners")
    
    with col2:
        view_grade_button = st.button("View Grade", key="view_grade")
        
    with col3:
        add_points_button = st.button("Add Points", key="add_points")
    
    # Update session state and call functions based on button clicks
    if create_partners_button:
        st.session_state.create_partners_clicked = True
    if view_grade_button:
        st.session_state.view_grade_clicked = True
    if add_points_button:
        st.session_state.add_points_clicked = True
    # Display additional components based on session state
    if st.session_state.create_partners_clicked:
        create_partners(canvas)
        
    if st.session_state.view_grade_clicked:
        st.write("Grade viewing functionality triggered.")  
    
    if st.session_state.add_points_clicked:
        st.write("Add points functionality triggered.")
