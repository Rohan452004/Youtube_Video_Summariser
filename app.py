# Importing Libraries
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from deep_translator import GoogleTranslator
from gtts import gTTS

# Running Streamlit
import streamlit as st

# Extracting Transcript from YouTube
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from textwrap import dedent
from pytube import YouTube

# Get Key value from Dictionary
def get_key_from_dict(val, dic):
    key_list = list(dic.keys())
    val_list = list(dic.values())
    ind = val_list.index(val)
    return key_list[ind]

# Hide Streamlit Footer and buttons
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# Adding logo for the App
# Load the image file
image = open("app_logo.gif", "rb").read()

# Display the image in the sidebar
st.sidebar.image(image, use_column_width=True)

# Input Video Link
url = st.sidebar.text_input('Video URL', 'https://www.youtube.com/watch?v=IWs0U0-HMcI')

# Fetching the title of the YouTube video from the provided URL
video_id = urlparse(url).query[2:]
response = requests.get(f"https://www.youtube.com/watch?v={video_id}")
soup = BeautifulSoup(response.text, 'html.parser')
title = soup.find("title").string

value = title
st.info("### " + value)
st.video(url)

# Specify Summarization type
sumtype = st.sidebar.selectbox(
    'Specify Summarization Type',
    options=['Abstractive'])

sumlength = st.sidebar.selectbox(
    'Specify Summarization length',
    options=['Small', 'Medium', 'Large'])

if sumlength == 'Small':
    length = 2000
elif sumlength == 'Medium':
    length = 1500
else:
    length = 1000

# Define languages dictionary
languages_dict ={'en':'English' ,'bn':'Bengali' ,'gu':'Gujarati'  ,'hi':'Hindi' ,'kn':'Kannada' ,'ml':'Malayalam' ,'mr':'Marathi' ,'or':'Odia' ,'ta':'Tamil' ,'te':'Telugu'  ,'ur':'Urdu'}


# Select Language Preference
add_selectbox = st.sidebar.selectbox(
    "Select Language",
    ('English' ,'Bengali' ,'Gujarati'  ,'Hindi' ,'Kannada' ,'Malayalam' ,'Marathi' ,'Odia' ,'Tamil' ,'Telugu'  ,'Urdu')

)

# If summarize button is clicked
if st.sidebar.button('Summarize'):
    st.success(dedent("""### \U0001F4D6 Summary
    > Success!
    """))

    # Generate Transcript by slicing YouTube link to id
    url_data = urlparse(url)
    id_video = url_data.query[2:]

    # Obtain YouTube video transcript
    transcript = YouTubeTranscriptApi.get_transcript(id_video)

    # Extract text from transcript
    doc = ""
    for line in transcript:
        doc = doc + ' ' + line['text']

    # Perform abstractive summarization
    summarizer = pipeline('summarization',model='sshleifer/distilbart-cnn-12-6')

    # Break the text into smaller chunks for summarization
    result = doc
    num_iters = int(len(result) / length)
    summarized_text = []

    for i in range(0, num_iters + 1):
        start = i * length
        end = (i + 1) * length
        chunk = result[start:end]
        out = summarizer(chunk)
        out = out[0]
        out = out['summary_text']
        summarized_text.append(out)

    # Combine the summarized chunks into a single summary
    final_summary = " ".join(summarized_text)
    para = GoogleTranslator(source='auto', target=get_key_from_dict(add_selectbox, languages_dict)).translate(final_summary)

    html_str3 = f"""
    <style>
    p.a {{
    text-align: justify;
    }}
    </style>
    <p class="a">{para}</p>
    """
    st.markdown(html_str3, unsafe_allow_html=True)

    # Generate Audio
    st.success("###  \U0001F3A7 Hear your Summary")
  
    speech = gTTS(text=para, lang=get_key_from_dict(add_selectbox, languages_dict), slow=False)
    speech.save('user_trans.mp3')
    audio_file = open('user_trans.mp3', 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/ogg', start_time=0)
