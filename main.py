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

language = st.sidebar.selectbox("Select Language", ["russian", "ukrainain", "english", "polish", "turkish", "italian", "dutch",
                                                    "serbian", "german", "czech", "french", "bolgarian", "spanish", "romanian"])

# Перевірка, чи існує файл для обраної мови
language_file_path = os.path.join("language", f"{language}.py")
if os.path.isfile(language_file_path):
    exec(open(language_file_path).read())
else:
    st.write(f"No code found for language: {language}")
