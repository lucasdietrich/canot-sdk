import argparse

"""
cli.py --hostname=192.168.10.240 --port=80 --cert=cert.pem --key=key.pem --ca=ca.pem
cli.py --config config.toml

cli.py caniot 1,0 attr read 0x20D0
cli.py caniot 1,0 attr write 0x20D0 500
cli.py caniot 1,0 attr write CfgTelemetryPeriodMs 500
cli.py caniot 1,0 cmd ep0 [0x00, 0x01]
cli.py caniot 1,0 cmd blc factory_reset
cli.py caniot broadcast request_telemetry blc

cli.py dfu firmware.bin --reboot
cli.py test 1 --n=10 --delay=1.0

"""