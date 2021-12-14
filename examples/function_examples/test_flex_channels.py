# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test flex channels on Bpod r2+

"""

from pybpodapi.protocol import Bpod
from confapp import conf


my_bpod = Bpod(serial_port='COM8')
my_bpod.set_flex_channel_types([2, 2, 3, 3])
my_bpod.set_analog_input_thresholds([2048, 3000, 3500, 4000], [100, 1000, 1500, 2000])
my_bpod.set_analog_input_threshold_polarity([0, 0, 1, 1], [1, 0, 1, 0])
my_bpod.set_analog_input_threshold_mode([0, 0, 0, 0])
my_bpod.enable_analog_input_threshold(1, 1, 1)

my_bpod.close()

print("Target Bpod firmware version: ", conf.TARGET_BPOD_FIRMWARE_VERSION)
print("Firmware version (read from device): ", my_bpod.hardware.firmware_version)
print("Machine type version (read from device): ", my_bpod.hardware.machine_type)
