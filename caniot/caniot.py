#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations

from enum import Enum, IntEnum
from dataclasses import dataclass

from typing import Union, List, Dict, Tuple

@dataclass
class DeviceId:
    def __init__(self, cls: int, sid: int):
        self.cls = cls & 0x7
        self.sid = sid & 0x7

    @classmethod
    def from_int(cls, deviceid: int) -> DeviceId:
        return DeviceId(
            cls=int(deviceid) & 7,
            sid=int(deviceid) >> 3
        )

    def get_id(self) -> int:
        return (self.sid << 3) | self.cls

    id = property(get_id)

    def __eq__(self, other: Union[int, DeviceId]):
        return int(other) == int(self)

    def __int__(self):
        return self.get_id()

    def is_broadcast(self) -> bool:
        return self.sid == 0x7 and self.cls == 0x7

    def __repr__(self):
        if self.is_broadcast():
            return "Broadcast (sid=0x7, cls = 0x7)"
        else:
            return f"DeviceId={self.get_id()} (cls = {self.cls}, sid={self.sid})"

    @classmethod
    def Broadcast(cls) -> DeviceId:
        return DeviceId(cls=0b111, sid=0b111)

class IdType(IntEnum):
    Standard = 11
    Extended = 29

class FrameType(IntEnum):
    Command = 0
    Telemetry = 1
    WriteAttribute = 2
    ReadAttribute = 3

class QueryType(IntEnum):
    Query = 0
    Response = 1

class Endpoint(IntEnum):
    ApplicationMain = 0 # app0
    ApplicationSecond = 1 # app1
    ApplicationThird = 2 # app2
    BoardLevelControl = 3 # blc

    def join(self, controller: Endpoint):
        return self | controller

@dataclass
class MsgId:
    frame_type: FrameType
    query_type: QueryType
    device_id: DeviceId
    endpoint: Endpoint = Endpoint.ApplicationMain

    extended_id: int = 0

    id_type: IdType = IdType.Standard

    def __eq__(self, other: Union[int, MsgId]):
        return int(self) == int(other)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.is_valid():
            return f"[{hex(self)}] " \
                   f"{QueryType(self.query_type).name} " \
                   f"{FrameType(self.frame_type).name} " \
                   f"{Endpoint(self.endpoint).name} " \
                   f"{self.device_id}"
        elif self.is_error():
            return f"[{hex(self)}] ERROR message from {self.device_id}"
        else:
            return f"INVALID CANIOT MESSAGE [0x{int(self):04X}]"

    def __int__(self) -> int:
        return self.get()

    def __index__(self):
        return int(self)

    def __and__(self, other: MsgId):
        return int(self) & int(other)

    def get(self) -> int:
        std_id = self.frame_type | self.query_type << 2 | self.device_id.get_id() << 3 | self.endpoint << 9

        if self.id_type is IdType.Extended:
            return std_id | self.extended_id << 11
        else:
            return std_id

    @staticmethod
    def from_int(value: int, extended: bool = None) -> MsgId:
        return MsgId(
            frame_type=FrameType(value & 0b11),
            query_type=QueryType((value >> 2) & 1),
            device_id=DeviceId.from_int((value >> 3) & 0b111111),
            endpoint=Endpoint((value >> 9) & 0b11),
            extended_id=value >> 11 if extended is None or extended is True else 0,
            id_type=IdType.Extended if value >> 11 and extended is not False else IdType.Standard
        )

    def bin_repr(self) -> str:
        return bin(int(self))[2:].rjust(self.id_type, "0")

    def is_error(self) -> bool:
        return self.frame_type == FrameType.Command and self.query_type == QueryType.Response

    def is_valid(self) -> bool:
        return self.device_id != 0 and not self.is_error() and \
               (self.query_type == QueryType.Query or not self.is_broadcast_device()) # cannot be a response from all nodes

    def is_query(self) -> bool:
        return self.is_valid() and self.query_type is QueryType.Query

    def is_broadcast_device(self) -> bool:
        return self.device_id == DeviceId.Broadcast()

    def is_response(self) -> bool:
        return self.is_valid() and self.query_type is QueryType.Response

    def prepare_response(self) -> MsgId:
        if self.is_query():
            if self.frame_type == FrameType.Command:
                resp_type = FrameType.Telemetry
            elif self.frame_type == FrameType.WriteAttribute:
                resp_type = FrameType.ReadAttribute
            else:
                resp_type = self.frame_type

            return MsgId(
                frame_type=resp_type,
                query_type=QueryType.Response,
                endpoint=self.endpoint,
                device_id=self.device_id,
                id_type=self.id_type,
                extended_id=self.extended_id if self.id_type is IdType.Extended else 0
            )
        else:
            raise Exception(f"{self} MsgID is not a query")

    def is_response_of(self, query: MsgId) -> bool:
        if self.is_valid():
            expected_response = query.prepare_response()

            # handle the case when a message is a response for a broadcast message
            if query.is_broadcast_device():

                # we expect a response to a broadcast query
                expected_response.device_id = self.device_id

            return expected_response == self
        else:
            raise Exception(f"{query} is not a valid Query")

    def is_query_of(self, response: MsgId) -> bool:
        return response.is_response_of(self)

    def is_extended(self) -> bool:
        return self.id_type is IdType.Extended

# ____________________________________________________________________________________________________________________ #


if __name__ == "__main__":
    msgid = MsgId(
        frame_type=FrameType.Telemetry,
        query_type=QueryType.Query,
        endpoint=Endpoint.ApplicationMain,
        device_id=DeviceId(DeviceId.Class.CUSTOMPCB, 1)
    )

    print(msgid, ":", msgid.bin_repr())
