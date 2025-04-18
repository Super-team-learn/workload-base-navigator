from random import randint
import math
import requests
import json

key = 'ed3b168b-3bc9-4a90-b03b-13df2aece788'
def station_weight(x, n): #Функция весов для остановок в зависимости их позиции по маршруту
    return math.log(n - x + 1, 1.2)

def get_routes(pts):
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
        if route['pedestrian']:
            route['workload'] = 0
            continue
        movements = []
        for mov in route['movements']:
            if mov['type'] == 'walkway':
                mov['workload'] = 0
                continue
            stations = mov['platforms']
            if not stations:
                mov['workload'] = 0
                continue

            stations = stations['names']

            stations.insert(0, mov['waypoint']['name'])  # Начальная станция
            new_platforms = []
            for station in stations:
                new_platforms.append({
                    'name': station,
                    'workload': None
                })
            mov['platforms'] = new_platforms
            stations = mov['platforms']
            for q in range(len(stations)):
                stations[q]['name'] = stations[q]['name'].replace(' (по требованию)', '')
                workload = requests.post('http://127.0.0.1:8001/count_people', json={'station_name': stations[q]['name']}).json()
                workload = workload['number_of_people']
                workload *= station_weight(q, len(stations))
                stations[q]['workload'] = workload
            workloads = tuple(x['workload'] for x in stations)
            mov['workload'] = sum(workloads) / len(workloads)  # Берётся среднее по загруженности промежуточных станций
            movements.append(mov)
        route['movements'] = movements
        route['workload'] = sum([i['workload'] for i in movements]) / len(movements)
        routes.append(route)

    routes.sort(key=lambda x: x['workload'])
    return routes
