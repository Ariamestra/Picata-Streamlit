import streamlit as st

# ----------- Teacher Portal Functions -----------------
def create_partners():
    st.write("Create partners for quizzes.")
    
    # Layout two columns for current and past courses
    current_col, past_col = st.columns(2)
    
    with current_col:
        current_courses_button = st.button("Current Courses", key="current_courses")
        
    with past_col:
        past_courses_button = st.button("Past Courses", key="past_courses")

    # Update session state based on button clicks
    if current_courses_button:
        st.session_state.current_courses_clicked = True
    if past_courses_button:
        st.session_state.past_courses_clicked = True

    # Additional functionality based on session state
    if st.session_state.get("current_courses_clicked"):
        st.write("Displaying current courses.")
        
    if st.session_state.get("past_courses_clicked"):
        st.write("Displaying past courses.")

# ----------- Teacher Portal -----------------
# Assume `selected` variable is defined earlier in your code
selected = "Teacher"  # Replace with dynamic selection in your full app

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
        create_partners()
        
    if st.session_state.view_grade_clicked:
        st.write("Grade viewing functionality triggered.")  
    
    if st.session_state.add_points_clicked:
        st.write("Add points functionality triggered.")
