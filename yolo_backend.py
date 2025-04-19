from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ultralytics import YOLO
from random import randint
from datetime import datetime
from typing import Optional
import requests
import psycopg2
import time

class StationRequest(BaseModel):
    station_name: str
    time: Optional[datetime]

app = FastAPI(title="ML API", version="0.1")

model = YOLO("yolo.pt")

conn = psycopg2.connect(
    dbname="count_of_people_on_stations",
    user="hackathon",
    password="hackathon",
    host="khokhlovkirill.ru"
)
cursor = conn.cursor()

@app.get("/")
def home():
    return {"message": "API is ready"}

@app.post("/count_people")
def count_people(request: StationRequest):
    if not request.time:
        image = f'stations/img_{request.station_name}.png' # Здесь должен быть запрос к камере (что невозможно)
        results = model(image, device="cpu")
        num_people = len(results[0].boxes)
        return {'number_of_people': num_people}
    cursor.execute("""
        SELECT *
        FROM measures
        WHERE name = %s 
          AND date_column = %s;
    """, (request['station_name'], request['time']))

    results = cursor.fetchall()[0]
    return results['count_people']


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
