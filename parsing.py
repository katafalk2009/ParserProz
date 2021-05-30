"""
Module with synchronous functions for parsing tender web pages.
"""
import re
from bs4 import BeautifulSoup


def parse_page(html, url, counter):
    """
    Main parsing function. Return dictionary with all parsed data.
    :param html:
    :param url:
    :param counter: global counter
    :return: Dictionary
    """
    soup = BeautifulSoup(html, 'html.parser')
    tender_dict = {
        'number': counter,
        'region': get_region(soup),
        'code DK': soup.find('div', class_='zk-purchase-label zk-purchase-label_theme_light-blue zk-purchase'
                                           '-label_type_with_indent').get_text(strip=True).split('\n')[1].lstrip(),
        'value': get_value(soup),
        'organizer': soup.find('div', class_='zk-definition-list__item-value qa_merchant_name').get_text(strip=True),
        'title': get_title(soup),
        'link': url,
        'procedure': soup.find('span', class_='zk-purchase-label zk-purchase-label_theme_light-blue zk-purchase'
                                              '-label_type_with_indent qa_procedure_type_tag').get_text(strip=True),
        'award': get_winner(soup)[0],
        'EDRPOU': get_winner(soup)[1],
        'contact': get_winner(soup)[2],
    }
    return tender_dict


def get_value(soup):
    """
    Returns expected cost of tender.
    :param soup:
    :return:
    """
    a = soup.find('div', class_='zk-purchase-price qa_price').get_text(strip=True)
    c = a[:a.find(',')]
    value = ''.join([i for i in c if i.isdigit()])
    return value


def get_region(soup):
    """
    Return tenders region.
    :param soup:
    :return:
    """
    address = soup.find('div', class_='zk-definition-list__item-value qa_address').get_text(strip=True)
    a = address.split(', ')
    return a[2]


def get_winner(soup):
    """
    Find all tender winner data. Return it as a tuple: name, legal code, contacts.
    :param soup:
    :return: Tuple
    """
    tables = soup.find_all('tr', class_='zk-table-list__row')
    winner_table = None
    for table in tables:
        a = table.find_all('td', class_='zk-table-list__cell')
        for i in a:
            if i.get_text(strip=True) == 'Статус:переможець':
                winner_table = table
    winner_name = winner_table.find(attrs={"add-popup-class": "h-width-200 h-break-word"})['label']
    winner_contacts = [i.get_text(strip=True) for i in winner_table.find_all('div', class_='h-mb-5')]
    winner_edrpou = winner_table.find(string=re.compile('ЄДРПОУ:')).find_next().string
    return winner_name, winner_edrpou, winner_contacts


def get_title(soup):
    """
    Return title of tender. Sometimes there can be bad symbols, which can't be encoded while saving to file.
    So it excludes bad symbols and return title without them.
    :param soup:
    :return:
    """
    title = soup.find('h1', class_='h-break-word').get_text(strip=True)
    try:
        title.encode('cp1251')
    except UnicodeEncodeError as e:
        title = title[:e.args[2]]+title[e.args[2]+1:]
    return title
