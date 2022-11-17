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
    ret = ctrl.get_room(0)
    print(ret)