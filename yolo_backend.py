from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ultralytics import YOLO
from random import randint

class StationRequest(BaseModel):
    station_name: str

app = FastAPI(title="ML API", version="0.1")

model = YOLO("yolo.pt")

@app.get("/")
def home():
    return {"message": "API is ready"}

@app.post("/count_people")
def count_people(request: StationRequest):
    image = f'stations/img_{randint(1, 6)}.png' #Здесь должен быть запрос к камере (что невозможно)
    results = model(image, device="cpu")
    num_people = len(results[0].boxes)
    return {'number_of_people': num_people}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
