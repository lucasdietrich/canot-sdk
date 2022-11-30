#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from caniot.caniot import DeviceId, Endpoint
from caniot.datatypes import XPS, HeatingStatus
from caniot.controller import Controller

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("caniot.controller")
logger.setLevel(logging.WARN)

from pprint import pprint

ip = "192.0.2.1" if False else "192.168.10.240"

with Controller(ip) as ctrl:
    ctrl.caniot.app_timeout = 1.0

    with ctrl.caniot.open_device(DeviceId(1, 0)) as device:
        if False:
            h1 = HeatingStatus.COMFORT_MIN_1
            h2 = HeatingStatus.COMFORT_MIN_1
            h3 = HeatingStatus.COMFORT_MIN_2
            h4 = HeatingStatus.COMFORT_MIN_2

            ret = device.command(Endpoint.ApplicationMain, [
                h1.value + (h2.value << 4),
                h3.value + (h4.value << 4),
            ])
            print(ret)

        if False:
            for i in range(0, 19):
                dur = device.read_attribute(0x20D0 + (i << 4)).get("value", 0)
                print(f"{i} Pulse duration {dur} ms")

                device.write_attribute(0x20D0 + (i << 4), 500)

        # ret = device.read_attribute(0x20D0 + ((19) << 4))
        # print(ret)

        # XPS
        if False:
            command = XPS.TOGGLE

            resp = device.command_cls1([
                XPS.NONE.name,
                XPS.NONE.name,
                XPS.NONE.name,
                XPS.NONE.name,

                XPS.NONE.name,
                XPS.NONE.name,
                XPS.NONE.name,
                XPS.NONE.name,
                
                command.name,
                command.name,
                command.name,
                command.name,

                command.name,
                command.name,
                command.name,
                command.name,
                
                XPS.NONE.name,
            ])
            pprint(resp)

        while False:
            resp = device.request_telemetry(Endpoint.BoardLevelControl.value)
            pprint(resp)

        resp = device.request_telemetry(Endpoint.BoardLevelControl.value)
        pprint(resp)

        