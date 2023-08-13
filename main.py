import os
import smtplib
from email.mime.text import MIMEText
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate

my_secret = os.environ['OPENAI_API_KEY']
postmark_secret = os.environ['postmark_key']
sender_key = os.environ['sender_key']

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
  receiver_email = sender_key

  message = MIMEText(summaries)
  message["Subject"] = "Daily Summaries"
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
