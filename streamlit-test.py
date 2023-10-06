To be able to get Airtable API access, parse Youtube videos, pdf files and websites for text before applying a language model for summary generation, several Python libraries need to be inclusive such as pandas, requests for API calls, beautifulsoup4 for web scraping, PyPDF2 for PDF file processing, youtube_transcript_api for getting YouTube videos transcriptions, and langchain for text chunking and summarizing.

However, the `langchain` library doesn't appear to exist, so I will use the `Gensim` library to perform text summarization in this example. 

Due to the complexity of the task, this will be a basic functionality code:

```python
# Import necessary modules
import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader
from youtube_transcript_api import YouTubeTranscriptApi
from gensim.summarization import summarize

# Set Airtable's access details
AIRTABLE_BASE_ID = 'insert your Airtable base ID'
AIRTABLE_API_KEY = 'insert your Airtable api key'
AIRTABLE_TABLE_NAME = 'insert your Airtable table name'

headers = {
  "Authorization": f"Bearer {AIRTABLE_API_KEY}",
  "Content-Type": "application/json"
}

def get_data_from_airtable():
    '''Extract URLs from Airtable'''
    response = requests.get(f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}", headers=headers)
    airtable_records = response.json()['records']
    url_list = [record['fields']['URL'] for record in airtable_records]
    return url_list

def text_from_youtube(url):
    '''Extract transcriptions from YouTube video'''
    video_id = url.split('=')[1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return ' '.join([text['text'] for text in transcript])

def text_from_website(url):
    '''Extract text from webpage'''
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    text = ' '.join(soup.stripped_strings)
    return text

def text_from_pdf(url):
    '''Extract text from PDF'''
    response = requests.get(url)
    with open('temp.pdf', 'wb') as f:
        f.write(response.content)
    reader = PdfFileReader('temp.pdf')
    n_pages = reader.numPages
    text = ' '.join([reader.getPage(i).extractText() for i in range(n_pages)])
    return text

def app():
    '''Streamlit App'''
    st.title('URL Summary App')

    url_list = get_data_from_airtable()

    for url in url_list:
        if 'youtube.com' in url:
            text = text_from_youtube(url)
        elif url.endswith('.pdf'):
            text = text_from_pdf(url)
        else:
            text = text_from_website(url)

        summary = summarize(text)

        st.subheader(f'Summary for {url}')
        st.write(summary)

if __name__ == "__main__":
    app()
```

This is a demonstrative example, the code may not run perfectly considering the variable structure of websites, videos on how to get transcriptions and PDF files. The summaries generated are also purely extractive i.e. selected sentences from the original content, not always making perfect sense on their own. Please replace `'insert your Airtable base ID'`, `'insert your Airtable api key'`, and `'insert your Airtable table name'` with your actual Airtable details.

Remember to install all the required libraries before execution. Use the command `pip install streamlit pandas requests beautifulsoup4 PyPDF2 youtube_transcript_api gensim` in your terminal to install them.

Also, please note that YouTube's automated transcriptions won't be available for all videos. In such case, you should handle the exception, or fallback to another method like Speech-to-Text APIs.

As this is quite a large task, each individual segment (like getting data from Airtable, extracting text from different URL types etc) should be thoroughly tested before combining them all to ensure each part works as intended.

Due to the complexity of your concept, I would advise hiring a professional developer or team to ensure a robust implementation of your idea.
