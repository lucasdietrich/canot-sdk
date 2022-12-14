#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from caniot.controller import Controller

from pprint import pprint

ip = "192.0.2.1" if True else "192.168.10.240"

with Controller(ip) as ctrl:
    # resp = ctrl.download("lua/math.lua", "./tmp/math.lua")

    while True:
        ctrl.upload("./tmp/ha_devices.json", "my/dir/devices.json", chunked_encoding=False, chunks_size=1024)
        ctrl.download("my/dir/devices.json", "./tmp/ha_devices2.json")
        break
    
    # ctrl.upload("./tmp/ha_devices.json", "tmp/devices.json", 1024)