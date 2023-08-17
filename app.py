"""
Module for Personal Newsletter Summarization using Streamlit, Airtable, and custom summarization logic.
"""

from datetime import datetime
from email.mime.text import MIMEText
import os
import smtplib
import streamlit as st
from airtable import Airtable
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate


def clear_airtable_records(api_key, base_key, table_name):
    """
    Function to clear Airtable records.
    """
    try:
        airtable_instance = Airtable(base_key, table_name, api_key)
        records_list = airtable_instance.get_all()
        if records_list:
            record_ids = [record['id'] for record in records_list]
            for record_id in record_ids:
                airtable_instance.delete(record_id)
            st.sidebar.success('URLs cleared successfully!')
        else:
            st.sidebar.warning('No URLs to clear.')
    except Exception as clear_error:  # Specific exception type should be replaced with Exception
        st.sidebar.error(f"An error occurred while clearing URLs: {str(clear_error)}")


# Secrets
MY_SECRET = os.environ['OPENAI_API_KEY']
POSTMARK_SECRET = os.environ['postmark_key']
SENDER_KEY = os.environ['sender_key']
STREAMLIT_KEY = os.environ['streamlit_key']
RECEIVER_KEY = os.environ['receiver_key']
AIRTABLE_API_KEY = os.environ['airtable_key']
BASE_ID = st.secrets['BASE_ID']
TABLE_NAME = os.environ['TABLE_NAME']

# Initialize Airtable
airtable = Airtable(BASE_ID, TABLE_NAME, api_key=AIRTABLE_API_KEY)

# Streamlit UI
st.title('Personal Newsletter Summarization')
st.sidebar.title('Admin & Actions')

# Password protection
password = st.sidebar.text_input("Enter password:", type="password")
correct_password = STREAMLIT_KEY

if password == correct_password:
    # URL input
    url_input = st.text_input(
        'Enter URL to add to add to the Airtable for processing for todays email summary:'
    ).strip()
    if url_input and st.button('Add URL'):
        try:
            airtable.insert({'URL': url_input})
            st.success('URL added successfully!')
        except Exception as add_error:  # Specific exception type should be replaced with Exception
            st.error(f"An error occurred while adding URL: {str(add_error)}")

    # View URLs
    if st.sidebar.button('View URLs'):
        try:
            records = airtable.get_all()
            urls = [record['fields']['URL'] for record in records if 'URL' in record['fields']]
            st.write(urls)
        except Exception as view_error:  # Specific exception type should be replaced with Exception
            st.error(f"An error occurred while fetching URLs: {str(view_error)}")

    # Execute Summarization
    if st.sidebar.button('Execute Summarization'):
        try:
            st.sidebar.success('Summarization process started...')
            urls = [record['fields']['URL'] for record in airtable.get_all() if 'URL' in record['fields']]
            ALL_SUMMARIES = ""

            # Custom Prompt Template
            PROMPT_TEMPLATE = (
                "Write a high-level executive summary of the following text, and then list the vital key points in bullet form. "
                "The summary should serve as a TL/DR for the content and contain the most important information. If there are topics "
                "that focus on marketing, local marketing, brand compliance, brand voice, marketing or similar topics included in the documents "
                "be sure to include these in the summary as they will be interesting to the BrandMuscle employee who reads the summary. If the "
                "document text does not focus on these topics you can include a section that talks about how to apply the information to local marketing.\n\n"
                "{text}\n\nSUMMARY:"
            )  # Broken into multiple lines
            PROMPT = PromptTemplate.from_template(PROMPT_TEMPLATE)

            # Summarization code
            for index, url in enumerate(urls, 1):
                print(f"Loading content from URL: {url.strip()}...")
                loader = WebBaseLoader(url.strip())
                docs = loader.load()

                print("Initializing LLM...")
                llm = ChatOpenAI(openai_api_key=MY_SECRET,
                                temperature=0,
                                model_name="gpt-3.5-turbo-16k")

                llm_chain = LLMChain(llm=llm, prompt=PROMPT)

                print("Loading and running summarization chain...")
                chain = StuffDocumentsChain(llm_chain=llm_chain,
                                            document_variable_name="text")
                summary = chain.run(docs)

                print("Storing summary in a file...")
                ALL_SUMMARIES += f"{index}. {url.strip()}\n{summary}\n\n"

            # Sending summaries via email
            sender_email = SENDER_KEY
            receiver_email = RECEIVER_KEY
            current_date = datetime.today().strftime('%Y-%m-%d')
            subject = f"Daily Summaries - {current_date}"
            message = MIMEText(ALL_SUMMARIES)
            message["Subject"] = subject
            message["From"] = sender_email
            message["To"] = receiver_email

            with smtplib.SMTP("smtp.postmarkapp.com", 587) as server:
                server.starttls()
                server.login(POSTMARK_SECRET, POSTMARK_SECRET)
                server.sendmail(sender_email, receiver_email, message.as_string())

            st.sidebar.success('Summarization process completed!')
        except Exception as summarize_error:  # Specific exception type should be replaced with Exception
            st.sidebar.error(f"An error occurred during summarization: {str(summarize_error)}")

    # Clear URLs
    if st.sidebar.button('Clear URLs'):
        clear_airtable_records(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
else:
    st.sidebar.warning('Incorrect password. Please enter the correct password to proceed.')
