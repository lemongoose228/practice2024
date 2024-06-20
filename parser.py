import time
import paho.mqtt.client as mqtt_client
from gnss_tec import rnx

broker = "broker.emqx.io"


client = mqtt_client.Client(
   mqtt_client.CallbackAPIVersion.VERSION1,
   'isu1001230065455645543'
)

print("Connecting to broker", broker)
print(client.connect(broker))
client.loop_start()
print("Publishing")

with open('FLRS00PRT_S_20240010000_01D_30S_MO.rnx') as obs_file:
    reader = rnx(obs_file)
    for tec in reader:
        state = '{} {}: {} {}'.format(
                tec.timestamp,
                tec.satellite,
                tec.phase_tec,
                tec.p_range_tec,
            )
    client.publish("lab/leds/state", state)


client.disconnect()
client.loop_stop()

# from gnss_tec import rnx
# 
# import sys
# 
# filename = sys.argv[1]
# 
# with open(filename) as obs_file:
#     reader = rnx(obs_file)
#     a = 0
#     for tec in reader:
#         print(
#             '{} {}: {} {}'.format(
#                 tec.timestamp,
#                 tec.satellite,
#                 tec.phase_tec,
#                 tec.p_range_tec,
#             )
#         )
#         a += 1
#         if a == 5:
#             break
