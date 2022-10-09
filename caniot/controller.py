#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

import requests
import ssl
import struct
import time

from typing import Dict

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
        return self.req("GET", self.url.sub("/info")).json()

    def get_ha_stats(self) -> Dict:
        return self.req("GET", self.url.sub("/ha/stats")).json()

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