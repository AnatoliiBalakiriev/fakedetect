import os
import streamlit as st

# st.sidebar.selectbox  - anotehr option
languages = ["russian", "ukrainian", "english", "polish", "turkish", "italian", "dutch",
            "serbian", "german", "czech", "french", "bulgarian", "spanish", "romanian"]

language = st.sidebar.radio("Select Language", languages)

st.title("Fake Detection")
st.sidebar.header("Input")

# Очищення поля вводу при зміні мови
if st.session_state.language != language:
    st.session_state.language = language
    input_string = ""

st.session_state.language = language

input_string = st.sidebar.text_area("Input your request and press the RUN button or press Enter", height=100)

if st.sidebar.button("RUN"):
    # Отримання оброблених документів з бази даних
    connection = create_database_connection()
    
    if connection:
        top_2_relevant_articles = get_top_2_relevant_articles(connection, input_string)
    
        # Виведення результатів
        for article_id, article, cosine_similarity in top_2_relevant_articles:
            st.write(f"\n\nThe article with id {article_id} has a similarity value {cosine_similarity}\n\n The Article:\n\n\n{article}")
    close_database_connection(connection)

# Перевірка, чи існує файл для обраної мови
language_file_path = os.path.join("language", f"{language}.py")
if os.path.isfile(language_file_path):
    exec(open(language_file_path).read())
else:
    st.write(f"No code found for language: {language}")
