"""
Module for Personal Newsletter and YouTube Transcript Summarization using Streamlit,
Airtable, and custom summarization logic.
"""

from datetime import datetime
from email.mime.text import MIMEText
import os
import smtplib
from json.decoder import JSONDecodeError
from requests.exceptions import RequestException
import streamlit as st
from airtable import Airtable
from langchain.chains.mapreduce import MapReduceChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader, YoutubeLoader
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
            st.sidebar.success('URLs and YouTube Video IDs cleared successfully!')
        else:
            st.sidebar.warning('No URLs or YouTube Video IDs to clear.')
    except (RequestException, JSONDecodeError) as clear_error:
        st.sidebar.error(
            f"An error occurred while clearing URLs and YouTube Video IDs: {str(clear_error)}")


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
st.title('Personal Newsletter and YouTube Transcript Summarization')
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
        except (RequestException, JSONDecodeError) as add_error:
            st.error(f"An error occurred while adding URL: {str(add_error)}")

    # YouTube Video ID input
    youtube_video_id_input = st.text_input(
        'Enter YouTube Video ID to add to the Airtable for processing for today\'s email summary:'
    ).strip()
    if youtube_video_id_input and st.button('Add YouTube Video ID'):
        try:
            airtable.insert({'YouTube Video ID': youtube_video_id_input})
            st.success('YouTube Video ID added successfully!')
        except (RequestException, JSONDecodeError) as add_error:
            st.error(f"An error occurred while adding YouTube Video ID: {str(add_error)}")

    # View URLs and YouTube Video IDs
    if st.sidebar.button('View URLs and YouTube Video IDs'):
        try:
            records = airtable.get_all()
            urls_and_video_ids = [{'URL': record['fields'].get('URL', ''), 'YouTube Video ID': record['fields'].get('YouTube Video ID', '')}
                                  for record in records if 'URL' in record['fields'] or 'YouTube Video ID' in record['fields']]
            st.write(urls_and_video_ids)
        except (RequestException, JSONDecodeError) as view_error:
            st.error(
                f"An error occurred while fetching URLs and YouTube Video IDs: {str(view_error)}")

    # Execute Summarization
    if st.sidebar.button('Execute Summarization'):
        try:
            st.sidebar.success('Summarization process started...')
            urls_and_video_ids = [{'URL': record['fields'].get('URL', '').strip(), 'YouTube Video ID': record['fields'].get('YouTube Video ID', '').strip()}
                                  for record in airtable.get_all() if 'URL' in record['fields'] or 'YouTube Video ID' in record['fields']]
            ALL_SUMMARIES = ""

            # Initialize LLM
            llm = ChatOpenAI(openai_api_key=MY_SECRET,
                             temperature=0,
                             model_name="gpt-3.5-turbo-16k")

            # Map-Reduce Summarization code
            for index, item in enumerate(urls_and_video_ids, 1):
                url = item['URL']
                youtube_video_id = item['YouTube Video ID']

                if url:
                    print(f"Loading content from URL: {url}...")
                    loader = WebBaseLoader(url)
                elif youtube_video_id:
                    print(f"Loading transcript from YouTube Video ID: {youtube_video_id}...")
                    loader = YouTubeTranscriptLoader(youtube_video_id)

                docs = loader.load()

                # Map
                map_template = """The following is a set of documents\n{docs}\nBased on this list of docs, please identify the main themes \nHelpful Answer:"""
                map_prompt = PromptTemplate.from_template(map_template)
                map_chain = LLMChain(llm=llm, prompt=map_prompt)

                # Reduce
                reduce_template = """The following is set of summaries:\n{doc_summaries}\nTake these and distill it into a final, consolidated summary of the main themes. \nHelpful Answer:"""
                reduce_prompt = PromptTemplate.from_template(reduce_template)
                reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)
                combine_documents_chain = StuffDocumentsChain(llm_chain=reduce_chain, document_variable_name="doc_summaries")
                reduce_documents_chain = ReduceDocumentsChain(combine_documents_chain=combine_documents_chain, collapse_documents_chain=combine_documents_chain, token_max=4000)

                # Combining documents by mapping a chain over them, then combining results
                map_reduce_chain = MapReduceDocumentsChain(llm_chain=map_chain, reduce_documents_chain=reduce_documents_chain, document_variable_name="docs", return_intermediate_steps=False)
                text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=0)
                split_docs = text_splitter.split_documents(docs)
                summary = map_reduce_chain.run(split_docs)

                print("Storing summary in a file...")
                ALL_SUMMARIES += f"{index}. {url if url else youtube_video_id}\n{summary}\n\n"

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
                server.sendmail(sender_email, receiver_email,
                                message.as_string())

            st.sidebar.success('Summarization process completed!')
        except (RequestException, JSONDecodeError) as summarize_error:
            st.sidebar.error(
                f"An error occurred during summarization: {str(summarize_error)}")

    # Clear URLs and YouTube Video IDs
    if st.sidebar.button('Clear URLs and YouTube Video IDs'):
        clear_airtable_records(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
else:
    st.sidebar.warning(
        'Incorrect password. Please enter the correct password to proceed.')
