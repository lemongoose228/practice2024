import time
import paho.mqtt.client as mqtt_client
import hashlib
import datetime
import sys
import systemd.daemon

from gnss_tec import rnx

broker = "broker.emqx.io"

filename = sys.argv[1]

time_str = str(datetime.datetime.now())
user_id = hashlib.md5(time_str.encode()).hexdigest()

client = mqtt_client.Client(
   mqtt_client.CallbackAPIVersion.VERSION1,
   user_id
)

systemd.daemon.notify('READY=1')

print("Connecting to broker", broker)
print(client.connect(broker))
client.loop_start()
print("Publishing")

with open(filename) as obs_file:
    reader = rnx(obs_file)
    current_time = -1
    start_time = 0
    end_time = 30
    for tec in reader:
        state = '{} {}: {} {}'.format(
                tec.timestamp,
                tec.satellite,
                tec.phase_tec,
                tec.p_range_tec,
            )
        if current_time == state.split()[1]:
            client.publish("info/" + filename[16:24], state)
        else:
            if current_time != -1:
                end_time = time.time()
                execution_time = end_time - start_time
                time.sleep(30 - execution_time)

            current_time = state.split()[1]

            client.publish("info/" + filename[16:24], state)
            start_time = time.time()

        print("message is " + state)


client.disconnect()
client.loop_stop()
