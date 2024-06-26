from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

#class getStreams(BaseModel):
#    streams: List

class getListReceivers(BaseModel):
    date: str


@app.get("/sites")
async def getListReceivers():
    res1 = get_file_names()
    return {"result": res1}


def get_file_names():
    file_names = []

    with open('variables.txt', 'r') as file:
        date = re.search(r'\d{4}-\d{2}-\d{2}', file.read()).group()

    path = './data/' + date[:4] + '/' + date[5:]

    if not os.path.exists(path):
        print("Установка ещё не завершена или не была запущена")
        return file_names

    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)) and (file.endswith('.Z') or file.endswith('.crx')):
            if '_' not in file:
                file_name = file.split('.')[0]
            else:
                file_name = file.split('_')[0]

            file_name = file_name.ljust(9, '0')[:9]
            file_names.append(file_name)

    return file_names


class Topics(BaseModel):
    receivers: list[str]

@app.post("/sites/topics")
async def create_message(message: Topics):
    response = {}
    response['receivers'] = []

    for receiver in message.receivers:

        with open('variables.txt', 'r') as file:
            date = re.search(r'\d{4}-\d{2}-\d{2}', file.read()).group()

        directory = './data/' + date[:4] + '/' + date[5:]

        files_in_directory = os.listdir(directory)
        matching_files = [file for file in files_in_directory if file.startswith(receiver[:5])]

        if matching_files:
            response['receivers'].append(f"{receiver}: info/{receiver}")
        else:
            print(f"Файла '{receiver}' не существует в папке {directory}")

    return response
