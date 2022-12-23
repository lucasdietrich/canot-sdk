#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

import sys

from pprint import pprint
from caniot.testclient import TestClient, ChunksGeneratorType

ip = ("192.168.10.240", 80)
ip = ("192.0.2.1", 80)

def simple_chunk_generator(size: int, chunks_size: int = 1024) -> ChunksGeneratorType:
    sent = 0
    while sent < size:
        tosend = min(chunks_size, size - sent)
        yield bytes([65 for _ in range(tosend)])
        sent += tosend

if __name__ == "__main__":

    test_n = 0

    # get first argument
    if len(sys.argv) > 1:
        test_n = int(sys.argv[1])

    print("========================================")
    print("Running test", test_n)
    print("========================================")

    t = TestClient(*ip)
    t.timeout = None

    if test_n == 0:
        res = t.test_big_data(20000, True)
    elif test_n == 1:
        res = t.test_stream(simple_chunk_generator(50000, 1024))
    elif test_n == 2:
        res = t.test_route_args(2, 3, 4)
    elif test_n == 3:
        res = t.test_headers({
            "App-Test-Header1": "Test-Value1",
            "App-Test-Header2": "Test-Value2",
            "App-Test-Header3": "Test-Value3",
        })
    elif test_n == 4:
        res = t.test_multipart()
    elif test_n == 5:
        res = t.test_session()
    elif test_n == 6:
        res = t.test_simultaneous(5, 5)

    print(res)

    try:
        if len(res.text):
            pprint(res.json())
    except:
        pass