from datetime import datetime

import requests
from bs4 import BeautifulSoup

import schedule


url = 'https://korgan.kz/'
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 RuxitSynthetic/1.0 v3975717906 t6703941201591042144 athfa3c3975 altpub cvcv=2 smf=0"
}


def get_data():
    req = requests.get(url=url, headers=headers)
    req.encoding = 'UTF8'
    src = req.text
    soup = BeautifulSoup(src, 'lxml')

    # Сбор всех ссылок на каталоги
    categories_li_1 = soup.find('ul', class_='catalog-menu-ul').find_all('li', class_='catalog-menu-li')
    dict_catalog = []
    for li_1 in categories_li_1:
        categories_li_2 = li_1.find('div', class_='catalog-category hidden-xs hidden-sm')\
            .find_all('a', class_='catalog-menu-li-a')
        for li_2 in categories_li_2:
            dict_catalog.append(li_2.get('href'))

    # сбор карточек в каталогах
    dict_cards = [["Название", "Артикул", "Цена"]]
    sum_count = []
    k = 0
    for url1 in dict_catalog:
        k += 1
        try:
            req1 = requests.get(url=url1, headers=headers)
            req1.encoding = 'UTF8'
            src1 = req1.text
            soup1 = BeautifulSoup(src1, 'lxml')

            name_catalogs = soup1.find_all('div', class_='col-lg-3 col-md-6 col-sm-6 padding-bottom-15 padding-right-0')

            for name_catalog in name_catalogs:
                url2 = f"{name_catalog.find('a').get('href')}?take=all"
                req2 = requests.get(url=url2, headers=headers)
                req2.encoding = 'UTF8'
                src2 = req2.text
                soup2 = BeautifulSoup(src2, 'lxml')

                all_cards = soup2.find_all('div', class_='col-lg-3 col-md-6 col-sm-6 padding-bottom-15 padding-right-0')

                count = 0
                for card in all_cards:
                    if len(card.find_all('span', class_='text-danger')) == 0:
                        count += 1
                        name_product = card.find('div', class_='product-card-text').find('strong').text.strip()

                        if len(card.find('div', class_='product-card-text').find('p').find('strong').find_all('span')) == 1:
                            price = card.find('div', class_='product-card-text').find('p').find('strong').find('span').text.strip()
                        else:
                            price = card.find('div', class_='product-card-text').find('p').find('strong').text.strip()[:-4]

                        article_num = card.find('div', class_='product-card-text').find('p').text.split(':')[-1].strip()

                        dict_cards.append(
                             [
                                 name_product,
                                 article_num,
                                 price
                             ]
                         )

                sum_count.append(count)

        except Exception as ex:
            print(ex)
            print(url1)

        print(k)

    print(sum(sum_count))
    google_table(dict_cards=dict_cards)


def google_table(dict_cards):
    import os.path

    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.oauth2 import service_account

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # mail bot 'parsers@parsers-372008.iam.gserviceaccount.com'
    SAMPLE_SPREADSHEET_ID = '107SdHe8_dV6npe_dKE-7xA2QJgxz6ZOywOy-GZyrZX0'
    SAMPLE_RANGE_NAME = 'korgan.kz'

    try:
        service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()

        # Чистим(удаляет) весь лист
        array_clear = {}
        clear_table = service.clear(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME,
                                    body=array_clear).execute()

        # добавляет информации
        array = {'values': dict_cards}
        response = service.append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                  range=SAMPLE_RANGE_NAME,
                                  valueInputOption='USER_ENTERED',
                                  insertDataOption='OVERWRITE',
                                  body=array).execute()

    except HttpError as err:
        print(err)


def main():
    start_time = datetime.now()

    schedule.every(50).minutes.do(get_data)

    while True:
        schedule.run_pending()

    finish_time = datetime.now()
    spent_time = finish_time - start_time
    print(spent_time)


if __name__ == '__main__':
    main()
