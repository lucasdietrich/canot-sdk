# CANIOT Python SDK for zephyr-caniot-controller

## Install

Create virtual environment at the root of the zephyr workspace
```
python3 -m venv .venv
```

Install zephyr dependencies and caniot-sdk dependencies
```
pip install -r zephyr/scripts/requirements.txt
pip install -r zephyr-caniot-controller/scripts/caniot-sdk/requirements.txt
```

Add `.venv/lib/python3.8/site-packages/caniot.pth` (with following content) 
to reference the `caniot` packet from the SDK:
```
../../../../zephyr-caniot-controller/scripts/caniot-sdk
```

Or absolute path to the `caniot` packet from the SDK: