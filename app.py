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
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().addHandler(logging.StreamHandler())

# Initialize or clear the todo.txt file
if not os.path.exists('todo.txt'):
    with open('todo.txt', 'w') as file:
        pass

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

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

if password == correct_password:
    url = st.text_input('Enter URL to add to todo.txt:').strip()
    if url and st.button('Add URL'):
        if is_valid_url(url):  # Validate the URL before adding
            with open('todo.txt', 'a') as file:
                file.write(url + '\n')
            st.success('URL added successfully!')
        else:
            st.error('Invalid URL. Please enter a valid URL.')

    if st.sidebar.button('View URLs'):
        with open('todo.txt', 'r') as file:
            urls = file.readlines()
        st.write(urls)

    if st.sidebar.button('Execute Summarization'):
        try:
            st.sidebar.success('Summarization process started...')
            urls = load_urls("todo.txt")
            all_summaries = ""
            for index, url in enumerate(urls, 1):
                url = url.strip()
                if not url or not is_valid_url(url):  # Skip empty or invalid URLs
                    continue
                # ... rest of the summarization code ...
        except Exception as e:
            logging.error(f"An error occurred during summarization: {str(e)}")
            st.sidebar.error('An error occurred during summarization. Please check the logs for details.')
else:
    st.sidebar.warning(
        'Incorrect password. Please enter the correct password to proceed.')
