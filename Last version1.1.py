from bs4 import BeautifulSoup
import csv
import os
import time
import asyncio
import aiohttp
from fake_useragent import UserAgent
import random
listoflinks=[]
tenders=[]
FILE = 'tenders.csv'
COUNTER = 0
PROXYLIST = open('proxie.txt').read().split('\n')
URL = 'https://zakupki.prom.ua/gov/tenders?status=6&primary_classifier=45330000-9'
async def run():
    urls=get_page_urls(URL)
    sem = asyncio.Semaphore(50)
    async with aiohttp.ClientSession() as session:
        tasks=[asyncio.create_task(get_tenders_url(sem, url, session)) for url in urls]
        await asyncio.gather(*tasks)

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(parse_page(sem, url, session)) for url in listoflinks]
        await asyncio.gather(*tasks)

async def get_tenders_url(sem, url, session):
    async with sem:
        while True:
            try:
                async with session.get(url, proxy="http://"+random.choice(PROXYLIST),
                                       headers={'user-agent': UserAgent().random}) as response:
                    print(url)
                    body = await response.text()
                    soup = BeautifulSoup(body, 'html.parser')
                    items = soup.find_all('div', class_='qa_state_purchase_list')
                    list_from_page=[item.find('a', class_='zkb-list__heading qa_title_link').get('href') for item in items]
                    listoflinks.extend(list_from_page)
            except Exception as e:
                print(e)
                continue
            break




def get_page_urls(url):
    urls = [url+f'&p={page}' for page in range(1,50)]
    # for page in range(1, 5):
    #     print(f'Parsing page {page}')
    #     urls.append(url+f'&p={page}')
    return urls


async def parse_page(sem, link, session):
    """
    Calls all small parsing methods on a soup of 1 webpage.
    And returns dict whis is added to big list with all other pages.
    :param soup:
    :param link:
    :param item:
    :return:
    """
    async with sem:
        while True:
            try:
                async with session.get(link, proxy="http://"+random.choice(PROXYLIST),headers=HEADERS) as response:
                    body = await response.text()
                    global COUNTER
                    COUNTER+=1
                    print(link)
                    soup=BeautifulSoup(body, 'html.parser')
                    #TODO тут надо сделать нормальній новій парсер
                    #tender_dict={'title':soup.find('h1',class_='h-break-word').get_text(strip=True), 'link':link}

                    tenders.append(tender_dict)
            except Exception as e:
                print(e)
                continue
            break
def save_file(items, path):
    """
    Saving all parsed data in file.
    :param items: List of dictionaries, with all parsed data
    :param path: String, path and name of File to save data.
    :return:
    """
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['номер', 'Регіон', 'КОД ДК', 'Вартість', 'название', 'Замовник', 'ссылка', 'Процедура',
                         'Статус', 'Переможець', 'ЕДРПОУ', 'Имя', 'Email', 'Телефон'])
        for item in items:
            writer.writerow([item['number'], item['region'], item['code DK'], item['value'], item['title'],
                             item['organizer'], item['link'], item['procedure'], item['status'], item['award'],
                             item['EDRPOU'], item['contact'], item['e-mail'], item['telephone']])
start_time = time.time()
policy = asyncio.WindowsSelectorEventLoopPolicy()
asyncio.set_event_loop_policy(policy)
loop = asyncio.get_event_loop()
main = asyncio.create_task(run())
loop.run_until_complete(main)
print(len(listoflinks))
print("--- %s seconds ---" % (time.time() - start_time))
save_file(tenders,FILE)
with open(FILE, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['номер', 'Регіон'])
    for item in tenders:
        writer.writerow([item['title'], item['link']])

os.startfile(FILE)




def save_file(items, path):
    """
    Saving all parsed data in file.
    :param items: List of dictionaries, with all parsed data
    :param path: String, path and name of File to save data.
    :return:
    """
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['номер', 'Регіон', 'КОД ДК', 'Вартість', 'название', 'Замовник', 'ссылка', 'Процедура',
                         'Статус', 'Переможець', 'ЕДРПОУ', 'Имя', 'Email', 'Телефон',
                         'участник1', 'ЕДРПОУ уч1', 'участник2', 'ЕДРПОУ уч2', 'участник3',
                         'ЕДРПОУ уч3', 'участник4', 'ЕДРПОУ уч4'])
        for item in items:
            writer.writerow([item['number'], item['region'], item['code DK'], item['value'], item['title'],
                             item['organizer'], item['link'], item['procedure'], item['status'], item['award'],
                             item['EDRPOU'], item['contact'], item['e-mail'], item['telephone'],
                            item['participants'][0], item['participants'][1],
                             item['participants'][2], item['participants'][3],
                             item['participants'][4], item['participants'][5],
                             item['participants'][6], item['participants'][7]])


def get_html(url, params):
    """
    Gets HTML from url link as String, ready to be parsed.
    :param url: Link of webpage
    :param params: Different params for current webpage
    :return:
    """
    a = S.get(url, headers=HEADERS, params=params)
    return a


def get_pages_count(html):
    """
    Gets q-ty of pages from a start page to be parsed in cycle.
    :param html:
    :return: pages count as int
    """
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('a', class_='zk-pagination__link')
    if pagination:
        return int(pagination[-2].get_text())
    else:
        return 1


def get_link_cabinet(url):
    """
    Returns special link of cabinet, which is easier to parse, then usual webpage.
    :param url:
    :return:
    """
    html = get_html(url, params=None)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        link_cabinet = soup.find('button', class_='zk-button zk-button_theme_green h-mb-25').get('onclick')[13:-12]
        return link_cabinet
    else:
        print('Error')


def get_content_page(url):
    """
    Gets whole content from webpage and returns it as soup (BeautifulSoup).
    :param url:
    :return:
    """
    html = get_html(url, params=None)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        return soup
    else:
        print(html.status_code)
        return None


def get_dk(soup):
    """
    Returns concatenation of number and name of dk_code.
    :param soup:
    :return:
    """
    dk_code = soup.find('span', class_='qa_classifier_descr_code').get_text(strip=True)
    dk_descr = soup.find('span', class_='qa_classifier_descr_primary').get_text(strip=True)
    return dk_code + ' ' + dk_descr


def get_participants(soup, award):
    """
    Gets list of max 4 participant excluding winner of tender.
    :param soup:
    :param award: winner to exclude of list. It is got from another method.
    :return:
    """
    participants = []
    table = soup.find('table', class_='b-items-table b-items-table_table_auto b-items-table_theme_light qa_all_members')
    if table:
        items = table.find_all('tr', class_='b-items-table__row')
        for item in items:
            a = item.find('p', class_='h-mb-10')
            b = item.find('div', class_='h-mb-5 qa_egrpou')
            if a and a.get_text(strip=True) != award:
                participants.append(a.get_text(strip=True))
                participants.append(b.get_text(strip=True))
    while len(participants) < 8:
        participants.append('')
    return participants


def get_region(soup):
    """
    Gets region of tender.
    :param soup:
    :return:
    """
    region = soup.find('span', class_='h-address-formatter qa_state_merchant_address_region').get_text(strip=True)
    return region


def get_procedure(soup):
    """
    Gets type of procedure.
    :param soup:
    :return:
    """
    procedure = soup.find('div', class_='b-purchase-label b-purchase-label_theme_light-blue '
                                        'b-purchase-label_type_with_indent qa_purchase_procedure').get_text(strip=True)
    return procedure


def get_status(soup):
    """
    Gets status of tender.
    :param soup:
    :return:
    """
    status = soup.find('span', class_='qa_tender_status').get_text(strip=True)
    return status


def get_organizer(soup):
    """
    Gets organizer of tender as concatenation of name and code.
    :param soup:
    :return:
    """
    code_organizer = soup.find('span',
                               class_='zk-definition-list__item-text qa_state_merchant_EDRPOU').get_text(strip=True)
    name_organizer = soup.find('span',
                               class_='zk-definition-list__item-text qa_state_merchant_name').get_text(strip=True)
    return code_organizer+' '+name_organizer


def get_winner_name(soup):
    """
    Gets name of winner.
    :param soup:
    :return:
    """
    award = soup.find('div', class_='qa_award_item h-mb-10').get_text(strip=True)
    return award


def get_winner_edrpou(soup):
    """
    Gets edrpou of winner.
    :param soup:
    :return:
    """
    edrpou = soup.find('div', class_='h-mb-5 qa_egrpou').get_text(strip=True)
    return edrpou


def get_winner_person(soup):
    """
    Gets name of winner contact person.
    :param soup:
    :return:
    """
    contact = soup.find('div', class_='h-mb-5 qa_name')
    if contact:
        return contact.get_text(strip=True)


def get_winner_email(soup):
    """
    Gets email of winner contact person.
    :param soup:
    :return:
    """
    email = soup.find('div', class_='h-mb-5 qa_email')
    if email:
        return email.get_text(strip=True)


def get_winner_telephone(soup):
    """
    Gets telephone number of winner contact person.
    :param soup:
    :return:
    """
    telephone = soup.find('div', class_='h-mb-5 qa_phone')
    if telephone:
        return telephone.get_text(strip=True)


def get_value(soup):
    """
    Gets value of tender (hrivna).
    :param soup:
    :return:
    """
    value = soup.find('span', class_='qa_buget').get_text(strip=True)
    return value


def parse_page(soup, link, item):
    """
    Calls all small parsing methods on a soup of 1 webpage.
    And returns dict whis is added to big list with all other pages.
    :param soup:
    :param link:
    :param item:
    :return:
    """
    tender_dict = {
                    'number': COUNTER,
                    'region': get_region(soup),
                    'code DK': get_dk(soup),
                    'value': get_value(soup),
                    'organizer': get_organizer(soup),
                    'title': item.find('a', class_='h-break-word qa_title_link').get_text(strip=True),
                    'link': link,
                    'procedure': get_procedure(soup),
                    'status': get_status(soup),
                    'award': get_winner_name(soup),
                    'EDRPOU': get_winner_edrpou(soup),
                    'contact': get_winner_person(soup),
                    'e-mail': get_winner_email(soup),
                    'telephone': get_winner_telephone(soup),
                    'participants': get_participants(soup, get_winner_name(soup))
                    }
    return tender_dict


def get_content(html):
    """
    Calls parse_page method on 20 tenders on 1 page, also checking if it has q-ty of lots.
    :param html:
    :return:
    """
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='zk-state-list__row qa_state_purchase_list')
    tenders = []
    for item in items:
        global COUNTER
        COUNTER += 1
        print(f'Parsing tender {COUNTER}')
        link = item.find('a', class_='h-break-word qa_title_link').get('href')
        new_link = get_link_cabinet(link)
        soup_content = get_content_page(new_link)
        link_list = []
        if soup_content.find('a', class_='zk-button zk-button_theme_green qa_lot_button'):
            for lot in soup_content.find_all('a', class_='zk-button zk-button_theme_green qa_lot_button'):
                link_list.append('https://my.zakupki.prom.ua'+lot.get('href'))
        if len(link_list) > 0:
            for l in link_list:
                soup_content = get_content_page(l)
                tender_dict = parse_page(soup_content, link, item)
                tenders.append(tender_dict)
        else:
            tender_dict = parse_page(soup_content, link, item)
            tenders.append(tender_dict)
    return tenders


def parse(url):
    """
    Main function of program.
    :return:
    """
    html = get_html(url, params=None)
    for page in range(3, 4):
        print(f'Parsing page {page}')
        html = get_html(URL, params={'p': page})
    if html.status_code == 200:
        tenders = []
        pages_count = get_pages_count(html.text)
        print('Q-ty of pages: ', pages_count)
        #for page in range(1,  pages_count+1):
        for page in range(3, 4):
            print(f'Parsing page {page}')
            html = get_html(URL, params={'p': page})
            tenders.extend(get_content(html.text))
        save_file(tenders, FILE)
        os.startfile(FILE)
    else:
        print('Error')

#start_time = time.time()

#parse(URL)

#print("--- %s seconds ---" % (time.time() - start_time))
