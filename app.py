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

            # Custom Prompt Template
            prompt_template = """Write a high-level executive summary of the following text, and then list the vital key points in bullet form. The summary should serve as a TL/DR for the content and contain the most important information. If there are topics that focus on marketing, local marketing, brand compliance, brand voice, marketing or similar topics included in the documents be sure to include these in the summary as they will be interesting to the BrandMuscle employee who reads the summary. If the document text does not focus on these topics you can include a section that talks about how to apply the information to local marketing.

{text}

SUMMARY:"""
            PROMPT = PromptTemplate.from_template(prompt_template)

            def load_urls(file_path):
                with open(file_path, "r") as file:
                    return file.readlines()

            def send_email(summaries):
                sender_email = sender_key
                receiver_email = receiver_key

                # Get the current date in the desired format
                current_date = datetime.today().strftime('%Y-%m-%d')

                # Include the current date in the subject
                subject = f"Daily Summaries - {current_date}"

                message = MIMEText(summaries)
                message["Subject"] = subject
                message["From"] = sender_email
                message["To"] = receiver_email

                with smtplib.SMTP("smtp.postmarkapp.com", 587) as server:
                    server.starttls()
                    server.login(postmark_secret, postmark_secret)
                    server.sendmail(sender_email, receiver_email, message.as_string())

            def store_summary(summary):
                with open("summaries.txt", "a") as file:
                    file.write(summary + "\n")

            urls = load_urls("todo.txt")
            all_summaries = ""

            for index, url in enumerate(urls, 1):
                print(f"Loading content from URL: {url.strip()}...")
                loader = WebBaseLoader(url.strip())
                docs = loader.load()

                print("Initializing LLM...")
                llm = ChatOpenAI(openai_api_key=my_secret,
                                temperature=0,
                                model_name="gpt-3.5-turbo-16k")

                llm_chain = LLMChain(llm=llm, prompt=PROMPT)

                print("Loading and running summarization chain...")
                chain = StuffDocumentsChain(llm_chain=llm_chain,
                                            document_variable_name="text")
                summary = chain.run(docs)

                print("Storing summary in a file...")
                store_summary(summary)

                all_summaries += f"{index}. {url.strip()}\n{summary}\n\n"

            print("Sending summaries via email...")
            send_email(all_summaries)

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
