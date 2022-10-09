#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from pprint import pprint
from caniot.controller import Controller
import json

with Controller("192.0.2.1") as ctrl:
    devices = ctrl.get_devices()
    stats = ctrl.get_ha_stats()

with open("tmp/ha_devices.json", "w") as f:
   json.dump(devices, f, indent=4)

with open("tmp/ha_stats.json", "w") as f:
    json.dump(stats, f, indent=4)

print("Devices: ./tmp/ha_devices.json")
print("Stats: ./tmp/ha_stats.json")