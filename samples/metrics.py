#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from pprint import pprint
from caniot.controller import Controller
import json

ip = "192.0.2.1" if False else "192.168.10.240"

with Controller(ip) as ctrl:
    print(ctrl.get_metrics())