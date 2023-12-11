import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import psycopg2
import json
import math

# Інші імпорти

language = st.sidebar.selectbox("Select Language", ["ru", "uk", "tr", "it", "nl", "sr", "pl", "de", "cz", "fr", "bg", "es", "ro", "en"])

# Перевірка, чи існує файл для обраної мови
language_file_path = os.path.join("language", f"{language}.py")
if os.path.isfile(language_file_path):
    exec(open(language_file_path).read())
else:
    st.write(f"No code found for language: {language}")