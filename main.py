import os
import streamlit as st

# st.sidebar.selectbox  - anotehr option
languages = ["russian", "ukrainian", "english", "polish", "turkish", "italian", "dutch",
            "serbian", "german", "czech", "french", "bulgarian", "spanish", "romanian"]

language = st.sidebar.selectbox("Select Language", languages)

# Перевірка, чи існує файл для обраної мови
language_file_path = os.path.join("language", f"{language}.py")
if os.path.isfile(language_file_path):
    exec(open(language_file_path).read())
else:
    st.write(f"No code found for language: {language}")
