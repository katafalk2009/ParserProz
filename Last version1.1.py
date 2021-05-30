import csv
import os
import time
import asyncio
import aiohttp
from fake_useragent import UserAgent
import random
from Parser.ParserProz.parsing import *
listoflinks = []
tenders = []
FILE = 'tenders.csv'
COUNTER = 0
ERROR_QTY = 0
PROXYLIST = open('proxie.txt').read().split('\n')
URL = 'https://zakupki.prom.ua/gov/tenders?status=6&primary_classifier=45330000-9&createdFrom=2021-05-01&createdTo=2021-05-31'


async def run():
    """
    Main function. It has 3 parts, which are synchronous relatively to each other.
    1) Getting pages urls.
    2) Asynchronously parsing pages, which consists of 20 tender urls. Getting these urls.
    3) Asynchronously parsing every tender web-page.
    :return:
    """
    async with aiohttp.ClientSession() as session:
        urls = await (get_page_urls(URL, session))
    sem = asyncio.Semaphore(50)
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(get_tenders_url(sem, url, session)) for url in urls]
        await asyncio.gather(*tasks)

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(get_tender_html(sem, url, session)) for url in listoflinks]
        await asyncio.gather(*tasks)


async def get_page_urls(url, session):
    """
    Parses initial link to find page count. Generates list of pages for further program.
    :param url:
    :param session:
    :return:
    """
    async with session.get(url, proxy="http://" + random.choice(PROXYLIST),
                           headers={'user-agent': UserAgent().random}) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        pagination = soup.find_all('a', class_='zkb-pagination__link')
        if pagination:
            pages = int(pagination[-2].get_text())
        else:
            pages = 1
    urls = [url+f'&p={page}' for page in range(1, pages+1)]
    return urls


async def get_tenders_url(sem, url, session):
    """
    Parses pages and returns list of tenders links for further program.
    :param sem:
    :param url:
    :param session:
    :return:
    """
    async with sem:
        while True:
            try:
                async with session.get(url, proxy="http://"+random.choice(PROXYLIST),
                                       headers={'user-agent': UserAgent().random}) as response:
                    print(url)
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    items = soup.find_all('div', class_='qa_state_purchase_list')
                    list_from_page = [item.find('a',
                                                class_='zkb-list__heading qa_title_link').get('href') for item in items]
                    listoflinks.extend(list_from_page)
            except Exception as e:
                global ERROR_QTY
                ERROR_QTY += 1
                print('Connection ERROR:', e, '. Retrying.')
                continue
            break


async def get_tender_html(sem, url, session):
    """
    Return html from tender web-page ready for parsing.
    :param sem:
    :param url:
    :param session:
    :return:
    """
    async with sem:
        while True:
            try:
                async with session.get(url, proxy="http://"+random.choice(PROXYLIST),
                                       headers={'user-agent': UserAgent().random}) as response:
                    html = await response.text()
                    global COUNTER
                    COUNTER += 1
                    print(url)
                    tender_dict = parse_page(html, url, COUNTER)
                    tenders.append(tender_dict)
            except Exception as e:
                print('Connection ERROR:', e, '. Retrying.')
                global ERROR_QTY
                ERROR_QTY += 1
                continue
            break


def save_file(items, path):
    """
    Saving all parsed data in file.
    :param items: List of dictionaries, with all parsed data
    :param path: String, path and name of File to save data.
    :return:
    """
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['номер', 'Регіон', 'КОД ДК', 'Вартість', 'название', 'Замовник', 'ссылка', 'Процедура',
                        'Переможець', 'ЕДРПОУ', 'Контакты'])
        for item in items:
            writer.writerow([item['number'], item['region'], item['code DK'], item['value'], item['title'],
                             item['organizer'], item['link'], item['procedure'], item['award'],
                             item['EDRPOU'], item['contact']])


start_time = time.time()

policy = asyncio.WindowsSelectorEventLoopPolicy()
asyncio.set_event_loop_policy(policy)

loop = asyncio.get_event_loop()
main = asyncio.ensure_future(run())
loop.run_until_complete(main)
save_file(tenders, FILE)
os.startfile(FILE)

print("--- %s seconds ---" % (time.time() - start_time))
