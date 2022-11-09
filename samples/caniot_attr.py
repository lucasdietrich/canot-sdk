#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from caniot.caniot import DeviceId
from caniot.controller import Controller

from pprint import pprint

ip = "192.0.2.1" if True else "192.168.10.240"

with Controller(ip) as ctrl:
    with ctrl.caniot.open_device(DeviceId(1, 7)) as device:
        # for i in range(0x400):
        #     pprint(device.read_attribute(i))

        for i in range(10):
            pprint(device.write_attribute(0x2000, i))
            pprint(device.read_attribute(0x2000))