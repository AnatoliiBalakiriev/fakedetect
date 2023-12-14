import streamlit as st

# Введення даних та кнопка "RUN"
st.sidebar.header("Input")
input_string = st.sidebar.text_area("Input your request and press the RUN button or press Enter", height=100)
run_pressed = st.sidebar.button("RUN")

# Вибір мови
languages = ["russian", "ukrainian", "english", "polish", "turkish", "italian", "dutch",
            "serbian", "german", "czech", "french", "bulgarian", "spanish", "romanian"]
language = st.sidebar.radio("Select Language", languages)

# Перевірка, чи була натиснута кнопка "RUN" і чи існує файл для обраної мови
if run_pressed:
    language_file_path = os.path.join("language", f"{language}.py")
    if os.path.isfile(language_file_path):
        exec(open(language_file_path).read())
    else:
        st.write(f"No code found for language: {language}")
