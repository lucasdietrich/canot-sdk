#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from pprint import pprint
from caniot.controller import Controller
import json
import time

qemu = False

ip = "192.0.2.1" if qemu else "192.168.10.240"

with Controller(ip) as ctrl:
    devices = ctrl.get_devices()
    stats = ctrl.get_ha_stats()

now = time.time()
for dev in devices:
    diff = 3600*2
    last_seen = now - dev["endpoints"][0]["last_event"]["timestamp"] - diff
    print(f"{dev['addr_type']} {dev['addr_medium']} {dev['addr_repr']} : -{last_seen:.0f}s")

with open("tmp/ha_devices.json", "w") as f:
   json.dump(devices, f, indent=4)

with open("tmp/ha_stats.json", "w") as f:
    json.dump(stats, f, indent=4)

print("Devices: ./tmp/ha_devices.json")
print("Stats: ./tmp/ha_stats.json")