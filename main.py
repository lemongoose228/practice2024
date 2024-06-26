from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

def downloading(date, check):
    file_name = f"data/{date[0:4]}/{date[5:]}.zip"
    link = f"https://api.simurg.space/datafiles/map_files?date={date}"

    start_byte = 0
    if os.path.exists(file_name):
        start_byte = os.path.getsize(file_name)

    headers = {"Range": f"bytes={start_byte}-"}

    with open(file_name, "ab") as f:
        print("Downloading %s" % file_name)
        response = requests.get(link, headers=headers, stream=True)

        if check:
            if response.status_code == 200:
                return True
            else:
                return False

        total_length = int(response.headers.get('content-length', 0)) - start_byte
        dl = start_byte

        if total_length:
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s] %3.1f%%" % ('=' * done, ' ' * (50 - done), 100 * dl / total_length))
                sys.stdout.flush()

        else:
            f.write(response.content)

    print("\nDownload completed for %s" % file_name)

    return True



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


class DateInput(BaseModel):
    date: str

@app.post("/sites/start")
async def get_date(date: DateInput):
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    if not date_pattern.match(date.date):
        return {"error": "Неверный формат даты. Пожалуйста, используйте формат YYYY-MM-DD."}

    if downloading(date.date, True):
        return {"result": "Система успешно запущена, подождите некоторое время"}

    count_trying = 0
    flag = False

    while count_trying < 5:
        try:
            flag = downloading(date.date, False)
            subprocess.check_call(["./starts " + date.date, date.date], shell=True)
        except Exception as exp:
            print(exp)

        if not(flag):
            time.sleep(60)
            count_trying += 1


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
