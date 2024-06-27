import sys
import time
import requests
from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import os
import re

app = FastAPI()


def downloading(date):
    file_name = f"../data/{date[0:4]}/{date[5:]}.zip"
    link = f"https://api.simurg.space/datafiles/map_files?date={date}"

    start_byte = 0
    if os.path.exists(file_name):
        start_byte = os.path.getsize(file_name)

    headers = {"Range": f"bytes={start_byte}-"}

    with open(file_name, "ab") as f:
        response = requests.get(link, headers=headers, stream=True)

        if response.status_code == 200:
            return True
        else:
            return False


class getDate(BaseModel):
    date: str


@app.get("/sites/list")
async def getDate():
    res1 = get_file_names()
    return {"result": res1}


def get_file_names():
    file_names = []

    with open('../txt/variables.txt', 'r') as file:
        date = re.search(r'\d{4}-\d{2}-\d{2}', file.read()).group()

    path = '../data/' + date[:4] + '/' + date[5:]

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


class DateInput(BaseModel):
    date: str


@app.post("/sites/start")
async def start_system(date: DateInput):
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    if not date_pattern.match(date.date):
        return {
            "error": "Неверный формат даты. Пожалуйста, используйте формат YYYY-MM-DD."}

    if downloading(date.date):
        subprocess.Popen(["bash", "../bash/starts", date.date], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return {
            "result": "Система успешно запущена, подождите некоторое время"}
    else:
        return {"result": "Данные на эту дату отсутствуют"}


@app.post("/sites/change_date")
async def change_system(date: DateInput):
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    if not date_pattern.match(date.date):
        return {
            "error": "Неверный формат даты. Пожалуйста, используйте формат YYYY-MM-DD."}

    if downloading(date.date):
        subprocess.Popen(["bash", "../bash/change", date.date], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return {
            "result": "Система успешно изменила дату, подождите некоторое время"}
    else:
        return {"result": "Данные на эту дату отсутствуют"}


@app.get("/sites/deactivate")
async def change_system():
    subprocess.Popen(["bash", "../bash/clean"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return {
        "result": "Система успешно деактивирована"}

class Topics(BaseModel):
    receivers: list[str]


@app.post("/sites/topics")
async def create_message(message: Topics):
    response = {}
    response['receivers'] = []

    for receiver in message.receivers:
        # Проверяем, существует ли файл с такими первыми 5 символами в папке data/2024/01-01
        with open('../txt/variables.txt', 'r') as file:
            date = re.search(r'\d{4}-\d{2}-\d{2}', file.read()).group()

        directory = '../data/' + date[:4] + '/' + date[5:]

        files_in_directory = os.listdir(directory)
        matching_files = [file for file in files_in_directory if file.startswith(receiver[:5])]

        if matching_files:
            response['receivers'].append(f"{receiver}: info/{receiver}")
        else:
            print(
                f"Файла с первыми 5 символами '{receiver[:5]}' не существует в папке {directory}")

    return response
