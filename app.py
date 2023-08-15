import os
import smtplib
import streamlit as st
import logging
from email.mime.text import MIMEText
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from datetime import datetime

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().addHandler(logging.StreamHandler())

st.title('Personal Newsletter Summarization')
st.sidebar.title('Admin & Actions')

my_secret = os.environ['OPENAI_API_KEY']
postmark_secret = os.environ['postmark_key']
sender_key = os.environ['sender_key']
streamlit_key = os.environ['streamlit_key']
receiver_key = os.environ['receiver_key']

# Password protection
password = st.sidebar.text_input("Enter password:", type="password")
correct_password = streamlit_key

# Check if the session state has the 'summary_completed' attribute
if 'summary_completed' not in st.session_state:
    st.session_state.summary_completed = False

if password == correct_password:
    url = st.text_input('Enter URL to add to todo.txt:')
    if st.button('Add URL'):
        with open('todo.txt', 'a') as file:
            file.write(url + '\n')
        st.success('URL added successfully!')

    if st.sidebar.button('View URLs'):
        with open('todo.txt', 'r') as file:
            urls = file.readlines()
        st.write(urls)

    if st.sidebar.button('Clear todo.txt'):
        with open('todo.txt', 'w') as file:
            file.write('')
        st.sidebar.success('todo.txt cleared successfully!')

    if st.sidebar.button('Execute Summarization'):
        try:
            st.sidebar.success('Summarization process started...')
            
            # ... (rest of the summarization code)

            print("All tasks completed successfully!")
            st.sidebar.success('Summarization process completed!')
            st.session_state.summary_completed = True
        except Exception as e:
            logging.error(f"An error occurred during summarization: {str(e)}")
            st.sidebar.error('An error occurred during summarization. Please check the logs for details.')

    # Check if the summarization process has been completed successfully
    if st.session_state.summary_completed:
        if st.sidebar.button('Clear todo log'):
            with open('todo.txt', 'w') as file:
                file.write('')
            st.sidebar.success('todo.txt cleared successfully!')
            st.session_state.summary_completed = False
else:
    st.sidebar.warning(
        'Incorrect password. Please enter the correct password to proceed.')
