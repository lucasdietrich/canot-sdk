#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from caniot.controller import Controller

from pprint import pprint

with Controller("192.0.2.1") as ctrl:
    ctrl.get_info()
    ctrl.get_ha_stats()