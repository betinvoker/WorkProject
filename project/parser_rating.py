from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os, time, psycopg2

path = r"chromedriver.exe"
driver = webdriver.Chrome(executable_path=path)

conn = psycopg2.connect(host="localhost", user="admin", password="111", dbname="university_reviews_db")
#   Создать соединение с базой
cursor = conn.cursor()

def main():
    driver.get("https://academia.interfax.ru/ru/ratings/?rating=0&page=0")
    delete_ratings()
    reset_auto_increment_ratings()
    #   Заполнение таблицы
    parse_ratings()
    #   Обновление записей об университете
    change_ratings()
    #   Закрыть браузер после выполнения
    driver.close()

#   Заполнение таблицы
def parse_ratings():
    nav = driver.find_element_by_class_name('pagination')
    pages = nav.find_elements_by_class_name('page')

    item = 2

    for page in pages:
        block = driver.find_element_by_class_name('main')
        universiteties = block.find_elements_by_class_name('-rating')
        btn = driver.find_element_by_xpath('/html/body/div[1]/div[4]/div/section/main/nav/a[%s]' % str(item))

        for university in universiteties:
            dict_university = take_data_university(university, universiteties.index(university) + 1)
            adding_rating(dict_university.get('name'), dict_university.get('link'))
            print("%s|%s\n" % (dict_university.get('name'), dict_university.get('link')))

        item += 1

        btn.click()
        time.sleep(2)

    conn.commit()

#   Взять из блока данные об университете
def take_data_university(university, index):
    name = university.find_element_by_class_name('name')
    link = university.find_element_by_xpath('/html/body/div[1]/div[4]/div/section/main/div/div[%s]/a' % index)

    dict_university = {'name' : name.text, 'link' : link.get_attribute("href") + "?page=ratings"}

    return dict_university

#   Добавить университет в базу
def adding_rating(name, link):
    cursor.execute("INSERT INTO search_reviews_ratings(name, link) VALUES (%s,%s)", (name, link))

#   Удалить все университеты из базы
def delete_ratings():
    cursor.execute("DELETE FROM search_reviews_ratings")

#   Сброс значения автоинкремена до 1 у таблицы Rating
def reset_auto_increment_ratings():
    cursor.execute("ALTER SEQUENCE search_reviews_ratings_id_seq RESTART WITH 1")

#   Обновление записей об университете
def change_ratings():
    #   Взять из базы список университетов
    cursor.execute("SELECT * from search_reviews_ratings")
    all_universities = cursor.fetchall()
    #   Перебрать все университеты по списку
    for university in all_universities:
        #   Cтраница Университета
        driver.get(university[2])
        #   Парсить данные с отзывами об университете
        update_university(university[0])
        time.sleep(5)

#   Обновление записей об университете
def update_university(university):
    ratings = driver.find_elements_by_class_name('card__details')

    dict_rating = {'rating_summary' : None, 'rating_education' : None, 'rating_brand' : None, 'rating_research' : None, 
        'rating_socialization' : None, 'rating_internationalization' : None, 'rating_innovation' : None}

    for rating in ratings:
        if rating.find_element_by_class_name('title').text == 'Сводный':
            dict_rating['rating_summary'] = ' '.join(rating.find_element_by_class_name('subtitle').text.split(' ')[:-1])

        elif rating.find_element_by_class_name('title').text == 'Образование':
            dict_rating['rating_education'] = ' '.join(rating.find_element_by_class_name('subtitle').text.split(' ')[:-1])

        elif rating.find_element_by_class_name('title').text == 'Бренд':
            dict_rating['rating_brand'] = ' '.join(rating.find_element_by_class_name('subtitle').text.split(' ')[:-1])

        elif rating.find_element_by_class_name('title').text == 'Исследования':
            dict_rating['rating_research'] = ' '.join(rating.find_element_by_class_name('subtitle').text.split(' ')[:-1])

        elif rating.find_element_by_class_name('title').text == 'Социализация':
            dict_rating['rating_socialization'] = ' '.join(rating.find_element_by_class_name('subtitle').text.split(' ')[:-1])

        elif rating.find_element_by_class_name('title').text == 'Интернационализация':
            dict_rating['rating_internationalization'] = ' '.join(rating.find_element_by_class_name('subtitle').text.split(' ')[:-1])

        elif rating.find_element_by_class_name('title').text == 'Инновации':
            dict_rating['rating_innovation'] = ' '.join(rating.find_element_by_class_name('subtitle').text.split(' ')[:-1])
    
    cursor.execute("""UPDATE search_reviews_ratings SET
                    rating_summary = %s,
                    rating_education = %s,
                    rating_brand = %s,
                    rating_research = %s,
                    rating_socialization = %s,
                    rating_internationalization = %s,
                    rating_innovation = %s
                    WHERE id = %s""", 
        (
            dict_rating.get('rating_summary'), 
            dict_rating.get('rating_education'), 
            dict_rating.get('rating_brand'), 
            dict_rating.get('rating_research'), 
            dict_rating.get('rating_socialization'), 
            dict_rating.get('rating_internationalization'), 
            dict_rating.get('rating_innovation'), 
            university
        )
    )

    conn.commit()

if __name__ == "__main__":
    main()