# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Example adapted from Josh Sanders' original version on Sanworks Bpod repository
"""
from pybpodapi.protocol import Bpod, StateMachine


"""
Run this protocol now
"""

my_bpod = Bpod()

sma = StateMachine(my_bpod)

sma.set_condition(condition_number=1, condition_channel='Port2', channel_value=1)

sma.add_state(
	state_name='Port1Light',
	state_timer=1,
	state_change_conditions={Bpod.Events.Tup: 'Port2Light'},
	output_actions=[(Bpod.OutputChannels.PWM1, 255)])

sma.add_state(
	state_name='Port2Light',
	state_timer=1,
	state_change_conditions={Bpod.Events.Tup: 'Port3Light', Bpod.Events.Condition1: 'Port3Light'},
	output_actions=[(Bpod.OutputChannels.PWM2, 255)])

sma.add_state(
	state_name='Port3Light',
	state_timer=1,
	state_change_conditions={Bpod.Events.Tup: 'exit'},
	output_actions=[(Bpod.OutputChannels.PWM3, 255)])

my_bpod.send_state_machine(sma)

my_bpod.run_state_machine(sma)

print("Current trial info: {0}".format(my_bpod.session.current_trial))

my_bpod.stop()