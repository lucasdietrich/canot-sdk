from typing import Iterable

def MakeChunks(data: bytes, size: int) -> Iterable:
    for i in range(0, len(data), size):
        yield data[i:i+size]

def is_bit_set(n: int, bit: int = 0) -> bool:
    return bool(n & (1 << bit))