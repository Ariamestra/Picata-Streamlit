# picaTA Streamlit

**PicaTA** is an interactive teaching assistant tool for instructors and students, designed to support peer instruction (PI) and continuous assessment (CA) integration. The platform helps instructors manage courses, track student progress, and facilitate personalized student learning in discrete mathematics and algorithms.

## Features

### Instructor Portal
- **Create Partners**: Generate partners for quizzes.
- **View Grades**: Review and analyze student performance.
- **Add Points**: Update scores based on assessments.

### Student Portal
- **Interactive Learning**: Engage with an AI-driven teaching assistant (TA) tailored for discrete mathematics and algorithms. Students can ask questions, and the TA provides step-by-step guidance without giving direct answers to encourage deep learning.

## Installation

1. **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd picaTA
    ```

2. **Set Up the Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # For macOS/Linux
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**:
    - `CANVAS_URL`: Your Canvas API base URL.
    - `CANVAS_TOKEN`: Your Canvas API key.
  
    These variables are essential for API interaction. You can set them directly in the terminal:
    ```bash
    export CANVAS_URL="your_canvas_url"
    export CANVAS_TOKEN="your_canvas_token"
    ```


## Running the App

Start the Streamlit app with the following command:

```bash
streamlit run main.py
```

## Usage

### Sidebar Menu
- **Home**: An overview of picaTA and its functionalities.
- **Teacher**: Instructor-specific tools for course and assessment management.
- **Student**: A conversational assistant for student learning support.

### Student Chatbot
- picaTA’s chatbot engages students in learning through guided assistance on complex topics. Ask questions to enhance understanding of discrete mathematics and algorithms.

## Libraries and Dependencies

- **Streamlit**: Web application framework for displaying interactive elements.
- **Ollama**: Software platform that allows users to run large language models (LLMs) on their local computer.
- **canvasapi**: Python wrapper for the Canvas LMS API.
- **langchain_ollama**: Language model library for interactive question-answering with a conversational AI model.
- **streamlit_option_menu**: Custom sidebar navigation for streamlined access to various features.

## Notes
- **Environment Configuration**: Ensure `CANVAS_URL` and `CANVAS_TOKEN` are set as environment variables to use Canvas API functionalities.