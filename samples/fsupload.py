#
# Copyright (c) 2022 Lucas Dietrich <ld.adecy@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#

from caniot.controller import Controller

import os 

from pprint import pprint

import logging
logger = logging.getLogger("caniot.controller")
logger.setLevel(logging.ERROR)

ip = "192.0.2.1" if True else "192.168.10.240"

fsdir = "./fs"
tmpdir = "./tmp"

with Controller(ip) as ctrl:
    for root, subdirs, files in os.walk(fsdir):
        dest_dir_path = os.path.join("/", root[len(fsdir):])
        for file in files:
            src_path = os.path.join(root, file)
            dest_path = os.path.join(dest_dir_path, file)
            print(f"Uploading {src_path} to {dest_path}")

            ctrl.upload(src_path, dest_path)

            # resp = ctrl.download(dest_path, dest_path + ".downloaded")