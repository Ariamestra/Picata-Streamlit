import canvasapi
import os
import streamlit as st
from datetime import datetime
from streamlit_option_menu import option_menu
import time
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate

# Set up Canvas API
API_URL = os.environ.get("CANVAS_URL")
API_KEY = os.environ.get("CANVAS_TOKEN")
if not (API_URL and API_KEY):
    raise Exception("'CANVAS_' environment variables not set - see installation instructions to resolve this")

# Initialize Canvas object
canvas = canvasapi.Canvas(API_URL, API_KEY)

# ----------- Home Page -----------------

st.title("Welcome to picaTA")
st.write("PICATA is a tool for instructors who wish to combine Peer Instruction (PI) and Continuous Assessments (CA) utilizing results from students' earlier CA data.")      
