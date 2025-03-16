import requests
import networkx as nx
from datetime import datetime

from api_request import path

# Универсальная функция для извлечения данных с учетом возможных вариантов полей
def get_station_info(segment, keys):
    for key in keys:
        value = segment.get(key)
        if value:
            code = value.get('code')
            title = value.get('title')
            if code and title:
                return code, title
    return None, None

def graph(depart_town, arrive_town, date):
    G = nx.Graph()
    url = path(depart_town, arrive_town, date)

    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()
    if 'segments' not in data:
        return None

    from_city = data['search']['from']['title']
    fmt = "%Y-%m-%dT%H:%M:%S%z"

    for segment in data['segments']:
        # Извлекаем данные о станции отправления и прибытия
        from_station_code, from_station = get_station_info(segment, ['from', 'departure_from', 'station_from', 'location_from'])
        to_station_code, to_station = get_station_info(segment, ['to', 'arrival_to', 'station_to', 'location_to'])

        departure_data = segment.get('departure')
        arrival_data = segment.get('arrival')
        transport_type = segment.get('thread', {}).get('transport_type')
        cost = segment.get('tickets', [{}])[0].get('price', {}).get('whole', 'Не указана')

        if from_station_code and from_station and to_station_code and to_station:
            # Добавляем станции в граф
            G.add_node(from_station_code, name_station=from_station, name_city=from_city)
            G.add_node(to_station_code, name_station=to_station, name_city=arrive_town)

            # Вычисляем длительность пути
            if departure_data and arrival_data:
                departure_time = datetime.strptime(departure_data, fmt)
                arrival_time = datetime.strptime(arrival_data, fmt)
                duration = (arrival_time - departure_time).seconds // 60
            else:
                duration = None

            # Добавляем обычное ребро в граф
            G.add_edge(from_station_code, to_station_code,
                       date=departure_data or 'Не указана',
                       duration=duration or 'Не указана',
                       cost=cost,
                       transport_type=transport_type or 'Не указан')

            # Обработка пересадок
            if segment.get('has_transfers', False):
                for transfer in segment.get('details', []):
                    transfer_from_code, transfer_from_station = get_station_info(transfer, ['from', 'departure_from', 'station_from', 'location_from'])
                    transfer_to_code, transfer_to_station = get_station_info(transfer, ['to', 'arrival_to', 'station_to', 'location_to'])

                    transfer_departure = transfer.get('departure')
                    transfer_arrival = transfer.get('arrival')

                    if transfer_from_code and transfer_to_code and transfer_departure and transfer_arrival:
                        transfer_departure_time = datetime.strptime(transfer_departure, fmt)
                        transfer_arrival_time = datetime.strptime(transfer_arrival, fmt)
                        transfer_duration = (transfer_arrival_time - transfer_departure_time).seconds // 60

                        # Добавляем станции пересадки в граф
                        if transfer_from_code not in G:
                            G.add_node(transfer_from_code, name_station=transfer_from_station or f"Пересадка ({transfer_from_code})")
                        if transfer_to_code not in G:
                            G.add_node(transfer_to_code, name_station=transfer_to_station or f"Пересадка ({transfer_to_code})")

                        # Добавляем ребро пересадки в граф
                        G.add_edge(transfer_from_code, transfer_to_code, duration=transfer_duration)

    return G

# ДАЛЕЕ ЧЕРНОВИК ГДЕ ВСЕ ВЫВОДИТСЯ!! НЕ УДОЛЯЙТЕ!

# import requests
# import networkx as nx
# import matplotlib.pyplot as plt
# from datetime import datetime

# from api_request import path

# # Универсальная функция для извлечения данных с учетом возможных вариантов полей
# def get_station_info(segment, keys):
#     for key in keys:
#         value = segment.get(key)
#         if value:
#             code = value.get('code')
#             title = value.get('title')
#             if code and title:
#                 return code, title
#     return None, None

# def main():
#     G = nx.Graph()

#     depart_town = input('Введите город отправления: ')
#     arrive_town = input('Введите город прибытия: ')
#     date = input('Введите дату отправления (в формате ГГГГ-ММ-ДД): ')

#     url = path(depart_town, arrive_town, date)
#     print(url)

#     response = requests.get(url)
#     if response.status_code != 200:
#         print(f"Ошибка: {response.status_code}, {response.text}")
#         return

#     data = response.json()
#     if 'segments' not in data:
#         print("Нет доступных маршрутов на выбранную дату.")
#         return

#     from_city = data['search']['from']['title']
#     fmt = "%Y-%m-%dT%H:%M:%S%z"
#     processed_routes = 0

#     for segment in data['segments']:
#         # Извлекаем данные о станции отправления
#         from_station_code, from_station = get_station_info(segment, ['from', 'departure_from', 'station_from', 'location_from'])
#         to_station_code, to_station = get_station_info(segment, ['to', 'arrival_to', 'station_to', 'location_to'])

#         departure_data = segment.get('departure')
#         arrival_data = segment.get('arrival')
#         transport_type = segment.get('thread', {}).get('transport_type')
#         cost = segment.get('tickets', [{}])[0].get('price', {}).get('whole', 'Не указана')

#         if from_station_code and from_station and to_station_code and to_station:
#             processed_routes += 1

#             # === ОТЛАДОЧНЫЙ ВЫВОД ===
#             print(f"Добавляю маршрут #{processed_routes}: {from_station} ({from_station_code}) → {to_station} ({to_station_code})")

#             # Добавляем станции в граф
#             G.add_node(from_station_code, name_station=from_station, name_city=from_city)
#             G.add_node(to_station_code, name_station=to_station, name_city=arrive_town)

#             # Вычисляем длительность пути
#             if departure_data and arrival_data:
#                 departure_time = datetime.strptime(departure_data, fmt)
#                 arrival_time = datetime.strptime(arrival_data, fmt)
#                 duration = (arrival_time - departure_time).seconds // 60
#             else:
#                 duration = None

#             # Добавляем обычное ребро в граф
#             G.add_edge(from_station_code, to_station_code,
#                        date=departure_data or 'Не указана',
#                        duration=duration or 'Не указана',
#                        cost=cost,
#                        transport_type=transport_type or 'Не указан')

#             # === ОБРАБОТКА ПЕРЕСАДОК ===
#             if segment.get('has_transfers', False):
#                 print(f"Найдены пересадки для маршрута {from_station_code} → {to_station_code}")

#                 for transfer in segment.get('details', []):
#                     transfer_from_code, transfer_from_station = get_station_info(transfer, ['from', 'departure_from', 'station_from', 'location_from'])
#                     transfer_to_code, transfer_to_station = get_station_info(transfer, ['to', 'arrival_to', 'station_to', 'location_to'])

#                     transfer_departure = transfer.get('departure')
#                     transfer_arrival = transfer.get('arrival')

#                     if transfer_from_code and transfer_to_code and transfer_departure and transfer_arrival:
#                         transfer_departure_time = datetime.strptime(transfer_departure, fmt)
#                         transfer_arrival_time = datetime.strptime(transfer_arrival, fmt)
#                         transfer_duration = (transfer_arrival_time - transfer_departure_time).seconds // 60

#                         # === ОТЛАДОЧНЫЙ ВЫВОД ===
#                         print(f"Добавляю пересадку: {transfer_from_code} → {transfer_to_code}, длительность: {transfer_duration} мин")

#                         # Добавляем станции пересадки в граф
#                         if transfer_from_code not in G:
#                             G.add_node(transfer_from_code, name_station=transfer_from_station or f"Пересадка ({transfer_from_code})")
#                         if transfer_to_code not in G:
#                             G.add_node(transfer_to_code, name_station=transfer_to_station or f"Пересадка ({transfer_to_code})")

#                         # Добавляем ребро пересадки в граф
#                         G.add_edge(transfer_from_code, transfer_to_code, duration=transfer_duration)

#     # === ВЫВОД ГРАФА В ТЕРМИНАЛ ===
#     print("\n=== ВЫВОД ГРАФА В ТЕРМИНАЛ ===")
#     print("Узлы графа:")
#     for node, data in G.nodes(data=True):
#         print(f"{node}: {data}")

#     print("\nРёбра графа:")
#     for u, v, data in G.edges(data=True):
#         print(f"{u} -> {v}: {data}")

#     # === ПОСТРОЕНИЕ ГРАФА ===
#     pos = nx.spring_layout(G)
#     labels = {node: f"{data['name_station']}\n({node})" for node, data in G.nodes(data=True)}
#     edge_labels = {
#         (u, v): f"{d.get('duration', '—')} мин\n{d.get('cost', '—')} ₽\n{d.get('transport_type', '')}" 
#         for u, v, d in G.edges(data=True)
#     }

#     nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=1000, font_size=10)
#     nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

#     plt.title(f"Маршрут из {depart_town} в {arrive_town}")
#     plt.show()

#     print(f"\n✅ Добавлено маршрутов: {processed_routes}")

# if __name__ == '__main__':
#     main()
