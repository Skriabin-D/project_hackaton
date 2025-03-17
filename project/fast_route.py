'''
Построение таблицы всех возможных маршрутов
'''
import networkx as nx
from graphs import graph

def calculate_path_duration(G, path):
    '''
    Calculate total duration of a path in minutes.
    :param G: nx.DiGraph
    :param path: list
    :return: int
    '''
    total_duration = 0
    for i in range(len(path) - 1):
        edge_data = G.get_edge_data(path[i], path[i + 1])
        duration = edge_data.get('duration')
        if duration == 'Не указана' or duration is None:
            return None
        total_duration += duration
    return total_duration

def find_shortest_paths(depart_town, arrive_town, date):
    '''
    Find and rank all paths by duration.
    :param depart_town: str
    :param arrive_town: str
    :param date: str
    :return: None
    '''
    # Build the graph
    G = graph(depart_town, arrive_town, date)
    if G is None or len(G.nodes) == 0:
        print("Ошибка: граф не создан или пустой.")
        return

    # Get all station codes for departure and arrival towns
    depart_stations = [n for n, d in G.nodes(data=True) if d.get('name_city') == depart_town]
    arrive_stations = [n for n, d in G.nodes(data=True) if d.get('name_city') == arrive_town]

    if not depart_stations or not arrive_stations:
        print("Ошибка: не найдены станции для городов отправления или прибытия.")
        return

    # Find all possible paths between any departure and arrival stations
    all_paths = []
    for start in depart_stations:
        for end in arrive_stations:
            try:
                paths = list(nx.all_simple_paths(G, source=start, target=end))
                for path in paths:
                    duration = calculate_path_duration(G, path)
                    if duration is not None:
                        all_paths.append((path, duration))
            except nx.NetworkXNoPath:
                continue

    if not all_paths:
        print("Нет доступных путей между городами.")
        return

    # Sort paths by duration
    sorted_paths = sorted(all_paths, key=lambda x: x[1])

    # Display results
    print(f"\nНайдено {len(sorted_paths)} маршрутов между {depart_town} и {arrive_town} на {date}:")
    for i, (path, duration) in enumerate(sorted_paths, 1):
        print(f"\nМаршрут {i}: {duration} минут")
        for j in range(len(path) - 1):
            start_node = G.nodes[path[j]]
            end_node = G.nodes[path[j + 1]]
            edge_data = G.get_edge_data(path[j], path[j + 1])
            # Safely access 'date' and 'cost' with defaults if missing
            date_info = edge_data.get('date', 'Не указана')
            cost_info = edge_data.get('cost', 'Не указана')
            print(f"  {start_node['name_station']} -> {end_node['name_station']}: "
                  f"{edge_data['duration']} мин, {edge_data['transport_type']}, "
                  f"дата: {date_info}, стоимость: {cost_info}")

