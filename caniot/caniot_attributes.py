import datetime
import struct
import time
from typing import Union

from enum import IntEnum

from .caniot import DeviceId
from .utils import is_bit_set


class AttributeId(IntEnum):
    NodeID = 0x0000
    Version = 0x0010
    Name = 0x0020
    MagicNumber = 0x0030

    SysUptimeSynced = 0x1000
    SysTime = 0x1010
    SysUptime = 0x1020
    SysStartTime = 0x1030
    SysLastTelemetry = 0x1040
    SysReceivedTotal = 0x1050
    SysReceivedReadAttribute = 0x1060
    SysReceivedWriteAttribute = 0x1070
    SysReceivedCommand = 0x1080
    SysReceivedRequestTelemetry = 0x1090
    SysSentTotal = 0x10C0
    SysSentTelemetry = 0x10D0
    SysLastCommandError = 0x10F0
    SysLastTelemetryError = 0x1100
    SysBattery = 0x1120

    CfgTelemetryPeriodMs = 0x2000
    CfgTelemetryDelay = 0x2010
    CfgTelemetryDelayMin = 0x2020
    CfgTelemetryDelayMax = 0x2030
    CfgTelemetryFlags = 0x2040
    CfgTelemetryTimezone = 0x2050
    CfgTelemetryLocation = 0x2060  # region/country

    CfgClass0PulseDurationOC1 = 0x2070
    CfgClass0PulseDurationOC2 = 0x2080
    CfgClass0PulseDurationRL1 = 0x2090
    CfgClass0PulseDurationRL2 = 0x20A0
    CfgClass0OutputDefaultsMask = 0x20B0
    CfgClass0TelemetryOnChangesMask = 0x20C0

    CfgClass1PulseDurationPC0 = 0x20D0
    CfgClass1PulseDurationPC1 = 0x20E0
    CfgClass1PulseDurationPC2 = 0x20F0
    CfgClass1PulseDurationPC3 = 0x2100
    CfgClass1PulseDurationPD0 = 0x2110
    CfgClass1PulseDurationPD1 = 0x2120
    CfgClass1PulseDurationPD2 = 0x2130
    CfgClass1PulseDurationPD3 = 0x2140
    CfgClass1PulseDurationEIO0 = 0x2150
    CfgClass1PulseDurationEIO1 = 0x2160
    CfgClass1PulseDurationEIO2 = 0x2170
    CfgClass1PulseDurationEIO3 = 0x2180
    CfgClass1PulseDurationEIO4 = 0x2190
    CfgClass1PulseDurationEIO5 = 0x21A0
    CfgClass1PulseDurationEIO6 = 0x21B0
    CfgClass1PulseDurationEIO7 = 0x21C0
    CfgClass1PulseDurationPB0 = 0x21D0
    CfgClass1PulseDurationPE0 = 0x21E0
    CfgClass1PulseDurationPE1 = 0x21F0
    CfgClass1OutputDirectionsMask = 0x2210
    CfgClass1OutputDefaultsMask = 0x2220
    CfgClass1TelemetryOnChangesMask = 0x2230


class Key:
    def __init__(self, key: int):
        self.key = key

        self.section = (self.key & 0xF000) >> 12
        self.attr = (self.key & 0xFF0) >> 4
        self.part = self.key & 0xF

    def __repr__(self):
        return f"0x{self.key:04X} ({self.section} / {self.attr} / {self.part})"


class Attribute:
    def __init__(self, key: int, name: str = "", size: int = 4, readonly: bool = False):
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

        c1, c2, c3, c4 = struct.unpack(
            "cccc", val.to_bytes(4, byteorder="little"))

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
        return f"err={int(is_bit_set(val, 0))} telem rdm={int(is_bit_set(val, 1))} ep={(val >> 2) & 0x3}"

class AttrTimezone(Attribute):
    def interpret(self, val: int, key: int = None):
        int32, = struct.unpack("i", val.to_bytes(4, byteorder="little"))

        shift = int(int32 / 3600)

        return f"+ {shift} H" if shift >= 0 else f"- {shift} H"


class AttrRegionCountry(Attribute):
    def interpret(self, val: int, key: int = None):
        r1, r2, c1, c2 = struct.unpack(
            "cccc", val.to_bytes(4, byteorder="little"))

        return (r1 + r2 + b"/" + c1 + c2).decode("utf8")


attributes = [
    # Identification
    AttrNodeID(AttributeId.NodeID, "nodeid", size=1, readonly=True),
    AttrVersion(AttributeId.Version, "version", size=2, readonly=True),
    AttrName(AttributeId.Name, "name", size=32, readonly=True),
    Attribute(AttributeId.MagicNumber, "magic_number", size=4, readonly=True),

    # System
    AttrSeconds(AttributeId.SysUptimeSynced, "uptime_synced", readonly=True),
    AttrTimestamp(AttributeId.SysTime, "time"),
    AttrSeconds(AttributeId.SysUptime, "uptime", readonly=True),
    AttrTimestamp(AttributeId.SysStartTime, "start_time", readonly=True),
    AttrTimestamp(AttributeId.SysLastTelemetry,
                  "last_telemetry", readonly=True),
    Attribute(AttributeId.SysReceivedTotal, "received.total", readonly=True),
    Attribute(AttributeId.SysReceivedReadAttribute,
              "received.read_attribute", readonly=True),
    Attribute(AttributeId.SysReceivedWriteAttribute,
              "received.write_attribute", readonly=True),
    Attribute(AttributeId.SysReceivedCommand,
              "received.command", readonly=True),
    Attribute(AttributeId.SysReceivedRequestTelemetry,
              "received.request_telemetry", readonly=True),
    Attribute(AttributeId.SysSentTotal, "sent.total", readonly=True),
    Attribute(AttributeId.SysSentTelemetry, "sent.telemetry", readonly=True),
    Attribute(AttributeId.SysLastCommandError,
              "last_command_error", size=2, readonly=True),
    Attribute(AttributeId.SysLastTelemetryError,
              "last_telemetry_error", size=2, readonly=True),
    Attribute(AttributeId.SysBattery, "battery", size=1, readonly=True),

    # Config General
    AttrDelayMS(AttributeId.CfgTelemetryPeriodMs, "telemetry.period"),
    AttrDelayMS(AttributeId.CfgTelemetryDelay, "telemetry.delay", size=2),
    AttrDelayMS(AttributeId.CfgTelemetryDelayMin,
                "telemetry.delay_min", size=2),
    AttrDelayMS(AttributeId.CfgTelemetryDelayMax,
                "telemetry.delay_max", size=2),
    AttrCfgFlags(AttributeId.CfgTelemetryFlags, "flags", size=1),
    AttrTimezone(AttributeId.CfgTelemetryTimezone, "timezone", size=4),
    AttrRegionCountry(AttributeId.CfgTelemetryLocation, "location", size=4),

    # Config Class 0
    AttrDelayMS(AttributeId.CfgClass0PulseDurationOC1,
                "custompcb.gpio.pulse_duration.oc1", size=4),
    AttrDelayMS(AttributeId.CfgClass0PulseDurationOC2,
                "custompcb.gpio.pulse_duration.oc2", size=4),
    AttrDelayMS(AttributeId.CfgClass0PulseDurationRL1,
                "custompcb.gpio.pulse_duration.rl1", size=4),
    AttrDelayMS(AttributeId.CfgClass0PulseDurationRL2,
                "custompcb.gpio.pulse_duration.rl2", size=4),
    Attribute(AttributeId.CfgClass0OutputDefaultsMask,
              "custompcb.gpio.mask.outputs_default", size=4),
    Attribute(AttributeId.CfgClass0TelemetryOnChangesMask,
              "custompcb.gpio.mask.telemetry_on_change", size=4),

    # Config Class 1
    AttrDelayMS(AttributeId.CfgClass1PulseDurationPC0, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationPC1, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationPC2, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationPC3, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationPD0, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationPD1, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationPD2, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationPD3, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationEIO0, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationEIO1, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationEIO2, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationEIO3, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationEIO4, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationEIO5, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationEIO6, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationEIO7, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationPB0, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationPE0, size=4),
    AttrDelayMS(AttributeId.CfgClass1PulseDurationPE1, size=4),
    Attribute(AttributeId.CfgClass1OutputDirectionsMask, size=4),
    Attribute(AttributeId.CfgClass1OutputDefaultsMask, size=4),
    Attribute(AttributeId.CfgClass1TelemetryOnChangesMask, size=4),
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
