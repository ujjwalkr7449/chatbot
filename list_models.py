import google.generativeai as genai
import streamlit as st

# Load the API key from secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# List available models
models = genai.list_models()
for model in models:
    print(model.name)
