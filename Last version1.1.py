import requests
from bs4 import BeautifulSoup
import csv
import os
import time

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36', 'accept': '*/*'}
URL = 'https://zakupki.prom.ua/gov/tenders?status=6&location=65-68&amount_f=100000&primary_classifier=45330000-9&createdFrom=2019-01-01'
FILE = 'tenders.csv'

DATA = {"email":input('email: '), "password":input('pass: ')}
URL_LOGIN = 'https://zakupki.prom.ua/signin'
COUNTER=0

S = requests.Session()
R = S.post(URL_LOGIN, data=DATA)

def save_file(items,path):
    with open (path, 'w', newline='') as file:
        writer= csv.writer(file, delimiter=';')
        writer.writerow(['номер', 'Регіон', 'КОД ДК', 'Вартість', 'название', 'Замовник', 'ссылка', 'Процедура',
                         'Статус','Дата підписання договору', 'Переможець','ЕДРПОУ','Имя','Email','Телефон',
                         'участник1','ЕДРПОУ уч1','участник2','ЕДРПОУ уч2','участник3',
                         'ЕДРПОУ уч3','участник4','ЕДРПОУ уч4'])
        for item in items:

            writer.writerow([item['number'], item['region'],item['code DK'], item['value'], item['title'], item['zamovnik'],
                             item['link'], item['procedure'],item['status'],item['date of contract'],item['award'],
                             item['EDRPOU'],item['contact'],item['e-mail'],item['telephone'],
                            item['uchastniki'][0],item['uchastniki'][1],item['uchastniki'][2],item['uchastniki'][3],
                             item['uchastniki'][4], item['uchastniki'][5], item['uchastniki'][6], item['uchastniki'][7]])


def get_html(url, params):
    a = S.get(url, headers=HEADERS, params=params)
    return a

def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination=soup.find_all('a', class_='zk-pagination__link')
    if pagination:
        return int(pagination[-2].get_text())
    else:
        return 1


def get_link_cabinet(url):
    html=get_html(url,params=None)
    if html.status_code == 200:
        soup=BeautifulSoup(html.text, 'html.parser')
        link_cabinet=soup.find('a',class_='zk-button zk-button_theme_green h-mb-25').get('href')
    return link_cabinet

def get_content_page(url):

    html = get_html(url,params=None)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
    return soup
def get_dk(soup):
    dk_code=soup.find('span',class_='qa_classifier_descr_code').get_text(strip=True)
    dk_descr=soup.find('span',class_='qa_classifier_descr_primary').get_text(strip=True)
    return (dk_code+' '+dk_descr)

def get_uchastniki(soup,award):
    uchastniki = []
    table=soup.find('table', class_='b-items-table b-items-table_table_auto b-items-table_theme_light qa_all_members')
    if table:
        items=table.find_all('tr', class_='b-items-table__row')

        for item in items:
            a=item.find('p', class_='h-mb-10')
            b=item.find('div',class_='h-mb-5 qa_egrpou')
            if a and a.get_text(strip=True)!=award:
                uchastniki.append(a.get_text(strip=True))
                uchastniki.append(b.get_text(strip=True))
    while len(uchastniki)<8:
        uchastniki.append('')
    return uchastniki
def get_region(soup):
    region=soup.find('span',class_='h-address-formatter qa_state_merchant_address_region').get_text(strip=True)
    return region
def get_procedure(soup):
    procedure=soup.find('div', class_='b-purchase-label b-purchase-label_theme_light-blue b-purchase-label_type_with_indent qa_purchase_procedure').get_text(strip=True)
    return procedure
def get_status(soup):
    status=soup.find('span', class_='qa_tender_status').get_text(strip=True)
    return status
def get_contract(soup):#на странице тендера нет такой инфі. нужно парсить еще 1 страницу.
    contract=' '
    return contract
def get_zamovnik(soup):
    code_zamovnik=soup.find('span', class_='zk-definition-list__item-text qa_state_merchant_EDRPOU').get_text(strip=True)
    zamovnik=soup.find('span', class_='zk-definition-list__item-text qa_state_merchant_name').get_text(strip=True)
    return code_zamovnik+' '+zamovnik
def get_award(soup):
    award=soup.find('div', class_='qa_award_item h-mb-10').get_text(strip=True)
    return award
def get_EDRPOU(soup):
    edrpou=soup.find('div', class_='h-mb-5 qa_egrpou').get_text(strip=True)
    return edrpou
def get_contact(soup):
    contact=soup.find('div', class_='h-mb-5 qa_name')
    if contact:
        return  contact.get_text(strip=True)
def get_email(soup):
    email = soup.find('div', class_='h-mb-5 qa_email')
    if email:
        return email.get_text(strip=True)
def get_telephone(soup):
    telephone=soup.find('div', class_='h-mb-5 qa_phone')
    if telephone:
        return telephone.get_text(strip=True)



def get_value(soup):
    value=soup.find('span', class_='qa_buget').get_text(strip=True)
    return value
def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='zk-state-list__row qa_state_purchase_list')
    tenders = []
    for item in items:
        global COUNTER
        COUNTER+=1
        print(f'Parsing tender {COUNTER}')
        link=item.find('a', class_='h-break-word qa_title_link').get('href')
        new_link = get_link_cabinet(link)
        soup_content=get_content_page(new_link)
        link_list = []
        if soup_content.find('a', class_='zk-button zk-button_theme_green qa_lot_button'):
            for lot in soup_content.find_all('a', class_='zk-button zk-button_theme_green qa_lot_button'):
                link_list.append('https://my.zakupki.prom.ua'+lot.get('href'))
        if len(link_list)>0:
            for link in link_list:
                soup_content = get_content_page(link)
                award = get_award(soup_content)
                dk=get_dk(soup_content)

                tenders.append({
                    'number': COUNTER,
                    'region':get_region(soup_content),
                    'code DK':dk,
                    'value':get_value(soup_content),
                    'zamovnik':get_zamovnik(soup_content),
                    'title': item.find('a', class_='h-break-word qa_title_link').get_text(strip=True),
                    'link': link,
                    'procedure': get_procedure(soup_content),
                    'status':get_status(soup_content),
                    'date of contract':get_contract(soup_content),
                    'award': award,
                    'EDRPOU':get_EDRPOU(soup_content),
                    'contact':get_contact(soup_content),
                    'e-mail':get_email(soup_content),
                    'telephone':get_telephone(soup_content),
                    'uchastniki': get_uchastniki(soup_content, award)
                    })
        else:#улучшить конструкцию и помнять код дк
            award=get_award(soup_content)
            dk = get_dk(soup_content)
            if dk != ' ':
                tenders.append({
                    'number': COUNTER,
                    'region':get_region(soup_content),
                    'code DK':dk,
                    'value':get_value(soup_content),
                    'zamovnik':get_zamovnik(soup_content),
                    'title': item.find('a', class_='h-break-word qa_title_link').get_text(strip=True),
                    'link': link,
                    'procedure': get_procedure(soup_content),
                    'status':get_status(soup_content),
                    'date of contract':get_contract(soup_content),
                    'award': award,
                    'EDRPOU':get_EDRPOU(soup_content),
                    'contact':get_contact(soup_content),
                    'e-mail':get_email(soup_content),
                    'telephone':get_telephone(soup_content),
                    'uchastniki': get_uchastniki(soup_content, award)
            })
    return tenders

def parse():
    html = get_html(URL, params=None)
    if html.status_code == 200:
        tenders=[]
        pages_count=get_pages_count(html.text)
        for page in range(1,  2):
            print(f'Parsing page {page}')
            html=get_html(URL, params={'p':page})
            tenders.extend(get_content(html.text))
        save_file(tenders,FILE)
        os.startfile(FILE)
    else:
        print('Error')

start_time = time.time()
parse()
print("--- %s seconds ---" % (time.time() - start_time))