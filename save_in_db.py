import requests
import psycopg2
import time
from datetime import datetime

conn = psycopg2.connect(
    dbname="dbname",
    user="username",
    password="password",
    host="localhost"
)
cursor = conn.cursor()
all_stations = ['1', '2', '3', '4', '5', '6']
while True:
    for station in all_stations:
        num_people = requests.post('http://127.0.0.1:8001/count_people', json={'station_name': station}).json()
        num_people = num_people['num_people']
        now = datetime.now()
        cursor.execute("INSERT INTO users (station_name, time, num_people) VALUES (%s, %s, %s)", (station, now, num_people))
        conn.commit()
    time.sleep(60)

cursor.close()
conn.close()
