# Personal Newsletter Tool

## Accessing the App

To load the service simply click on the button below and enter the password. 

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://personal-news.streamlit.app/)

### Using the Service

* Add a URL

* Click "Execute Summarization" to execute the summarization and send emails.

* Click "Clear todo" to empty the URLs after sending emails.


### "Roadmap"

The "roadmap" is split into 3 sections and for siplicities sake, it will all be tracked here in this one issue outside of bugs, which may get issues, if they're lucky. 

## To Do - BM

- [ ] Connect to correct SMTP
- [ ] Allow for sending to multiple emails
- [ ] Switch to BM OAI API Key in Streamlit Secrets Management
- [x] Switch receiver to a BK's BM email. 


## To Do General - (Both)

- [ ] Allow for the user to add some context to the URL to augment the summary
- [ ] Allow loading PDF files to a folder and have these chunked and summarized
- [ ] Allow loading a URL of a YouTube video that will auto transcribe using OpenAI Whisper and generate a summary
- [ ] Allow loading a MP3 of a Podcast or other audio file that will transcribe using OpenAI Whisper and generate a summary
- [ ] add some sensible logging and error catching so this code can pretend to be real
- [x] Use Airtable instead of todo.txt for storing the URLs as this fixes the state issue and issue of using GitHub and Streamlit cloud.
- [x ] Add logic to clear URLs from the Airtable queue
- [ ] Add tracking for tokens used/cost
- [x ] Add fakeuseragent to requirements.txt 
- [ ] Confirm fakeuseragent actually works

### To Do Personal

- [ ] Add signing for the DKIM / SPF when using postmark app so the emails don't get flagged as spam/phishing


