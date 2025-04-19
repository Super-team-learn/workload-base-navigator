from random import randint
import math
import requests
import json

key = 'ed3b168b-3bc9-4a90-b03b-13df2aece788'
def station_weight(x, n): #Функция весов для остановок в зависимости их позиции по маршруту
    return math.log(n - x + 1, 10)

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
                # workload = requests.post('http://127.0.0.1:8000/count_people', json={'station_name': q}).json()
                # workload = workload['number_of_people']
                workload = randint(0, 60) / 10
                workload *= station_weight(q, len(stations))
                stations[q]['workload'] = workload
            workloads = tuple(x['workload'] for x in stations)
            mov['workload'] = sum(workloads) / len(workloads) + mov['moving_duration']/60 # Берётся среднее по загруженности промежуточных станций и прибавляется время пути
            movements.append(mov)
        route['movements'] = movements
        route['workload'] = sum([i['workload'] for i in movements]) / len(movements)
        routes.append(route)

    routes.sort(key=lambda x: x['workload'])
    return routes

with open('transport_routes.json', 'r', encoding='utf-8') as f:
    stations_info = json.load(f)
def get_past_routes(routes_names, station, next_station):
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
            result_stations.append({'station':stations[q], 'workload': workload})
            minutes_ += 3
        route = i
        workloads = [x['workload'] for x  in result_stations]
        route['workload'] = sum(workloads)/len(workloads)
        routes.append(route)
    return routes



