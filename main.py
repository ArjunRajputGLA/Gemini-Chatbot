
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from datetime import datetime
from PIL import Image
import io
import time

# Load environment variables
load_dotenv()

# Define available models
available_models = {
    'Pro': 'gemini-pro',
    'Mini': 'gemini-mini',
    'Standard': 'gemini-standard'
}

# Streamlit page configuration
st.set_page_config(
    page_title='Gemini Pro QnA',
    layout='wide',
    initial_sidebar_state='expanded',
    page_icon = '🤖'
)

# Main page layout
st.markdown("""
    <style>
        .reportview-container .main .block-container {
            flex: 1 1 75%;
            padding: 0px 50px;
        }
        .reportview-container .main {
            display: flex;
            flex-direction: row;
        }
    </style>
""", unsafe_allow_html=True) 

selected_model_name = st.selectbox('Select Gemini Model', list(available_models.keys()))
selected_model = available_models[selected_model_name]   # Main page headers and input

st.header('Gemini Pro QnA Application')
st.title('SkillCred')

# Configure the Generative AI model based on selection
model = genai.GenerativeModel(selected_model)
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Function to get response from the Gemini model with retry logic
def get_gemini_response(question, images=None, retries=3, backoff_factor=2):
    prompt = question
    if images:
        # Process each image and convert them to bytes
        image_bytes_list = []
        for image in images:
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes_list.append(image_bytes.getvalue())
        # Combine text and image bytes in a suitable format
        prompt = f"Text: {question}\nImages: {image_bytes_list}"
    
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except ResourceExhausted as e:
            if attempt < retries - 1:
                time.sleep(backoff_factor * (2 ** attempt))
            else:
                st.error("API quota exceeded. Please try again later.")
                return None

question = st.text_input('', placeholder='Ask Prompt')

# Initialize session state to store conversation history and uploaded files
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Handle button click to get response and store conversation
if st.button('Ask prompt'):
    if question != "": 
        response = get_gemini_response(question)
        if response:
            # Get current time and date
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Store the question, response, and time in the session state
            st.session_state.conversation_history.append(('User', question, current_time))
            st.session_state.conversation_history.append(('Gemini', response, current_time))
            st.write('User:', question)
            st.write('Gemini:', response)
    else:
        st.warning("Prompt cannot be empty!")

# Sidebar on the right to display conversation history
st.sidebar.header('Conversation History')
for i, (sender, message, timestamp) in enumerate(st.session_state.conversation_history):
    if sender == 'User':
        with st.sidebar.expander(f'{timestamp} - {message}'):
            st.write(message) 