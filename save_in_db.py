import requests
import psycopg2
import time
import datetime

conn = psycopg2.connect(
    dbname="count_of_people_on_stations",
    user="hackathon",
    password="hackathon",
    host="khokhlovkirill.ru"
)
cursor = conn.cursor()
all_stations = ['1', '2', '3', '4', '5', '6']
while True:
    for station in all_stations:
        num_people = requests.post('http://127.0.0.1:8001/count_people', json={'station_name': station}).json()
        num_people = num_people['number_of_people']
        cursor.execute("INSERT INTO measures (station_name, count_people) VALUES (%s, %s)", (station, num_people))
        conn.commit()
    print(datetime.datetime.now(), '| Information was sent')
    time.sleep(60)

cursor.close()
conn.close()
