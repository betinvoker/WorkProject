from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os, time, psycopg2

path = r"chromedriver.exe"
options = Options()
options.headless = True
driver = webdriver.Chrome(executable_path=path, chrome_options=options)

conn = psycopg2.connect(host="localhost", user="admin", password="111", dbname="university_reviews_db")
#   Создать соединение с базой
cursor = conn.cursor()

def main():
    #   Удалить все записи и заполнить таблицу Universities.
    changing_data_universities()
    #   Удалить все записи и заполнить таблици Opinions. 
    changing_data_opinions()
    #   Закрыть браузер после выполнения
    driver.close()

#   Удалить все записи и заполнить таблицу Universities.
def changing_data_universities():
    #   Удалить данные об университетах из таблицы
    delete_universities()
    #   Сброс значения автоинкремена до 1 у таблицы Universities
    reset_auto_increment_universities()
    #   Главная страница сайта
    driver.get("https://tabiturient.ru/")
    #   Нажимать на кнопку загрузить еще, пока она существует на странице
    click_btn('mobpadd20', '/html/body/div[1]/div[2]/div[1]/div/div[5]')
    #   Парсить данные об университетах со страницы
    parse_list_of_universities()

#   Удалить все записи и заполнить таблици Opinions. 
def changing_data_opinions():
    #   Удалить отзывы об университетах из таблицы
    delete_opinions()
    #   Сброс значения автоинкремена до 1 у таблицы Opinions
    reset_auto_increment_opinions()
    #   Взять из базы список университетов
    cursor.execute("SELECT * from search_reviews_universities")
    all_universities = cursor.fetchall()
    #   Перебрать все университеты по списку
    for university in all_universities:
        #   Cтраница Университета
        driver.get(university[3])
        #   Нажимать на кнопку загрузить еще, пока она существует на странице
        click_btn('mobpadd10', '/html/body/div[1]/div[2]/div[1]/div/div[7]')
        time.sleep(5)
        #   Парсить данные с отзывами об университете
        parse_list_of_opinions(university[0])

#   Парсить данные об университетах со страницы
def parse_list_of_universities():  
    block = driver.find_element_by_id('resultdiv0')
    all_universities = block.find_elements_by_class_name('mobpadd20')

    #   Цикл сбора данных и записи данных об университете
    for university in all_universities:
        #   Взять из блока данные об университете
        dict_university = take_data_university(university, all_universities.index(university) + 1)
        
        print("%s | %s | %s | %s\n" % (dict_university.get('abbreviation'), dict_university.get('full_name'), dict_university.get('link'), dict_university.get('logo')))
        adding_universities(dict_university.get('abbreviation'), dict_university.get('full_name'), dict_university.get('link'), dict_university.get('logo'))

        dict_university.clear()
    #   Сохранить изменения в базе
    conn.commit()

#   Парсить данные с отзывами об университете
def parse_list_of_opinions(university):
    block = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div[5]')
    all_opinions = driver.find_elements_by_class_name('mobpadd20-2')

    #   Цикл сбора данных и записи данных отзыва
    for opinion in all_opinions:
        #   Нажимать на ссылку "Показать полностью..."
        click_on_show_link(opinion, '/html/body/div[1]/div[2]/div[1]/div/div[5]/div[' + str(all_opinions.index(opinion) + 1) + ']/div[1]/div[2]/b')
        #   Взять из блока данные об отзыве
        dict_opinion = take_data_opinion(university, opinion, all_opinions.index(opinion) + 1)

        print("%s | %s | %s | %s\n" % (dict_opinion.get('text'), dict_opinion.get('date_opinion'), dict_opinion.get('status'), dict_opinion.get('id_university')))
        adding_opinions(dict_opinion.get('text'), dict_opinion.get('date_opinion'), dict_opinion.get('status'), dict_opinion.get('id_university'))
        
        dict_opinion.clear()
    #   Сохранить изменения в базе
    conn.commit()

#   Взять из блока данные об университете
def take_data_university(university, index):
    abbreviation = university.find_element_by_class_name('font3')
    full_name = university.find_element_by_class_name('font2')
    link = university.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div[2]/div[' + str(index) + ']/table[2]/tbody/tr[2]/td/a[3]')
    logo = university.find_element_by_class_name('vuzlistimg')

    dict_university = {'abbreviation' : abbreviation.text, 'full_name' : full_name.text, 'link' : link.get_attribute("href"), 'logo' : logo.get_attribute("src")[31:]}

    return dict_university

#   Взять из блока данные об отзыве
def take_data_opinion(university, opinion, index):
    text = opinion.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div[5]/div[' + str(index) + ']/div[1]/div[2]')
    date_opinion = opinion.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div[5]/div[1]/div[1]/div[1]/div/div[1]/table/tbody/tr/td[2]/table/tbody/tr/td[5]/span[2]')
    status = positive_or_negative_opinions(opinion)
    id_university = str(university)

    dict_opinion = {'text' : text.text, 'date_opinion' : date_opinion.text, 'status' : status, 'id_university' : id_university}

    return dict_opinion

#   Добавить университет в базу
def adding_universities(abbreviated, full_name, link, logo):
    cursor.execute("INSERT INTO search_reviews_universities(abbreviated, name, link, logo) VALUES (%s,%s,%s,%s)", 
                        (abbreviated, full_name, link, logo))
       
#   Добавить отзывов об университете в базу
def adding_opinions(text, date_opinion, status, id_university):
    cursor.execute("INSERT INTO search_reviews_opinions(text, date_opinion, status, university_id) VALUES (%s,%s,%s,%s)", 
                        (text, date_opinion, status, id_university))

#   Сброс значения автоинкремена до 1 у таблицы Universities
def reset_auto_increment_universities():
    cursor.execute("ALTER SEQUENCE search_reviews_universities_id_seq RESTART WITH 1")

#   Сброс значения автоинкремена до 1 у таблицы Universities
def reset_auto_increment_opinions():
    cursor.execute("ALTER SEQUENCE search_reviews_opinions_id_seq RESTART WITH 1")

#   Удалить все университеты из базы
def delete_universities():
    cursor.execute("DELETE FROM search_reviews_universities")
       
#   Удалить все отзывы из базы
def delete_opinions():
    cursor.execute("DELETE FROM search_reviews_opinions")                        

#   Нажимать на кнопку загрузить еще, пока она существует на странице
def click_btn(data_block, button):
    while check_exists_by_class_name(data_block) == True:
        btn = driver.find_element_by_xpath(button)
        if btn.is_displayed():
            btn.click()
            time.sleep(5)
        else:
            break

#   Нажимать на ссылку "Показать полностью..."
def click_on_show_link(opinion, show_full):
    if check_exists_by_xpath(show_full):
        btn = opinion.find_element_by_xpath(show_full)
        driver.execute_script("arguments[0].click();", btn)

#   Узнать, позитивный или негативный отзыв
def positive_or_negative_opinions(opinion):
    picture = opinion.find_element_by_tag_name("img")
    if picture.get_attribute("src") == "https://tabiturient.ru/img/smile2.png":
        return "False"
    else:
        return "True"

#   Проверка элемента на наличие по классу
def check_exists_by_class_name(class_name):
    try:
        driver.find_element_by_class_name(class_name)
    except NoSuchElementException:
        return False
    return True

#   Проверка элемента на наличие по xpath
def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

if __name__ == "__main__":
    main()