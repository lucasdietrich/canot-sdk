#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

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

t = TestClient(*ip)

# res = t.test_big_data(20000)
# res = t.test_stream(simple_chunk_generator(30000, 2048))

# res = t.test_route_args(2, 3, 4)
# res = t.test_headers({
#     "App-Test-Header1": "Test-Value1",
#     "App-Test-Header2": "Test-Value2",
#     "App-Test-Header3": "Test-Value3",
# })
# res = t.test_multipart()
# res = t.test_session()
# res = t.test_simultaneous(5)

print(res)

if len(res.text):
    pprint(res.json())