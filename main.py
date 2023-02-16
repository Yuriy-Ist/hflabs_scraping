import gspread
from bs4 import BeautifulSoup as bs
import schedule
import requests


hflabs_url = "https://confluence.hflabs.ru/pages/viewpage.action?pageId=1181220999"

def get_codes_table(url): #Парсим данные таблицы с сайта, и преобразуем их к нужному виду для полследующей обработки
    response = requests.get(url=url)
    response.encoding = 'utf-8'
    soup = bs(response.text, 'lxml')

    whole_table = soup.find('div', {'class':'table-wrap'})
    th = whole_table.find_all('th')
    td = whole_table.find_all('td', {'class':'confluenceTd'})
    
    lst_items = []
    for th_item in th:
        lst_items.append(th_item.text)

    for td_item in td:
        lst_items.append(td_item.text)

    item_to_dict = iter(lst_items)
    dict_items = dict(zip(item_to_dict, item_to_dict))
    return dict_items

def populate_google_table(url): #Заполняем гугл таблицу данными, которые спарсили и предварительно преобразовали 
    sa = gspread.service_account(filename="config/creds.json")
    sh = sa.open("api")
    wks = sh.worksheet("api1")

    num_row = 1
    col_a, col_b = 'A', 'B'
    for code, description in get_codes_table(url).items():
        col_a += str(num_row)
        col_b += str(num_row)
        wks.update(col_a, code)
        wks.update(col_b, description)
        col_a, col_b = 'A', 'B'
        num_row += 1

    wks.format('A1:B1', {'textFormat': {'bold': True}}) #Отформатировали шапку таблицы

def main():
    schedule.every(10).seconds.do(populate_google_table, hflabs_url) #Здесь можно настроить периодичность с которой будут парсится и соответственно обновляться данные в таблице.
    
    while True:
        schedule.run_pending()

    


if __name__ == '__main__':  
    main()    #Запускаем парсер

    