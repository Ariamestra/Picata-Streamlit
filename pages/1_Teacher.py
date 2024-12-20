import os
import streamlit as st
from datetime import datetime
from canvasapi import Canvas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class CanvasPortal:
    """
    Initialize the Canvas API setup
    """
    def __init__(self):
        self.canvas = self.setup_canvas_api()
        self.initialize_session_state()

    @staticmethod
    def setup_canvas_api():
        API_URL = os.getenv("CANVAS_URL")
        API_KEY = os.getenv("CANVAS_TOKEN")
        if not (API_URL and API_KEY):
            raise Exception("'CANVAS_' environment variables not set - see installation instructions to resolve this")
        return Canvas(API_URL, API_KEY)

    def initialize_session_state(self):
        """
        Initialize session states for tracking UI states
        """
        default_states = [
            "create_partners_clicked",
            "view_grade_clicked",
            "add_points_clicked",
            "current_courses_clicked",
            "past_courses_clicked"
        ]
        for state_key in default_states:
            if state_key not in st.session_state:
                st.session_state[state_key] = False

    def run_teacher_portal(self):
        """
        Main method to run the teacher portal 
        """
        st.title("Welcome to the Teacher Portal")
        
        # Create columns for main action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            create_partners_button = st.button("Create Partners", key="create_partners")
        
        with col2:
            view_grade_button = st.button("View Grade", key="view_grade")
        
        with col3:
            add_points_button = st.button("Add Points", key="add_points")
        
        # Update session state based on button clicks
        if create_partners_button:
            st.session_state.create_partners_clicked = True
        if view_grade_button:
            st.session_state.view_grade_clicked = True
        if add_points_button:
            st.session_state.add_points_clicked = True
        
        # Display additional components based on session state
        if st.session_state.create_partners_clicked:
            self.create_partners()
        
        if st.session_state.view_grade_clicked:
            st.write("Grade viewing functionality triggered.")  
        
        if st.session_state.add_points_clicked:
            st.write("Add points functionality triggered.")

    def select_course(self):
        """
        selecting cources and quizzes
        """
        past_courses = []
        current_courses = []
        current_date = datetime.now()
        
        for course in self.canvas.get_courses():
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
            # Course selection
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
                    return self.mark_attendance(selected_course, selected_quiz)
        
        return None
    
    def mark_attendance(self, selected_course, selected_quiz):
        """
        Handle attendance 
        """
        st.write(f"Selected Quiz: {selected_quiz.title}")
        students = selected_course.get_users(enrollment_type=['student'])
        attendance = {}
        
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

        if st.button("Submit Attendance", key="submit_attendance"):
            # Attendance tracking
            attendance_data = [{"Student Name": student_name, "Status": status} for student_name, status in attendance.items()]
            attendance_df = pd.DataFrame(attendance_data)
        
            # Display attendance record
            st.write("### Attendance Record")
            st.table(attendance_df)
            
            total_present = attendance_df[attendance_df["Status"] == "Here"].shape[0]
            st.write(f"**Total Students Present: {total_present}**")

            # Save attendance to CSV
            save_dir = "data/attendance"
            os.makedirs(save_dir, exist_ok=True)

            quiz_title = selected_quiz.title
            class_name = selected_course.name
            current_date = datetime.now().strftime("%Y-%m-%d")
            file_name = f"{class_name}_{quiz_title}_attendance_{current_date}.csv".replace(" ", "_")

            file_path = os.path.join(save_dir, file_name)
            attendance_df.to_csv(file_path, index=False)

            st.success(f"Attendance saved automatically at: {file_path}")

            # Quiz Data Analysis
            st.write("### Quiz Data Analysis")
            try:
                quiz_analysis = self.analyze_quiz_data(selected_course, selected_quiz)
            except Exception as e:
                st.error(f"Error in quiz analysis: {e}")

            return selected_course
        return None
    
    def analyze_quiz_data(self, selected_course, selected_quiz):
        """
        Analyze quiz data and generate table and graph
        """

        # Create data directory if doesn't already exist
        os.makedirs("data/quiz_analysis", exist_ok=True)

        submissions = selected_quiz.get_submissions()
        quiz_data = []
        
        
        for submission in submissions:
            try:
                user_id = submission.user_id # May need to change to student_ids/student_id
                
                try:
                    user = selected_course.get_user(user_id)
                    student_name = getattr(user, 'name', f'Student ID {user_id}')
                except Exception as user_error:
                    st.warning(f"Could not retrieve user details for ID {user_id}: {user_error}")
                    student_name = f'Student ID {user_id}'
                
                submitted_at = getattr(submission, 'submitted_at', 'Not Submitted')
                quiz_data.append({
                    'Student Name': student_name,
                    'Score': submission.score or 0,  
                    'Submitted At': submitted_at
                })
            except Exception as e:
                st.warning(f"Error processing submission: {e}")
        
        if not quiz_data:
            st.warning("No quiz submissions found.")
            return None
        
        df = pd.DataFrame(quiz_data)
        
        analysis_results = {
            'Total Submissions': len(df),
            'Mean Score': df['Score'].mean(),
            'Median Score': df['Score'].median(),
            'Standard Deviation': df['Score'].std(),
            'Minimum Score': df['Score'].min(),
            'Maximum Score': df['Score'].max()
        }
        
        # Analysis DataFrame
        analysis_df = pd.DataFrame.from_dict(analysis_results, orient='index', columns=['Value'])
        analysis_df.index.name = 'Metric'
        results_filename = f"data/quiz_analysis/{selected_quiz.title}_analysis.csv".replace(" ", "_")
        analysis_df.to_csv(results_filename)
        
        # Display 
        st.dataframe(analysis_df)
        
        return analysis_df
    
    def create_partners(self):
        """
        ...
        """
        st.write("Create partners for quizzes.")
        selected_course = self.select_course()
        


def main():
    """
    Main function to run the Streamlit application
    """
    portal = CanvasPortal()
    portal.run_teacher_portal()

if __name__ == "__main__":
    main()