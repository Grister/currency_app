import time
from config.celery import app


@app.task
def add(x, y):
    time.sleep(10)
    print(x + y)
    return x + y


@app.task
def hello():
    print('hello')
