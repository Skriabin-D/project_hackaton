'''
Файл, в котором происходит построение графа  по данным полученным от API
'''
import requests
import networkx as nx
from datetime import datetime


from api_request import path


def get_station_info(segment, keys):
    '''
    Универсальная функция для извлечения данных с учетом возможных вариантов полей
    :param segment: dict
    :param keys: any
    :return: code, title or None
    '''
    for key in keys:
        value = segment.get(key)
        if value:
            code = value.get('code')
            title = value.get('title')
            if code and title:
                return code, title
    return None, None

def calculate_duration(departure, arrival, fmt="%Y-%m-%dT%H:%M:%S%z"):
    '''
    Вычисляет продолжительность в минутах между departure и arrival.
    :param departure: Any
    :param arrival: Any
    :param fmt: str
    :return: int or None
    '''
    if departure and arrival:
        dep_time = datetime.strptime(departure, fmt)
        arr_time = datetime.strptime(arrival, fmt)
        return (arr_time - dep_time).seconds // 60
    return None

def graph(depart_town, arrive_town, date):
    '''
    Функция построения графа
    :param depart_town: string
    :param arrive_town: string
    :param date: string
    :return: nx.DiGraph
    '''
    G = nx.DiGraph()  # Используем направленный граф для учета последовательности

    url = path(depart_town, arrive_town, date)
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()
    if 'segments' not in data:
        return None

    from_city = data['search']['from']['title']
    to_city = data['search']['to']['title']
    fmt = "%Y-%m-%dT%H:%M:%S%z"

    for segment_idx, segment in enumerate(data['segments']):
        # Извлекаем данные о станции отправления и прибытия
        from_station_code, from_station = get_station_info(segment, ['departure_from', 'from', 'station_from'])
        to_station_code, to_station = get_station_info(segment, ['arrival_to', 'to', 'station_to'])

        departure_data = segment.get('departure')
        arrival_data = segment.get('arrival')
        transport_type = segment.get('thread', {}).get('transport_type', 'Не указан')
        cost = segment.get('tickets', [{}])[0].get('price', {}).get('whole', 'Не указана')

        if not (from_station_code and to_station_code):
            continue  # Пропускаем некорректные сегменты

        # Добавляем узлы с атрибутами
        G.add_node(from_station_code, name_station=from_station, name_city=from_city)
        G.add_node(to_station_code, name_station=to_station, name_city=to_city)

        # Прямой маршрут (без пересадок)
        if not segment.get('has_transfers', False):
            duration = calculate_duration(departure_data, arrival_data)
            if duration is None:
                continue  # Пропускаем, если нет времени

            G.add_edge(from_station_code, to_station_code,
                       duration=duration,
                       date=departure_data,
                       cost=cost,
                       transport_type=transport_type,
                       segment_id=segment_idx)
        else:
            # Обработка пересадок
            last_code = from_station_code
            last_arrival_time = departure_data
            details = segment.get('details', [])

            for detail in details:
                if 'is_transfer' in detail:
                    # Это пересадка
                    transfer_from_code, transfer_from_station = get_station_info(detail, ['transfer_from'])
                    transfer_to_code, transfer_to_station = get_station_info(detail, ['transfer_to'])
                    transfer_duration = detail.get('duration')

                    if not (transfer_from_code and transfer_to_code):
                        continue

                    # Добавляем узлы пересадки
                    transfer_city = detail.get('transfer_point', {}).get('title', 'Не указан')
                    G.add_node(transfer_from_code, name_station=transfer_from_station, name_city=transfer_city)
                    G.add_node(transfer_to_code, name_station=transfer_to_station, name_city=transfer_city)

                    # Вычисляем duration для пересадки
                    if transfer_duration:
                        duration_minutes = transfer_duration // 60
                    else:
                        duration_minutes = 0  # Минимальная длительность пересадки

                    # Связываем предыдущий узел с началом пересадки
                    if last_arrival_time and detail.get('departure'):
                        duration_to_transfer = calculate_duration(last_arrival_time, detail.get('departure'))
                    else:
                        duration_to_transfer = duration_minutes

                    if duration_to_transfer is not None:
                        G.add_edge(last_code, transfer_from_code,
                                   duration=duration_to_transfer,
                                   transport_type="Пересадка",
                                   segment_id=segment_idx)

                    # Добавляем ребро самой пересадки
                    G.add_edge(transfer_from_code, transfer_to_code,
                               duration=duration_minutes,
                               transport_type="Пересадка",
                               segment_id=segment_idx)

                    last_code = transfer_to_code
                    last_arrival_time = detail.get('arrival')
                else:
                    # Это участок маршрута
                    detail_from_code, detail_from_station = get_station_info(detail, ['from'])
                    detail_to_code, detail_to_station = get_station_info(detail, ['to'])
                    detail_departure = detail.get('departure')
                    detail_arrival = detail.get('arrival')
                    detail_duration = detail.get('duration')
                    detail_transport = detail.get('thread', {}).get('transport_type', 'Не указан')

                    if not (detail_from_code and detail_to_code):
                        continue

                    detail_from_city = detail.get('from', {}).get('title', 'Не указан')
                    detail_to_city = detail.get('to', {}).get('title', 'Не указан')

                    # Используем коды станций из departure_from и arrival_to, если они есть
                    actual_from_code = get_station_info(detail, ['departure_from'])[0] or detail_from_code
                    actual_to_code = get_station_info(detail, ['arrival_to'])[0] or detail_to_code

                    G.add_node(actual_from_code, name_station=detail_from_station, name_city=detail_from_city)
                    G.add_node(actual_to_code, name_station=detail_to_station, name_city=detail_to_city)

                    # Вычисляем duration
                    duration = calculate_duration(detail_departure, detail_arrival)
                    if duration is None and detail_duration:
                        duration = detail_duration // 60

                    if duration is not None:
                        G.add_edge(actual_from_code, actual_to_code,
                                   duration=duration,
                                   date=detail_departure,
                                   transport_type=detail_transport,
                                   segment_id=segment_idx)

                    # Связываем с предыдущим узлом
                    if last_code != actual_from_code:
                        if last_arrival_time and detail_departure:
                            duration_between = calculate_duration(last_arrival_time, detail_departure)
                        else:
                            duration_between = 0

                        if duration_between is not None:
                            G.add_edge(last_code, actual_from_code,
                                       duration=duration_between,
                                       transport_type="Пересадка",
                                       segment_id=segment_idx)

                    last_code = actual_to_code
                    last_arrival_time = detail_arrival

            # Связываем последнюю пересадку с конечной точкой
            if last_code != to_station_code:
                duration_to_end = calculate_duration(last_arrival_time, arrival_data)
                if duration_to_end is not None:
                    G.add_edge(last_code, to_station_code,
                               duration=duration_to_end,
                               transport_type="После пересадки",
                               segment_id=segment_idx)

    # Удаляем петли и проверяем связность
    G.remove_edges_from(nx.selfloop_edges(G))

    # Проверяем, что все ребра имеют duration
    for u, v, d in G.edges(data=True):
        if 'duration' not in d or d['duration'] is None:
            G.remove_edge(u, v)

    return G if nx.is_weakly_connected(G) else None

