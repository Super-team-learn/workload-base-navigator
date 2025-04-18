from random import randint

import requests
import json

key = 'ed3b168b-3bc9-4a90-b03b-13df2aece788'


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
            for q in stations:
                q['name'] = q['name'].replace(' (по требованию)', '')
                # workload = requests.post('http://127.0.0.1:8000/count_people', json={'station_name': q}).json()
                # workload = workload['number_of_people']
                workload = randint(0, 60) / 10
                q['workload'] = workload
            print(stations)
            workloads = tuple(x['workload'] for x in stations)
            mov['workload'] = sum(workloads) / len(workloads)  # Берётся среднее по загруженности промежуточных станций
            movements.append(mov)
        route['movements'] = movements
        route['workload'] = sum([i['workload'] for i in movements]) / len(movements)
        routes.append(route)

    return routes
