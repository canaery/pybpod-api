# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test flex channels on Bpod r2+

"""

from pybpodapi.protocol import Bpod


my_bpod = Bpod()  # For Bpod r2+ (with flex channels), do not provide the serial_port parameter.

my_bpod.set_flex_channel_types([2, 2, 3, 3])
my_bpod.set_analog_input_thresholds([2048, 3000, 3500, 4000], [100, 1000, 1500, 2000])
my_bpod.set_analog_input_threshold_polarity([0, 0, 1, 1], [1, 0, 1, 0])
my_bpod.set_analog_input_threshold_mode([0, 0, 0, 0])
my_bpod.enable_analog_input_threshold(1, 1, 1)

my_bpod.close()
