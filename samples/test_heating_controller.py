#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from caniot.caniot import DeviceId, MsgId
from caniot.datatypes import XPS
from caniot.controller import Controller

from pprint import pprint

ip = "192.0.2.1" if False else "192.168.10.240"

with Controller(ip) as ctrl:
    ctrl.caniot.app_timeout = 1.0

    with ctrl.caniot.open_device(DeviceId(1, 7)) as device:
        # pprint(device.command_cls1([
        #     "none",
        #     "set_on",
        # ]))

        resp = device.command_cls1([
            XPS.NONE.name,
            XPS.NONE.name,
            XPS.NONE.name,
            XPS.NONE.name,

            XPS.NONE.name,
            XPS.NONE.name,
            XPS.NONE.name,
            XPS.NONE.name,
            
            XPS.TOGGLE.name,
            XPS.TOGGLE.name,
            XPS.TOGGLE.name,
            XPS.TOGGLE.name,

            XPS.TOGGLE.name,
            XPS.TOGGLE.name,
            XPS.TOGGLE.name,
            XPS.TOGGLE.name,
            
            XPS.SET_OFF.name,
        ])
        pprint(resp)

        # while True:
        #     resp = device.request_telemetry(MsgId.Endpoint.BoardControlEndpoint.value)
        #     pprint(resp)