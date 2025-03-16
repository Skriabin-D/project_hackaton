import requests as rq
from config import API
import json
from urllib.parse import urlencode

def town_code(town):
    url = 'https://suggests.rasp.yandex.net/all_suggests'

    params = {
        'part': f'{town}'
    }
    response = rq.get(url, params=params)
    data = response.json()

    return data['suggests'][0]['point_key']

def path(depart_town, arrive_town, date):
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
    response = rq.get(url, params=params)
    data = response.json()
    # return data
    formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
    # return formatted_data
    final_url = f"{url}?{urlencode(params)}"
    return final_url