import os
import streamlit as st

languages = ["russian", "ukrainian", "english", "polish", "turkish", "italian", "dutch",
            "serbian", "german", "czech", "french", "bulgarian", "spanish", "romanian"]

# Відобразити поле вводу
st.title("Fake Detection")
st.sidebar.header("Input")
input_string = st.sidebar.text_area("Input your request and press the RUN button or press Enter", height=100)
st.sidebar.button("RUN")
if st.sidebar.button("RUN"):

            # Відобразити вибір мови
            language = st.sidebar.radio("Select Language", languages)
            language_file_path = os.path.join("language", f"{language}.py")
            
            if os.path.isfile(language_file_path):
                exec(open(language_file_path).read())
            else:
                st.write(f"No code found for language: {language}")
