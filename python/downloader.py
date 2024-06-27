import sys
import requests
import time
import os

def downloading(date):
    file_name = f"data/{date[0:4]}/{date[5:]}.zip"
    link = f"https://api.simurg.space/datafiles/map_files?date={date}"

    start_byte = 0
    if os.path.exists(file_name):
        start_byte = os.path.getsize(file_name)

    headers = {"Range": f"bytes={start_byte}-"}

    with open(file_name, "ab") as f:
        print("Downloading %s" % file_name)
        response = requests.get(link, headers=headers, stream=True)

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

date = sys.argv[1]

count_trying = 0
flag = False

while count_trying < 5:
    try:
        flag = downloading(date)
    except Exception as exp:
        print(exp)

    if not(flag):
        time.sleep(60)
        count_trying += 1