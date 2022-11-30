#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from caniot.caniot import *

mid = MsgId(
    FrameType.Telemetry,
    QueryType.Query,
    DeviceId(0x01, 0x07),
    Endpoint.BoardLevelControl
)

print(mid, int(mid))