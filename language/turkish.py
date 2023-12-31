# CHECKING EXISTING NEW ARTICLES
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import psycopg2
import json
import dateparser

# З'єднання з базою даних PostgreSQL
# Функція для створення з'єднання з базою даних
def create_database_connection():
    try:
        conn = psycopg2.connect(
            host="02f7e6f1-1adb-4347-835a-02c74fcccb0e.db.cloud.postgresml.org",
            port=6432,
            database="pgml_adipfbagfodmwax",
            user="u_2qsbxxofmtnki2r",
            password="j2k3xtdknrlyrdv"
        )
        return conn
    except Exception as e:
        print(f"Error creating database connection: {str(e)}")
        return None

# Функція для закриття з'єднання з базою даних
def close_database_connection(conn):
    try:
        if conn:
            conn.close()
            print("Database connection closed.")
    except Exception as e:
        print(f"Error closing database connection: {str(e)}")
        
def check_fakeness(article_text):
    # Перевірка наявності слова "Фейк" або "фейк" у тексті статті
    if re.search(r'\bFake|Manipülasyon|video fake|videofake|Yalan|yalan\b', article_text, re.IGNORECASE):
        return 1
    else:
        return 0

def insert_data(conn, data):
    # Запит на вставку даних в таблицю
    insert_query = """
    INSERT INTO pgml.stopfakes_tr (title, article, url, date, relative_urls, source_url, anchor_texts, relative_images, fakeness)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    with conn.cursor() as cursor:
        cursor.executemany(insert_query, data)
    conn.commit()

def fetch_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1', {'class': 'entry-title'}).text
    article_content = soup.find('div', {'class': 'td-post-content tagdiv-type'})
    article_text = article_content.get_text(separator='\n', strip=True) if article_content else ''

    # Перевірка на фейк
    fakeness = check_fakeness(article_text)

    # Знайдемо посилання, що стоїть біля слова "Источник" в тегу <p> в тексті статті
    source_url = None
    for paragraph in article_content.find_all('p'):
        if "Kaynak" in paragraph.get_text():
            link_tag = paragraph.find('a', href=True)
            if link_tag:
                source_url = link_tag['href']
                break

    # Збирання відносних посилань та тексту, на якому вони закріплені
    relative_urls = [a_tag['href'] for a_tag in article_content.find_all('a', href=True)]
    anchor_texts = [a_tag.text for a_tag in article_content.find_all('a', href=True)]

    # Збирання відносних зображень
    relative_images = [img_tag['src'] for img_tag in article_content.find_all('img', src=True)]

    # Форматування списків для збереження у CSV
    relative_urls_str = '\n'.join(relative_urls)
    anchor_texts_str = '; '.join(anchor_texts)
    relative_images_str = '\n'.join(relative_images)

    date_tag = soup.find('time', {'class': 'entry-date updated td-module-date'})
    date = date_tag.text if date_tag else ''

    return title, article_text, date, relative_urls_str, anchor_texts_str, relative_images_str, fakeness, source_url

# def fetch_data_from_category(category, conn):
#     articles_data = []
#     for page_number in tqdm(range(1, 2)):  # Смужка прогресу для сторінок
#         url = f'https://www.stopfake.org/tr/category/{category}/page/{page_number}/'
#         response = requests.get(url)
#         soup = BeautifulSoup(response.content, 'html.parser')

#         article_number = 0
#         for article in soup.find_all('div', {'class': 'item-details'}):
#             link_tag = article.find('a', href=True)
#             if link_tag:
#                 article_url = link_tag['href']
#                 title, article_text, date, relative_urls, anchor_texts, relative_images, fakeness, source_url = fetch_article(article_url)

#                 # Перевірка, чи такий title вже існує в базі даних
#                 with conn.cursor() as cursor:
#                     cursor.execute("SELECT COUNT(*) FROM pgml.stopfakes_tr WHERE title = %s", (title,))
#                     result = cursor.fetchone()
#                     if result[0] > 0:
#                         print(f'SKIPPED article from the {category.upper()} category on the page {page_number} because it is already in the database: {title}\n')
#                         continue

#                 articles_data.append((
#                     title,
#                     article_text,
#                     article_url,
#                     date,
#                     relative_urls,
#                     source_url,
#                     anchor_texts,
#                     relative_images,
#                     fakeness,
#                 ))
                
#                 article_number += 1
#                 print(f'PROCESSED article {article_number} from the {category.upper()} category on the page {page_number}: {title}\n')

#     return articles_data

def main():
    
    # Створення з'єднання з базою даних
    connection = create_database_connection()
    
    if not connection:
        print("Could not establish a database connection. Exiting...")
        return

    # try:
    #     # Збір даних з категорії "kontekst"
    #     articles_data_kontekst = fetch_data_from_category("haberler-tr", connection)
    #     if articles_data_kontekst:
    #         insert_data(connection, articles_data_kontekst)

    #     # Збір даних з категорії "factcheck_for_facebook_ru"
    #     articles_data_factcheck = fetch_data_from_category("fbcheck_tr", connection)
    #     if articles_data_factcheck:
    #         insert_data(connection, articles_data_factcheck)

    # finally:
        # Завершення роботи та закриття з'єднання з базою даних
    close_database_connection(connection)

if __name__ == '__main__':
    main()
    

def create_embeddings_for_articles(conn):
    with conn.cursor() as cursor:
        # Отримання списку статей з бази даних
        cursor.execute("SELECT id, title || article AS title_article FROM pgml.stopfakes_tr WHERE embed IS NULL;")
        articles = cursor.fetchall()

        for article_id, article in tqdm(articles, desc="Creating Embeddings"):

            # Оновлення запису в таблиці з вектором
            cursor.execute("""
                UPDATE pgml.stopfakes_tr
                SET embed = pgml.embed('intfloat/multilingual-e5-large', %s)::vector(1024)
                WHERE id = %s;
            """, (article, article_id,))
    
    conn.commit()
    

connection = create_database_connection()
if connection:

    # Збереження векторів для статей, які вже оброблені та збережені в базі даних
    create_embeddings_for_articles(connection)

    close_database_connection(connection)
    
# Функція для отримання топ-2 статей за схожістю до запиту
def get_top_2_relevant_articles(conn, query):
    with conn.cursor() as cursor:
        # Створення вектора для запиту
        cursor.execute("""
            WITH request AS (
                SELECT pgml.embed('intfloat/multilingual-e5-large', %s)::vector(1024) AS query_vector
            )
            SELECT
                id,
                title, 
                article,
                1 - (embed <=> (SELECT query_vector FROM request)) AS cosine_similarity,
                url,
                relative_images,
                date
            FROM pgml.stopfakes_tr
            ORDER BY cosine_similarity DESC
            LIMIT 2;
        """, (query,))
        
        # Отримання результатів
        top_2_relevant_articles = cursor.fetchall()

    return top_2_relevant_articles

st.title("Fake Detection")
st.sidebar.header("Input")

input_string = st.sidebar.text_area("Input your request and press the RUN button or press Enter", height=100)

# Отримати сторінку за посиланням і перевірити її доступність
def is_url_accessible(url):
    try:
        response = requests.head(url)
        return response.status_code == 200  # Код 200 означає успішний запит
    except requests.ConnectionError:
        return False
        
if st.sidebar.button("RUN"):
    # Отримання оброблених документів з бази даних
    connection = create_database_connection()
    
    if connection:
        top_2_relevant_articles = get_top_2_relevant_articles(connection, input_string)
    
        # Виведення результатів
        for article_id, title, article, cosine_similarity, url, images, date in top_2_relevant_articles:
            # Розділити рядок images за https://
            image_links = images.split('https://')

            # Видалити перший пустий рядок, який з'являється після розділення
            image_links = image_links[1:]

            # Додати 'https://' назад до кожного посилання на зображення
            image_links = ['https://' + link for link in image_links]
            
            try:
                parsed_date = dateparser.parse(date)
                formatted_date = parsed_date.strftime('%Y-%m')
            except:
                formatted_date = None
            if formatted_date:
                st.markdown(f"<b>{formatted_date}</b>\n\nThe article with id <b>{article_id}</b> has a similarity value <b>{round(cosine_similarity, 3)}</b>", unsafe_allow_html=True)
            else:
                st.markdown(f"The article with id <b>{article_id}</b> has a similarity value <b>{round(cosine_similarity, 3)}</b>", unsafe_allow_html=True)
            st.markdown(f"<a href='{url}' target='_blank'><b>{title}</b></a>", unsafe_allow_html=True)
            st.markdown(f"<p>{article}</p>", unsafe_allow_html=True)  # Відформатований текст у параграфі

            # Вивести посилання на зображення, які доступні
            for image_link in image_links:
                if is_url_accessible(image_link):
                    st.image(image_link)
                
    close_database_connection(connection)
