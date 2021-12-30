# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test flex channels on Bpod r2+

"""

from pybpodapi.protocol import Bpod, StateMachine


my_bpod = Bpod()  # For Bpod r2+ (with flex channels), do not provide the serial_port parameter. It will auto-detect.

my_bpod.set_flex_channel_types([2, 2, 3, 3])
my_bpod.set_analog_input_sampling_interval(100)
my_bpod.set_analog_input_thresholds([2000, 0, 0, 0], [4000, 0, 0, 0])
my_bpod.set_analog_input_threshold_polarity([0, 0, 0, 0], [0, 0, 0, 0])
my_bpod.set_analog_input_threshold_mode([0, 0, 0, 0])
# my_bpod.enable_analog_input_threshold(1, 1, 1)  # Can also be enabled from the state machine with ("AnalogThreshEnable", "0001") or ("AnalogThreshEnable", [0, 0, 0, 1]).
# my_bpod.enable_analog_input_threshold(1, 2, 1)


sma = StateMachine(my_bpod)
sma.add_state(
    state_name="WaitForThresh1",
    state_timer=0,
    state_change_conditions={"Flex1Trig1": "OpenValve"},
    output_actions=[
        ("Flex3AO", 5),
        ("AnalogThreshEnable", "0001")  # Binary string/list is MSB first so the rightmost bit is flex channel 1 (whose index is 0). One will enable both thresholds. Zero does not mean disabled.
    ]
)
sma.add_state(
    state_name="OpenValve",
    state_timer=1,
    state_change_conditions={"Tup": "WaitForThresh2"},
    output_actions=[("Valve1", 1)]
)
sma.add_state(
    state_name="WaitForThresh2",
    state_timer=0,
    state_change_conditions={"Flex1Trig2": "OpenValveAgain"},
    output_actions=[("Flex3AO", 4.5)]
)
sma.add_state(
    state_name="OpenValveAgain",
    state_timer=1,
    state_change_conditions={"Tup": "exit"},
    output_actions=[("Valve1", 1)]
)

my_bpod.send_state_machine(sma)
my_bpod.run_state_machine(sma)

my_bpod.close()
