import os
import streamlit as st

# st.sidebar.selectbox  - anotehr option
languages = ["russian", "ukrainian", "english", "polish", "turkish", "italian", "dutch",
            "serbian", "german", "czech", "french", "bulgarian", "spanish", "romanian"]

language = st.sidebar.radio("Select Language", languages)

# Перевірка, чи існує файл для обраної мови
language_file_path = os.path.join("language", f"{language}.py")
if os.path.isfile(language_file_path):
    exec(open(language_file_path).read())
else:
    st.write(f"No code found for language: {language}")

# Очищення поля вводу при зміні мови
if 'language' not in st.session_state:
    st.session_state.language = ''

if st.session_state.language != language:
    st.session_state.language = language
    input_string = ""
