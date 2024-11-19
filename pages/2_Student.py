import os
import streamlit as st
import time
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

st.title(f"Welcome to the Student Portal")

PDF_PATH ="Data/Discrete_Math_Book.pdf"

# Process the bundled PDF file
@st.cache_data
def process_embedded_pdf(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_documents(pages)
    
    # Combine the text chunks into a single string
    pdf_content = "\n".join([doc.page_content for doc in texts])
    return pdf_content

# Process and store the PDF content
if "pdf_content" not in st.session_state:
    st.session_state["pdf_content"] = process_embedded_pdf(PDF_PATH)

# Display the processed content ------------------------------------------------------
if st.session_state["pdf_content"]:
    with st.expander("View Embedded PDF Content"):
        st.text_area("PDF Content", st.session_state["pdf_content"], height=450)

# System message for the chatbot
system_message = """
You are PicaTA, a knowledgeable teaching assistant specialized in discrete mathematics.
Your goal is to provide helpful, detailed, and step-by-step explanations to undergraduate 
computer science students. Always maintain a friendly and professional tone. Use the context 
provided from the conversation and the embedded PDF to support your responses.
"""

# Define the prompt template
template = """
System: {system_message}

Context from PDF: {pdf_context}

Answer the question below.

Here is the conversation history: {context}

Answer: {question}
"""

model = OllamaLLM(model="llama3.2")
prompt = ChatPromptTemplate.from_template(template)

# Handle conversation
def handle_conversation(user_input, context):
    pdf_context = st.session_state.get("pdf_content", "") 
    result = prompt | model
    response = result.invoke({
        "system_message": system_message,
        "pdf_context": pdf_context,
        "context": context,
        "question": user_input
    })
    return response

# Chat history session state 
if "messages" not in st.session_state:
    st.session_state.messages = []  # Store chat messages 
if "context" not in st.session_state:
    st.session_state.context = ""  # Store context

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process new user input
if user_input := st.chat_input("Ask a question about the document or your coursework:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.context += f"\nUser: {user_input}"

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process user input and AI response
    start_time = time.time()
    ai_response = handle_conversation(user_input, st.session_state.context)
    end_time = time.time()
    response_time = end_time - start_time

    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # Update context 
    st.session_state.context += f"\nPicaTA: {ai_response}"

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(ai_response)

    st.write(f"Response time: {response_time:.2f} seconds")
