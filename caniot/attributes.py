import datetime
import struct
import time
from typing import Union

from .caniot import DeviceId

def is_bit(n: int, bit: int = 0) -> bool:
    return bool(n & (1 << bit))

class Key:
    def __init__(self, key: int):
        self.key = key

        self.section = (self.key& 0xF000) >> 12
        self.attr = (self.key & 0xFF0) >> 4
        self.part = self.key & 0xF

    def __repr__(self):
        return f"0x{self.key:04X} ({self.section} / {self.attr} / {self.part})"


class Attribute:
    def __init__(self, key: int, name: str, size: int = 4, readonly: bool = False):
        self.key = key
        self.name = name
        self.size = size
        self.readonly = readonly

        self.parts = int(round(self.size / 4, 0))

        assert self.parts < 16

    def __repr__(self):
        return f"0x{self.key:04X} ({self.name})"

    def get_part_key(self, n: int = 0) -> int:
        assert n < self.parts

        return self.key + n

    def default_interpret(val: int, key: int = None):
        return f"{val} (0x{val:04X})"

    def interpret(self, val: int, key: int = None):
        return Attribute.default_interpret(val, key)

    def __contains__(self, key: Union[Key, int]):
        if isinstance(key, int):
            key = Key(key)

        my = Key(self.key)

        return my.section == key.section and \
               my.attr == key.attr and \
               key.part <= self.size // 4


class AttrNodeID(Attribute):
    def interpret(self, val: int, key: int = None):
        return DeviceId.from_int(val).__repr__()

class AttrVersion(Attribute):
    def interpret(self, val: int, key: int = None):
        return f"CANIOT {val >> 8} Application {val & 0xFF}"

class AttrName(Attribute):
    def interpret(self, val: int, key: int = None):

        c1, c2, c3, c4 = struct.unpack("cccc", val.to_bytes(4, byteorder="little"))

        prev = "" if key & 0x4 == 0 else "... "
        post = "" if key & 0x4 == 8 else " ..."

        return prev + (c1 + c2 + c3 + c4).decode("utf8") + post


class AttrTimestamp(Attribute):
    def interpret(self, val: int, key: int = None):
        return datetime.datetime.fromtimestamp(val).strftime("%Y-%m-%d %H:%M:%S")

class AttrSeconds(Attribute):
    def interpret(self, val: int, key: int = None):
        days = val // 86400
        hours = (val % 86400) // 3600
        minutes = (val % 3600) // 60
        seconds = val % 60

        fmt = f"{hours}h {minutes}m {seconds}s"
        if days > 0:
            fmt = f"{days} days" + fmt
        return fmt

class AttrDelayS(Attribute):
    def interpret(self, val: int, key: int = None):
        return f"{val} seconds"

class AttrDelayMS(Attribute):
    def interpret(self, val: int, key: int = None):
        return f"{val} ms"

class AttrCfgFlags(Attribute):
    def interpret(self, val: int, key: int = None):
        return f"err={int(is_bit(val, 0))} telem rdm={int(is_bit(val, 1))} ep={(val >> 2) & 0x3}"

# https://docs.python.org/3/library/struct.html
class AttrTimezone(Attribute):
    def interpret(self, val: int, key: int = None):
        int32, = struct.unpack("i", val.to_bytes(4, byteorder="little"))

        shift = int(int32 / 3600)

        return f"+ {shift} H" if shift >= 0 else f"- {shift} H"

class AttrRegionCountry(Attribute):
    def interpret(self, val: int, key: int = None):
        r1, r2, c1, c2 = struct.unpack("cccc", val.to_bytes(4, byteorder="little"))

        return (r1 + r2 + b"/" + c1 + c2).decode("utf8")


attributes = [
    AttrNodeID(0x0000, "nodeid", size=1, readonly=True),
    AttrVersion(0x0010, "version", size=2, readonly=True),
    AttrName(0x0020, "name", size=32, readonly=True),
    Attribute(0x0030, "magic_number", size=4, readonly=True),

    AttrSeconds(0x1000, "uptime_synced", readonly=True),
    AttrTimestamp(0x1010, "time"),
    AttrSeconds(0x1020, "uptime", readonly=True),
    AttrTimestamp(0x1030, "start_time", readonly=True),
    AttrTimestamp(0x1040, "last_telemetry", readonly=True),
    Attribute(0x1050, "received.total", readonly=True),
    Attribute(0x1060, "received.read_attribute", readonly=True),
    Attribute(0x1070, "received.write_attribute", readonly=True),
    Attribute(0x1080, "received.command", readonly=True),
    Attribute(0x1090, "received.request_telemetry", readonly=True),
    # Attribute(0x10A0, "received.processed", readonly=True),
    # Attribute(0x10B0, "received.query_failed", readonly=True),
    Attribute(0x10C0, "sent.total", readonly=True),
    Attribute(0x10D0, "sent.telemetry", readonly=True),
    # Attribute(0x10E0, "events.total", readonly=True),
    Attribute(0x10F0, "last_command_error", size=2, readonly=True),
    Attribute(0x1100, "last_telemetry_error", size=2, readonly=True),
    # Attribute(0x1110, "last_event_error", size=2, readonly=True),
    Attribute(0x1120, "battery", size=1, readonly=True),

    AttrDelayS(0x2000, "telemetry.period"),
    AttrDelayMS(0x2010, "telemetry.delay", size=2),
    AttrDelayMS(0x2020, "telemetry.delay_min", size=2),
    AttrDelayMS(0x2030, "telemetry.delay_max", size=2),
    AttrCfgFlags(0x2040, "telemetry.flags", size=1),
    AttrTimezone(0x2050, "telemetry.timezone", size=4),
    AttrRegionCountry(0x2060, "region/country", size=4),
    AttrDelayMS(0x2070, "custompcb.gpio.pulse_duration.oc1", size=4),
    AttrDelayMS(0x2080, "custompcb.gpio.pulse_duration.oc2", size=4),
    AttrDelayMS(0x2090, "custompcb.gpio.pulse_duration.rl1", size=4),
    AttrDelayMS(0x20A0, "custompcb.gpio.pulse_duration.rl2", size=4),
    Attribute(0x20B0, "custompcb.gpio.mask.outputs_default", size=4),
    Attribute(0x20C0, "custompcb.gpio.mask.telemetry_on_change", size=4),
]

def get_by_key(key: int) -> Attribute:
    key = Key(key)

    for attr in attributes:
        if key in attr:
            return attr

def get(name: str) -> Attribute:
    for attr in attributes:
        if attr.name == name:
            return attr

def interpret(key: int, val: int) -> str:
    attr = get_by_key(key)

    if attr:
        return attr.interpret(val, key)
    else:
        return Attribute.default_interpret(val, key)