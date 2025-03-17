import requests as rq
from config import API
import json
from urllib.parse import urlencode

def town_code(town):
    '''
    Функция, возвращающая код города по его названию
    :param town: str
    :return: str
    '''
    url = 'https://suggests.rasp.yandex.net/all_suggests'

    params = {
        'part': f'{town}'
    }
    response = rq.get(url, params=params)
    data = response.json()

    return data['suggests'][0]['point_key']

def path(depart_town, arrive_town, date):
    '''
    Функция составляющая url для API запроса
    :param depart_town: str
    :param arrive_town: str
    :param date: str
    :return: str
    '''
    depart_town_code = town_code(depart_town)
    arrive_town_code = town_code(arrive_town)

    url = 'https://api.rasp.yandex.net/v3.0/search/'
    params = {
        'apikey': API,
        'from': depart_town_code,
        'to': arrive_town_code,
        'lang': 'ru_RU',
        'date': date,
        'transfers': "true"
    }
    final_url = f"{url}?{urlencode(params)}"
    return final_url