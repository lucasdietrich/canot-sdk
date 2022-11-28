import struct
from enum import IntEnum

U10_MAX_VALUE = 0x3ff

class XPS(IntEnum):
    NONE = 0
    SET_ON = 1
    SET_OFF = 2
    TOGGLE = 3
    RESET = 4
    PULSE_ON = 5
    PULSE_OFF = 6
    PULSE_CANCEL = 7

    def __str__(self):
        return self.name

class HeatingStatus(IntEnum):
    NONE = 0
    COMFORT = 1
    COMFORT_MIN_1 = 2
    COMFORT_MIN_2 = 3
    ENERGY_SAVING = 4
    FROST_FREE = 5
    OFF = 6

def IntHum2float(H: int) -> float:
    return (H & U10_MAX_VALUE) / 100.0

def IntPres2float(P: int) -> float:
    return (P & U10_MAX_VALUE) / 100.0 + 950.0


def IntTemp2float(T: int) -> float:
    return (T & U10_MAX_VALUE) / 10.0 - 28.0

def Temperature2float(raw: bytes) -> float:
    T = struct.unpack("h", raw)[0]
    return IntTemp2float(T)

def IsActiveT10(A: int):
    return A != U10_MAX_VALUE