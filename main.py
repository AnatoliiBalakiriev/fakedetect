import os
import streamlit as st

languages = ["russian", "ukrainian", "english", "polish", "turkish", "italian", "dutch",
            "serbian", "german", "czech", "french", "bulgarian", "spanish", "romanian"]

selected_language = st.sidebar.empty()  # Створення місця для вибору мови

# Створення кнопок для вибору мови
for lang in languages:
    if st.sidebar.button(lang):
        selected_language.text(lang)  # Встановлення вибраної мови

language = selected_language.text

# Перевірка, чи існує файл для обраної мови
if language:
    language_file_path = os.path.join("language", f"{language}.py")
    if os.path.isfile(language_file_path):
        exec(open(language_file_path).read())
    else:
        st.write(f"No code found for language: {language}")
else:
    st.write("Please select a language")
