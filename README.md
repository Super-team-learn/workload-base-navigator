# Backend part for the application

## Main service
To start use ``uvicorn`` on port ``8000``:
```shell
      python main.py
```

## ML serivce
To start use ``uvicorn`` on port ``8001``
```shell
      python yolo_backend.py
```

## Requirements
```
fastapi==0.115.12
psycopg2==2.9.10
pydantic==2.11.3
Requests==2.32.3
ultralytics==8.3.111
uvicorn==0.34.1
```