from typing import Iterable

def MakeChunks(data: bytes, size: int) -> Iterable:
    for i in range(0, len(data), size):
        yield data[i:i+size]