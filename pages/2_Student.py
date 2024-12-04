import os
import streamlit as st
import time
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
#from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


st.title(f"Welcome to the Student Portal")

# File Uploader -------------------------------------------------
with st.sidebar:
    uploaded_files = st.file_uploader("Upload PDFs", type=['pdf'], accept_multiple_files=True)
    if uploaded_files:
        combined_pdf_content = ""  

        @st.cache_data
        def process_pdf(file_path):
            loader = PyPDFLoader(file_path)
            pages = loader.load()

            # Split text into chunks 
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            texts = text_splitter.split_documents(pages)

            # Extract content
            pdf_content = "\n".join([doc.page_content for doc in texts])
            return pdf_content

        for uploaded_file in uploaded_files:
            temp_file_path = f"temp_{uploaded_file.name}"
            
            # Save each uploaded file temporarily
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            # Process each PDF 
            pdf_content = process_pdf(temp_file_path)
            combined_pdf_content += f"\n--- Content from {uploaded_file.name} ---\n{pdf_content}"

            # Clean up temporary file
            os.remove(temp_file_path)

        # Ensure PDF(s) are in session state
        st.session_state["pdf_content"] = combined_pdf_content
        st.success(f"{len(uploaded_files)} PDFs processed successfully!")
    else:
        if "pdf_content" not in st.session_state:
            st.session_state["pdf_content"] = ""


# Display extracted content (Delete Later) ---------------------------------------
if st.session_state["pdf_content"]:
    with st.expander("View extracted PDF content"):
        st.text_area("PDF Content", st.session_state["pdf_content"], height=450)
        

# Chat -----------------------------------------------------------------------------
system_message = """
You are PicaTA, a knowledgeable teaching assistant. Your goal is to provide helpful, detailed, and step-by-step explanations to undergraduate students. 
Do not give answers outright, instead, guide students toward understanding. Always maintain a friendly and professional tone. 
Use the context provided from the conversation and possibly the uploaded PDF to support your responses.
"""


template = """
System: {system_message}

Context from PDF: {pdf_context}

Answer the question below.

Here is the conversation history: {context}

Answer: {question}
"""

system_message = """
You are PicaTA
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

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process new user input
if user_input := st.chat_input("You:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.context += f"\nUser: {user_input}"

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process user input and picata response
    start_time = time.time()
    ai_response = handle_conversation(user_input, st.session_state.context)
    end_time = time.time()
    response_time = end_time - start_time

    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    
    st.session_state.context += f"\nPicaTA: {ai_response}"

    # picta response
    with st.chat_message("assistant"):
        st.markdown(ai_response)

    st.write(f"Response time: {response_time:.2f} seconds")