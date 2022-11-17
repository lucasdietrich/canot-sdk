#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from caniot.controller import Controller, DeviceId
import time

from pprint import pprint

ip = "192.0.2.1" if False else "192.168.10.240"

with Controller(ip) as ctrl:
    for i in range(0x800):
        resp = ctrl.send_can(i, [])
        print(hex(i), resp)
        time.sleep(0.1)

    # ctrl.caniot.request_telemetry(DeviceId.Broadcast(), 0x1)