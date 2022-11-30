#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from caniot.caniot import DeviceId, Endpoint
from caniot.datatypes import XPS
from caniot.controller import Controller

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("caniot.controller")
logger.setLevel(logging.WARN)

from pprint import pprint

ip = "192.0.2.1" if False else "192.168.10.240"

with Controller(ip) as ctrl:
    ctrl.caniot.app_timeout = 1.0

    with ctrl.caniot.open_device(DeviceId(1, 2)) as device:
        if False:
            device.reboot()

        if False:
            device.factory_reset()

        if True:
            ret = device.command(Endpoint.ApplicationMain, [
                25,
                50,
                75,
                100
            ])

            device.request_telemetry(Endpoint.ApplicationMain)