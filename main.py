from fastapi import FastAPI, Response, status
import re
import requests

# Пути
from routes.get_routes import get_routes

# API-ключи
GEOCODER_API_KEY = '6802813d0f1de583834110rqa501dcf'

app = FastAPI()


@app.get("/coords/")
async def get_routes_route(pnt_a, pnt_b, response: Response):
    '''
    Получить список маршрутов с просчитанной оптимальностью (учитывает загруженность и время маршрута)
    :param pnt_a: Начальная точка маршрута
    :param pnt_b: Конечная точка маршрута
    :param response: Объект запроса
    :return: Модифицированный JSON-объект на базе 2GIS Public Transport API
    '''

    coords_pattern = re.compile(r'[0-9]{1,3}.[0-9]*,\s?[0-9]{1,3}.[0-9]*')  # RegExp для определения координат

    # Инициализация списка точек
    pts = [
        {
            'value': pnt_a
        },
        {
            'value': pnt_b
        }
    ]

    # Приведение всех точек к виду координат
    for pnt in pts:
        pnt['type'] = 'coordinates' if coords_pattern.match(pnt['value']) else 'address'

        if pnt['type'] == 'coordinates':
            # Форматируем координаты
            pnt['value'] = tuple(map(float, pnt['value'].split(',')))
            pnt['value'] = {
                'lat': pnt['value'][0],
                'lon': pnt['value'][1]
            }
        else:
            # Получаем кооридинаты при помоши Geocoder API
            suggest_response = requests.get('https://geocode.maps.co/search', {
                'api_key': GEOCODER_API_KEY,
                'q': 'Россия, Москва, ' + pnt['value']
            })
            if suggest_response.status_code != 200:
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {
                    'error': 'Error in Geosuggest request'
                }
            suggest_response = suggest_response.json()
            pnt['type'] = 'coordinates'
            coords = suggest_response[0]
            pnt['value'] = {
                'lat': float(coords['lat']),
                'lon': float(coords['lon'])
            }
    pts = (pts[0]['value'], pts[1]['value'])  # Переформатируем координаты
    return get_routes(pts)


# Запуск сервиса
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
