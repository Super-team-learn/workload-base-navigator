from random import randint
import math
import requests
import json

# API-ключи
key = 'ed3b168b-3bc9-4a90-b03b-13df2aece788'  # 2GIS Public Transport API


def station_weight(x, n):
    '''
    Функция весов для остановок в зависимости их позиции по маршруту
    :param x: Порядковый номер остановки
    :param n: Общее количество остановок
    :return: Вес остановки
    '''
    return math.log(n - x + 1, 10)


def get_routes(pts):
    '''
    Получение списка всех возможных маршрутов
    :param pts: Объект точек начала и конца
    :return: Список маршрутов в формате 2GIS Public Transport API
    '''
    # Запрос к 2GIS Public Transport API
    data = requests.post(f'https://routing.api.2gis.com/public_transport/2.0?key={key}',
                         headers={'Content-Type': 'application/json'},
                         json={
                             "locale": "ru",
                             "source":
                                 {
                                     "name": "Точка А",
                                     "point":
                                         {
                                             "lat": pts[0]['lat'],
                                             "lon": pts[0]['lon']
                                         }
                                 },
                             "target":
                                 {
                                     "name": "Точка Б",
                                     "point":
                                         {
                                             "lat": pts[1]['lat'],
                                             "lon": pts[1]['lon']
                                         }
                                 },
                             "transport": ["bus", "tram", "trolleybus"]
                         }).json()

    routes = []
    for route in data:
        if route['pedestrian']:  # Выставляем нулевую загруженность для пешеходных маршрутов
            route['workload'] = 0
            continue
        movements = []
        for mov in route['movements']:
            if mov['type'] == 'walkway':  # Выставляем нулевую загруженность для пешеходной части маршрута
                mov['workload'] = 0
                continue
            stations = mov['platforms']
            # Если на маршруте не встретиться ни одной остановки
            if not stations:
                mov['workload'] = 0
                continue

            stations = stations['names']

            stations.insert(0, mov['waypoint']['name'])  # Начальная станция
            new_platforms = []
            # Переоформляем стиль блока platforms
            for station in stations:
                new_platforms.append({
                    'name': station,
                    'workload': None
                })
            mov['platforms'] = new_platforms
            stations = mov['platforms']
            # Определяем загруженность каждой из остановки
            for q in range(len(stations)):
                stations[q]['name'] = stations[q]['name'].replace(' (по требованию)', '')
                workload = requests.post('http://127.0.0.1:8001/count_people', json={'station_name': str(max(10, ord(stations[q]['name'][0].upper()) - ord('А') + 1)), 'time':None}).json()
                workload = workload['number_of_people']
                #workload = randint(0, 60) / 10
                workload *= station_weight(q, len(stations))  # Используем функцию веса остановки
                stations[q]['workload'] = workload
            workloads = tuple(x['workload'] for x in stations)
            # Берётся среднее по загруженности промежуточных станций и прибавляется время пути
            mov['workload'] = sum(workloads) / len(workloads) + mov['moving_duration'] / 60
            movements.append(mov)
        route['movements'] = movements
        # Рассчитываем общую загруженность маршрута
        route['workload'] = sum([i['workload'] for i in movements]) / len(movements)
        routes.append(route)

    routes.sort(key=lambda x: x['workload']) # Отсортировать список маршрутов по загруженности
    return routes

# Подгрузить список маршрутов Московского транспорта
'''with open('transport_routes.json', 'r', encoding='utf-8') as f:
    stations_info = json.load(f)'''


def get_past_routes(routes_names, station, next_station):
    '''
    Получить предыдущие остановки (были пройдены до той, на которой хочет сесть пользователь)
    :param routes_names: Номер маршрута
    :param station: Станция маршрута
    :param next_station: Следующая станция маршрута (для определения направления маршрута)
    :return: Список маршрутов
    '''
    routes = []
    for i in routes_names:
        stations = [q for q in stations_info if q['station'].split(' ')[0] == i][0]['route']
        if stations.index(station) - stations.index(next_station) > 0:
            stations = reversed(stations)
        result_stations = []
        minutes_ = 3
        for q in range(min(stations.index(station), 10), -1, -1):
            # workload = requests.post('http://127.0.0.1:8000/count_people', json={'station_name': q, 'time': datetime.now() - timedelta(minutes=minutes_)}).json()
            # workload = workload['number_of_people']
            workload = randint(0, 60) / 10
            workload *= station_weight(q, min(stations.index(station), 10))
            result_stations.append({'station': stations[q], 'workload': workload})
            minutes_ += 3
        route = i
        workloads = [x['workload'] for x in result_stations]
        route['workload'] = sum(workloads) / len(workloads)
        routes.append(route)
    return routes

get_routes([{'lat': 55.757671, 'lon':37.616396}, {'lat': 55.702305, 'lon':37.529068}])
