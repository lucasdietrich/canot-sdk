#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from caniot.caniot import DeviceId, Endpoint
from caniot.controller import Controller

from pprint import pprint

ip = "192.0.2.1" if False else "192.168.10.240"

with Controller(ip) as ctrl:    
    with ctrl.caniot.open_device(DeviceId(1, 0)) as device:
        pprint(device.request_telemetry(Endpoint.ApplicationMain))

    # ctrl.caniot.request_telemetry(DeviceId(1, 7), 1)