#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations
import json

import requests
import ssl
import struct
import time

from .caniot import DeviceId

from abc import ABC, abstractmethod

from typing import Dict, List, Union, Iterable

from .url import URL

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Controller:
    def __init__(self, host: str = "192.0.2.1", port: int = None, secure: bool = False, 
                 cert: str = None, key: str = None, verify: str = None) -> None:

        self.host = host

        if port is None:
            self.port = 443 if secure else 80
        else:
            self.port = int(port)
        
        self.secure = secure
        self.cert = cert
        self.key = key
        self.verify = verify

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = False
        ssl_context.load_default_certs()

        self.session = None

        self.timeout = 5.0

        self.url = URL(f"{self.host}:{self.port}", secure=self.secure)

        self.default_headers = {
            "Timeout-ms": str(int(self.timeout * 1000)),
        }

        self.default_req = {
            "verify": False,
        }

        self.caniot: CaniotAPI = CaniotAPI(self)
    
    def is_http_session(self) -> bool:
        return self.session is not None

    def req(self,
            method,
            url,
            params=None,
            data=None,
            headers=None,
            cookies=None,
            files=None,
            auth=None,
            timeout=None,
            allow_redirects=True,
            proxies=None,
            hooks=None,
            stream=None,
            verify=None,
            cert=None,
            json=None
            ) -> requests.Response:
        
        request_method = self.session.request if self.session else requests.request

        t0 = time.perf_counter()
        resp = request_method(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json
        )
        t1 = time.perf_counter()

        logger.info(f"[{t1 - t0:.3f} s] {method} {url} status={resp.status_code} len={len(resp.content)}")

        return resp

    def get_info(self) -> Dict:
        return self.req("GET", self.url.sub("info")).json()

    def get_ha_stats(self) -> Dict:
        return self.req("GET", self.url.sub("ha/stats")).json()

    def get_devices_page(self, page: int = 0) -> List:
        return self.req("GET", self.url.sub(f"devices?page={page}")).json()

    def get_metrics(self) -> str:
        return self.req("GET", self.url.sub("metrics")).text

    def get_devices(self) -> List:
        page = 0
        devices = []

        while True:
            to_append = self.get_devices_page(page)
            if len(to_append) > 0:
                devices += to_append
                page += 1
            else:
                break
        
        return devices

    def send_can(self, arbitration_id: int, vals: Iterable[int] = None) -> requests.Response:
        if vals is None:
            vals = []
        arr = list(vals)
        assert len(arr) <= 8
        assert all(map(lambda x: 0 <= x <= 255 and isinstance(x, int), arr))
        url = self.url.sub("if/can/{id:X}").project(arbitration_id=arbitration_id)
        return self.req("POST", url, json=arr)
        
    def __enter__(self):
        if self.session:
            raise RuntimeError("Session already exists")

        self.session = requests.Session() 

        # TODO Setup session
        # SSL
        # Default headers
        # Timeout

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.session:
            self.session.close()
            self.session = None


class RestAPI(ABC):
    def __init__(self, ctrl, timeout: float = 1.0) -> None:
        self.ctrl: Controller = ctrl

        self.app_timeout: float = timeout

        self.app_timeout_header = {
            "Timeout-ms": str(int(self.app_timeout * 1000)),
        }

class CaniotAPI(RestAPI):
    def __init__(self, ctrl):
        super().__init__(ctrl)

    class Device:
        def __init__(self, api: CaniotAPI, did: DeviceId):
            self.api = api
            self.did = did

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def read_attribute(self, attr: int):
            return self.api.read_attribute(self.did, attr)

        def request_telemetry(self, ep: int):
            return self.api.request_telemetry(self.did, ep)

        def write_attribute(self, attr: int, value: int):
            return self.api.write_attribute(self.did, attr, value)

    def open_device(self, did: DeviceId) -> CaniotAPI.Device:
        return CaniotAPI.Device(self, did)

    def request_telemetry(self, did: Union[DeviceId, int], ep: int):
        url = self.ctrl.url.sub("devices/caniot/{did}/endpoint/{ep}/telemetry").project(**{
            "did": int(did),
            "ep": ep
        })
        return self.ctrl.req("GET", url, self.app_timeout_header).json()

    def command(self, did: Union[DeviceId, int], ep: int, vals: Iterable[int]):
        if vals is None:
            vals = []
        arr = list(vals)
        assert len(arr) <= 8
        assert all(map(lambda x: 0 <= x <= 255 and isinstance(x, int), arr))
        url = self.ctrl.url.sub("devices/caniot/{did}/endpoint/{ep}/command").project(**{
            "did": int(did),
            "ep": ep,
        })
        return self.ctrl.req("POST", url, json=arr, headers=self.app_timeout_header)

    def read_attribute(self, did: Union[DeviceId, int], attr: int) -> requests.Response:
        url = self.ctrl.url.sub("devices/caniot/{did}/attribute/{attr:x}").project(**{
            "did": int(did),
            "attr": attr
        })
        resp = self.ctrl.req("GET", url, headers=self.app_timeout_header)

        if resp.status_code == 200:
            return resp.json()

    def write_attribute(self, did: Union[DeviceId, int], attr: int, value: Union[int, bytes]):
        url = self.ctrl.url.sub("devices/caniot/{did}/attribute/{attr:x}").project(**{
            "did": int(did),
            "attr": attr
        })
        return self.ctrl.req("PUT", url, json={"value": str(hex(value))}, 
                             headers=self.app_timeout_header).json()

class TestAPI(RestAPI):
    def __init__(self, ctrl):
        super().__init__(ctrl)

