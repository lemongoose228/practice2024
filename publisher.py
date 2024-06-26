import time
import paho.mqtt.client as mqtt_client
import hashlib
import datetime
import sys
import systemd.daemon

from gnss_tec import rnx

def get_rnx_number():
    with open('/home/user/practice/variables.txt', 'r') as f:
        rnx_number = ''
        while 'rnx' not in rnx_number:
            rnx_number = f.readline().strip()

    return rnx_number

def get_status(receiver_name):
    with open('/home/user/practice/pub_statuses.txt', 'r') as f:
        status = ''
        while receiver_name not in status:
            status = f.readline().strip()

    return status

def broker_setup():
    broker = "broker.emqx.io"

    time_str = str(datetime.datetime.now())
    user_id = hashlib.md5(time_str.encode()).hexdigest()

    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION2,
        user_id[0:12]
    )

    print("Connecting to broker", broker)
    client.connect(broker)
    client.loop()
    print("Publishing")

    return client

def get_begin_work_time():
    real_time = datetime.datetime.now()
    # real_time = datetime.datetime(2024, 1, 1, 23, 59, 21)

    if 20 <= int(real_time.strftime("%H:%M:%S").split(":")[-1]) <= 50:
        real_time += datetime.timedelta(minutes=1)
        real_time = real_time.strftime("%H:%M:%S")

        begin_work_hour = real_time.split(":")[0]
        begin_work_minutes = real_time.split(":")[1]

        begin_work_time = f"{begin_work_hour}:{begin_work_minutes}:00"
    else:
        if int(real_time.strftime("%H:%M:%S").split(":")[-1]) >= 50:
            real_time += datetime.timedelta(minutes=1)
            real_time = real_time.strftime("%H:%M:%S")
            begin_work_hour = real_time.split(":")[0]
            begin_work_minutes = real_time.split(":")[1]

            begin_work_time = f"{begin_work_hour}:{begin_work_minutes}:30"

        else:
            real_time = real_time.strftime("%H:%M:%S")
            begin_work_hour = real_time.split(":")[0]
            begin_work_minutes = real_time.split(":")[1]

            begin_work_time = f"{begin_work_hour}:{begin_work_minutes}:30"

    return begin_work_time


def publishing(fullpath):
    begin_work_time = get_begin_work_time()

    with open(fullpath) as obs_file:
        reader = rnx(obs_file)
        parsing_current_time = -1
        start_time = 0
        ready_work = False

        for tec in reader:
            state = '{} {}: {} {}'.format(
                    tec.timestamp,
                    tec.satellite,
                    tec.phase_tec,
                    tec.p_range_tec,
                )
            if not(ready_work):
                if state.split()[1] == begin_work_time:
                    while datetime.datetime.now().strftime("%H:%M:%S") != begin_work_time:
                        time.sleep(0.1)
                    ready_work = True
                else:
                    continue

            if parsing_current_time == state.split()[1]:
                client.publish("info/" + filename[0:9], state)
            else:
                if parsing_current_time != -1:
                    end_time = time.time()
                    execution_time = end_time - start_time
                    time.sleep(30 - execution_time)

                parsing_current_time = state.split()[1]

                client.publish("info/" + filename[0:9], state)
                start_time = time.time()


            print("message is " + state)

filename = sys.argv[1]
# filename = "DRAO00CAN_R_20240070000_01D_30S_MO.rnx"

systemd.daemon.notify('READY=1')

if get_status(filename[0:9]) == 'wait' and datetime.datetime.now() < datetime.datetime.now().replace(hour=23, minute=59, second=21):
    while datetime.datetime.now().strftime("%H:%M:%S") != "23:59:21":
        time.sleep(0.1)

if get_status(filename[0:9]) == 'willstop' and datetime.datetime.now() > datetime.datetime.now().replace(hour=23, minute=59, second=19):
    exit()

if get_status(filename[0:9]) == 'work' and \
        datetime.datetime.now() > datetime.datetime.now().replace(hour=23, minute=58, second=58) and \
        datetime.datetime.now() < datetime.datetime.now().replace(hour=23, minute=59, second=21):
    while datetime.datetime.now().strftime("%H:%M:%S") != "23:59:30":
        time.sleep(0.1)


client = broker_setup()

fullpath = f"/home/user/practice/{get_rnx_number()}/{filename}"

while True:
    publishing(fullpath)
    if get_status(filename[0:9]) == 'willstop':
        exit()
    fullpath = f"/home/user/practice/{get_rnx_number()}/{filename}"
