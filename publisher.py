import time
import paho.mqtt.client as mqtt_client
import hashlib
import datetime
import sys
# import systemd.daemon

from gnss_tec import rnx

def get_rnx_number():
    with open('variable.txt', 'r') as f:
       rnx_number = f.read().strip()

    return rnx_number

broker = "broker.emqx.io"

# filename = sys.argv[1]
filename = "DRAO00CAN_R_20240070000_01D_30S_MO.rnx"

print("info/" + filename[0:9])

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

# systemd.daemon.notify('READY=1')


fullpath = f"{get_rnx_number()}/{filename}"

real_time = datetime.datetime.now()

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

with open(fullpath) as obs_file:
    reader = rnx(obs_file)
    current_time = -1
    start_time = 0
    end_time = 30
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

        if current_time == state.split()[1]:
            client.publish("info/" + filename[0:9], state)
        else:
            if current_time != -1:
                end_time = time.time()
                execution_time = end_time - start_time
                time.sleep(30 - execution_time)

            current_time = state.split()[1]

            client.publish("info/" + filename[0:9], state)
            start_time = time.time()


        print("message is " + state)
