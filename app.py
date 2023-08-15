import os
import smtplib
import streamlit as st
from email.mime.text import MIMEText
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from datetime import datetime
from airtable import Airtable

# Function to calculate tokens and cost
def calculate_tokens_and_cost(response):
    tokens_used = response['usage']['total_tokens']
    cost_per_token = 0.06 / 1000  # Assuming $0.06 per 1000 tokens, adjust this value based on your pricing
    cost = tokens_used * cost_per_token
    return tokens_used, cost

# Secrets
my_secret = os.environ['OPENAI_API_KEY']
postmark_secret = os.environ['postmark_key']
sender_key = os.environ['sender_key']
streamlit_key = os.environ['streamlit_key']
receiver_key = os.environ['receiver_key']
AIRTABLE_API_KEY = os.environ['airtable_key']
BASE_ID = st.secrets['BASE_ID']
TABLE_NAME = os.environ['TABLE_NAME']

airtable = Airtable(BASE_ID, TABLE_NAME, api_key=AIRTABLE_API_KEY)

st.title('Personal Newsletter Summarization')
st.sidebar.title('Admin & Actions')

# Password protection
password = st.sidebar.text_input("Enter password:", type="password")
correct_password = streamlit_key

if password == correct_password:
    url_input = st.text_input('Enter URL to add to add to the Airtable for processing for todays email summary:').strip()
    if url_input and st.button('Add URL'):
        airtable.insert({'URL': url_input})
        st.success('URL added successfully!')

    if st.sidebar.button('View URLs'):
        records = airtable.get_all()
        urls = [record['fields']['URL'] for record in records if 'URL' in record['fields']]
        st.write(urls)

    if st.sidebar.button('Execute Summarization'):
        st.sidebar.success('Summarization process started...')
        urls = [record['fields']['URL'] for record in airtable.get_all() if 'URL' in record['fields']]
        all_summaries = ""
        total_tokens_used = 0

        # Custom Prompt Template
        prompt_template = """Write a high-level executive summary of the following text, and then list the vital key points in bullet form. The summary should serve as a TL/DR for the content and contain the most important information. If there are topics that focus on marketing, local marketing, brand compliance, brand voice, marketing or similar topics included in the documents be sure to include these in the summary as they will be interesting to the BrandMuscle employee who reads the summary. If the document text does not focus on these topics you can include a section that talks about how to apply the information to local marketing.

        {text}

        SUMMARY:"""
        PROMPT = PromptTemplate.from_template(prompt_template)

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
            summary, response = chain.run(docs)  # Assuming chain.run returns the response as well

            tokens_used, cost = calculate_tokens_and_cost(response)
            total_tokens_used += tokens_used

            print("Storing summary in a file...")
            all_summaries += f"{index}. {url.strip()}\n{summary}\n\n"

        # Log the tokens and cost
        st.write(f"Total tokens used: {total_tokens_used}")
        st.write(f"Total cost: ${total_tokens_used * cost_per_token:.4f}")

        # Sending summaries via email
        sender_email = sender_key
        receiver_email = receiver_key
        current_date = datetime.today().strftime('%Y-%m-%d')
        subject = f"Daily Summaries - {current_date}"
        message = MIMEText(all_summaries)
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email

        with smtplib.SMTP("smtp.postmarkapp.com", 587) as server:
            server.starttls()
            server.login(postmark_secret, postmark_secret)
            server.sendmail(sender_email, receiver_email, message.as_string())

        st.sidebar.success('Summarization process completed!')

        if st.sidebar.button('Clear URLs'):
            records = airtable.get_all()
            if records:
                record_ids = [record['id'] for record in records]
                for record_id in record_ids:
                    airtable.delete(record_id)
                st.sidebar.success('URLs cleared successfully!')
            else:
                st.sidebar.warning('No URLs to clear.')
else:
    st.sidebar.warning('Incorrect password. Please enter the correct password to proceed.')
