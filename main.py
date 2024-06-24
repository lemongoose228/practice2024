from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

#class getStreams(BaseModel):
#    streams: List

class getDate(BaseModel):
    date: str


@app.post("/sites")
async def getDate(date: getDate):
    res1 = get_file_names(date.date)
    return {"result": res1}


#@app.post("/sites/streams")
#async def streams(data: getStreams):
#    for name in data:
#       for file in os.listdir("data/2024/01-02"):
#            if name in file:
#                res = subprocess.check_call(["./data_manager", date.date], shell=True)
#    return {"result": res}


def get_file_names(date):
    file_names = []

    path = './data/' + date[:4] + '/' + date[5:]

    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)) and not file.endswith('.Z'):
            file_name = file.split('_')[0]
            file_names.append(file_name)

    return file_names
