#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations
import json
from json.decoder import JSONDecodeError

import requests
import ssl
import struct
import time
import re

from .caniot import DeviceId, MsgId

from abc import ABC, abstractmethod

from typing import Dict, List, Union, Iterable, Optional

from .utils import MakeChunks

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

        # HTTP Timeout
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

    def _req(self,
             method,
             url, 
             **kwargs) -> requests.Response:
        request_method = self.session.request if self.session else requests.request

        t0 = time.perf_counter()
        resp = request_method(method, url, **kwargs)
        t1 = time.perf_counter()

        logger.info(f"[{t1 - t0:.3f} s] {method} {url} status={resp.status_code} len={len(resp.content)}")

        return resp

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
            ) -> Optional[Union[dict, str]]:
        resp = self._req(method, url, params=params, data=data, headers=headers, cookies=cookies, files=files, auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies, hooks=hooks, stream=stream, verify=verify, cert=cert, json=json)

        result = None

        if resp.status_code == 200:
            try:
                result = resp.json()
            except JSONDecodeError as e:
                result = resp.text
        elif resp.status_code == 204:
            result = ""
        else:
            logger.error(f"Request failed: {resp.status_code} {resp.reason}")

        return result

    def download(self, filepath: str, dest: str) -> bool:
        resp = self._req("GET", self.url.sub(f"files/{filepath}"))

        if resp.status_code == 200:
            with open(dest, "wb") as f:
                content = resp.content
                size = len(content)
                f.write(content)
                logger.info(f"Downloaded {filepath} [{size} B] to {dest}")
                return True
        else:
            logger.error(f"Failed to download {filepath} to {dest}")
            return False

    def upload(self, source: str,
               filepath: str,
               chunked_encoding: bool = True,
               chunks_size: int = 1024) -> requests.Response:
        rec_path = re.compile(
            r"^(\.?/)?(?P<filepath>([a-zA-Z0-9_]+/)*[a-zA-Z0-9_\-\.]+)$")

        m = rec_path.match(filepath)
        if m is None:
            raise ValueError(f"Invalid filepath: {filepath}")
        else:
            filepath = m.group("filepath")

        binary = open(source, "rb").read()
        
        if chunked_encoding:
            if chunks_size:
                binary = MakeChunks(binary, chunks_size)

        return self._req(
            "POST",
            self.url.sub(f"files/{filepath}"),
            data=binary,
        )

    def get_info(self) -> Dict:
        return self.req("GET", self.url.sub("info"))

    def get_ha_stats(self) -> Dict:
        return self.req("GET", self.url.sub("ha/stats"))

    def get_devices_page(self, page: int = 0) -> List:
        return self.req("GET", self.url.sub(f"devices?page={page}"))

    def get_metrics(self) -> str:
        return self.req("GET", self.url.sub("metrics")).text

    def get_room(self, room_id: int) -> dict:
        return self.req("GET", self.url.sub(f"room/{room_id}"))

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
        url = self.url.sub("if/can/{arbitration_id:X}").project(arbitration_id=arbitration_id)
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
    _app_timeout: float

    def __init__(self, ctrl, app_timeout: float = 0.5) -> None:
        self.ctrl: Controller = ctrl

        # Application timeout
        self.app_timeout = app_timeout

    def set_app_timeout(self, timeout: float):
        self._app_timeout = timeout
        self.app_timeout_header = {
            "Timeout-ms": str(int(self._app_timeout * 1000)),
        }
    
    def get_app_timeout(self) -> float:
        return self._app_timeout

    app_timeout = property(get_app_timeout, set_app_timeout)

    

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

        def read_attribute(self, attr: int) -> dict:
            return self.api.read_attribute(self.did, attr)

        def request_telemetry(self, ep: int):
            return self.api.request_telemetry(self.did, ep)

        def write_attribute(self, attr: int, value: int):
            return self.api.write_attribute(self.did, attr, value)

        def command(self, ep: int, data: Iterable[int]):
            return self.api.command(self.did, ep, data)

        def command_cls1(self, vals: Iterable[str]):
            return self.api.command_cls1(self.did, vals)
        
        def reboot(self):
            return self.api.reboot(self.did)

        def factory_reset(self):
            return self.api.factory_reset(self.did)

    def open_device(self, did: DeviceId) -> CaniotAPI.Device:
        return CaniotAPI.Device(self, did)

    def request_telemetry(self, did: Union[DeviceId, int], ep: int):
        url = self.ctrl.url.sub("devices/caniot/{did}/endpoint/{ep}/telemetry").project(**{
            "did": int(did),
            "ep": ep
        })
        return self.ctrl.req("GET", url, headers=self.app_timeout_header)

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

    def command_cls1(self, did: Union[DeviceId, int], vals: Iterable[str]):
        url = self.ctrl.url.sub("devices/caniot/{did}/endpoint/blc1/command").project(**{
            "did": int(did),
            "ep": MsgId.Endpoint.BoardLevelControl,
        })
        return self.ctrl.req("POST", url, json=list(vals), headers=self.app_timeout_header)

    def read_attribute(self, did: Union[DeviceId, int], attr: int) -> requests.Response:
        url = self.ctrl.url.sub("devices/caniot/{did}/attribute/{attr:x}").project(**{
            "did": int(did),
            "attr": attr
        })
        return self.ctrl.req("GET", url, headers=self.app_timeout_header)

    def write_attribute(self, did: Union[DeviceId, int], attr: int, value: Union[int, bytes]):
        url = self.ctrl.url.sub("devices/caniot/{did}/attribute/{attr:x}").project(**{
            "did": int(did),
            "attr": attr
        })
        return self.ctrl.req("PUT", url, json={"value": str(hex(value))}, 
                             headers=self.app_timeout_header)

    def factory_reset(self, did: Union[DeviceId, int]):
        url = self.ctrl.url.sub("devices/caniot/{did}/factory_reset").project(**{
            "did": int(did),
        })
        return self.ctrl.req("POST", url, headers=self.app_timeout_header)

    def reboot(self, did: Union[DeviceId, int]):
        url = self.ctrl.url.sub("devices/caniot/{did}/reboot").project(**{
            "did": int(did),
        })
        return self.ctrl.req("POST", url, headers=self.app_timeout_header)

class TestAPI(RestAPI):
    def __init__(self, ctrl):
        super().__init__(ctrl)

