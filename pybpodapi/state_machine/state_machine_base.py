# !/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from pybpodapi.state_machine.conditions import Conditions
from pybpodapi.state_machine.global_counters import GlobalCounters
from pybpodapi.state_machine.global_timers import GlobalTimers

from pybpodapi.bpod.hardware.events import EventName
from pybpodapi.bpod.hardware.output_channels import OutputChannel
from pybpodapi.bpod.hardware.channels import ChannelName

logger = logging.getLogger(__name__)


class StateMachineBase(object):
    """
    Each Bpod trial is programmed as a virtual finite state machine. This ensures precise timing of events - for any
    state machine you program, state transitions will be completed in less than 250 microseconds - so inefficient
    coding won't reduce the precision of events in your data.

    .. warning:: A lot of data structures are kept here for compatibility with original matlab library which are not
                 so python-like. Anyone is welcome to enhance this class but keep in mind that it will affect the whole
                 pybpodapi library.

    :ivar Hardware hardware: bpod box hardware description associated with this state machine
    :ivar Channels channels: bpod box channels handling
    :ivar list(str) state_names: list that holds state names added to this state machine
    :ivar list(float) state_timers: list that holds state timers
    :ivar int total_states_added: holds all states added, even if name is repeated
    :ivar list(int) state_timer_matrix: TODO:
    :ivar Conditions conditions: holds conditions
    :ivar GlobalCounters global_counters: holds global timers
    :ivar GlobalTimers global_timers: holds global counters
    :ivar list(tuple(int)) input_matrix: TODO:
    :ivar list(str) manifest: list of states names that have been added to the state machine
    :ivar list(str) undeclared: list of states names that have been referenced but not yet added
    :ivar tuple(str) meta_output_names: TODO:
    :ivar list(tuple(int)) output_matrix: TODO:
    :ivar bool is_running: whether this state machine is being run on bpod box

    """

    def __init__(self, bpod):
        """

        :param Hardware hardware: hardware description associated with this state machine
        """
        self.hardware = bpod.hardware  # type: Hardware

        self.state_names = []  # type: list(str)
        self.state_timers = [0] * self.hardware.max_states  # list(float)
        self.total_states_added = 0  # type: int

        # state change conditions
        self.state_timer_matrix = [0] * self.hardware.max_states
        self.conditions = Conditions(
            self.hardware.max_states, self.hardware.n_conditions
        )
        self.global_counters = GlobalCounters(
            self.hardware.max_states, self.hardware.n_global_counters
        )
        self.global_timers = GlobalTimers(
            self.hardware.max_states, self.hardware.n_global_timers
        )
        self.input_matrix = [[] for i in range(self.hardware.max_states)]

        # should be incremented whenever the user uses a timer
        self.n_global_timers_used = 0

        # should be incremented whenever the user uses a counter
        self.n_global_counters_used = 0

        # should be incremented whenever the user uses a conditions
        self.n_global_conditions_used = 0

        # if active uses the state 255 to store the previous state, so the user can go back in the state machine
        self.use_255_back_signal = False

        # List of states that have been added to the state machine
        self.manifest = []  # type: list(str)

        # List of states that have been referenced but not yet added
        self.undeclared = []  # type:list(str)

        # output actions
        self.output_matrix = [[] for i in range(self.hardware.max_states)]

        # 0 = manually program serial message library with load_serial_message() function.
        # 1 = implicitly program from the state machine during trial onset.
        self.serial_message_mode = 0
        self.n_serial_messages = [0] * self.hardware.n_uart_channels  # List of the number of serial messages for each channel.
        
        # self.serial_messages (below) is a list of dicts where each dict contains all the serial messages (up to 256) of each uart channel.
        # Contains two types of keys: one key type is the serial message list converted to a string whose paired value
        # is the serial message's index (for use by the bpod to store the message in an array), the second key type is
        # the serial message's index (int) whose paired value is the serial message list itself (for building the state machine).
        # Combination of these two is used for instant access to check if the serial message has been stored already and to
        # get the message and index instead of looping through a list of serial messages and comparing the serial message
        # that is to be used with the serial messages already stored to find out if it is a new serial message to be loaded.
        # Of course, this can also be separated into two lists of dicts.
        self.serial_messages = [{}] * self.hardware.n_uart_channels
        
        self.is_running = False

    def add_state(
        self, state_name, state_timer=0, state_change_conditions={}, output_actions=()
    ):
        """
        Adds a state to an existing state matrix.

        :param str name: A character string containing the unique name of the state. The state will automatically be assigned a number for internal use and state synchronization via the sync port
        :param float timer: The state timer value, given in seconds. This value must be zero or positive, and can range between 0-3600s. If set to 0s and linked to a state transition, the state will still take ~100us to execute the state's output actions before the transition completes
        :param dict state_change_conditions: Dictionary whose keys are names of a valid input event (state change) and values are names of states to enter if the previously listed event occurs (or 'exit' to exit the matrix and return all captured data)
        :param list(tuple) output_actions: a list of binary tuples where first value should contain the name of a valid output action and the second value should contain the value of the previously listed output action (see output actions for valid values).        

        Example:

        .. code-block:: python

            sma.add_state(
                state_name='Port1Lit',
                state_timer=.25,
                state_change_conditions={'Tup': 'Port3Lit', 'GlobalTimer1_End': 'exit'},
                output_actions=[('PWM1', 255)])

        """

        # TODO: WHY DO WE NEED THIS IF-ELSE?
        if state_name not in self.manifest:
            self.state_names.append(state_name)
            self.manifest.append(state_name)
            state_name_idx = len(self.manifest) - 1
        else:
            state_name_idx = self.manifest.index(state_name)
            self.state_names[state_name_idx] = state_name

        self.state_timer_matrix[state_name_idx] = state_name_idx

        self.state_timers[state_name_idx] = state_timer

        for event_name, event_state_transition in state_change_conditions.items():
            try:
                event_code = self.hardware.channels.event_names.index(event_name)
                logger.debug("Event code: %s", event_code)
            except:
                raise SMAError(
                    "Error creating state: "
                    + state_name
                    + ". "
                    + event_name
                    + " is an invalid event name."
                )

            if event_state_transition in self.manifest:
                destination_state_number = self.manifest.index(event_state_transition)
            else:
                if event_state_transition in ["exit", ">exit"]:
                    destination_state_number = float("NaN")

                elif event_state_transition in ["back", ">back"]:
                    self.use_255_back_signal = True
                    destination_state_number = 255
                else:  # Send to an undeclared state (replaced later with actual state in myBpod.sendStateMachine)
                    self.undeclared.append(event_state_transition)
                    destination_state_number = (len(self.undeclared) - 1) + 10000

            if EventName.is_state_timer(event_name):
                self.state_timer_matrix[state_name_idx] = destination_state_number

            elif EventName.is_condition(event_name):
                self.conditions.matrix[state_name_idx].append(
                    (event_code, destination_state_number)
                )

            elif EventName.is_global_counter_end(event_name):
                self.global_counters.matrix[state_name_idx].append(
                    (event_code, destination_state_number)
                )

            elif EventName.is_global_timer_trigger(event_name):

                if isinstance(event_state_transition, str):
                    v = int(event_state_transition, 2)
                else:
                    v = event_state_transition
                self.global_timers.end_matrix[state_name_idx] = v

            elif EventName.is_global_timer_cancel(event_name):

                if isinstance(event_state_transition, str):
                    v = int(event_state_transition, 2)
                else:
                    v = event_state_transition

                self.global_timers.end_matrix[state_name_idx] = v

            elif EventName.is_global_timer_end(event_name):
                self.global_timers.end_matrix[state_name_idx].append(
                    (event_code, destination_state_number)
                )

            elif EventName.is_global_timer_start(event_name):
                self.global_timers.start_matrix[state_name_idx].append(
                    (event_code, destination_state_number)
                )

            else:
                self.input_matrix[state_name_idx].append(
                    (event_code, destination_state_number)
                )

        for action_name, action_value in output_actions:
            if action_name == "Valve":
                output_code = self.hardware.channels.output_channel_names.index(
                    OutputChannel.Valve + str(action_value)
                )
                output_value = 1

                """
                elif action_name == 'ValveState':
                    output_code  = self.hardware.channels.output_channel_names.index( OutputChannel.Valve+str(action_value))
                    output_value = math.pow(2, action_value - 1)
                """
            elif action_name == OutputChannel.LED:
                output_code = self.hardware.channels.output_channel_names.index(
                    ChannelName.PWM + str(action_value)
                )
                output_value = 255

            else:
                try:
                    output_code = self.hardware.channels.output_channel_names.index(action_name)
                
                except:
                    raise SMAError(
                        "Error creating state: "
                        + state_name
                        + ". "
                        + action_name
                        + " is an invalid output name."
                    )

                output_value = action_value

            if action_name == OutputChannel.GlobalCounterReset:
                self.global_counters.reset_matrix[output_value] = 1  # output_value (or action_value) is actually the global counter number that is to be resetted.

            # For backwards compatability, integers specifying global timers convert to equivalent binary decimals.
            # To specify binary, use a string of bits.
            if (output_code == self.hardware.channels.events_positions.globalTimerTrigger):
                self.global_timers.triggers_matrix[state_name_idx] = 2 ** (output_value - 1)

            if output_code == self.hardware.channels.events_positions.globalTimerCancel:
                self.global_timers.cancels_matrix[output_value - 1] = 1

            # Check if output_code refers to a flex channel.
            if (output_code >= self.hardware.channels.events_positions.output_Flex) and (output_code < self.hardware.channels.events_positions.output_BNC):
                flex_channel = output_code - self.hardware.channels.events_positions.output_Flex  # Find the flex channel index.
                if self.hardware.flex_channel_types[flex_channel] == 3:
                    # This means the flex channel is configured for analog output, so convert voltage to the integer bit value.
                    maxFlexVoltage = 5
                    if (action_value < 0) or (action_value > maxFlexVoltage):
                        raise SMAError("Error creating state: Flex channel voltages must be in the range [0, 5]")
                    output_value = round((action_value / maxFlexVoltage) * 4095)
            
            # Check if output_code refers to AnalogThreshEnable/Disable.
            if ((output_code == self.hardware.channels.events_positions.analogThreshEnable)
                or (output_code == self.hardware.channels.events_positions.analogThreshDisable)):
                # Convert the ones and zeros (that represent each flex channel) into a single integer value.
                if isinstance(action_value, list) and (len(action_value) == self.hardware.n_flex_channels):
                    try:
                        # If list of integer ones and zeros, concatenate to a string and then convert the binary to the integer value.
                        output_value = int("".join(str(x) for x in action_value), base=2)
                    except ValueError:
                        raise SMAError("Error creating state: AnalogThreshEnable/Disable action value must contain only ones and zeros.")
                elif isinstance(action_value, str) and (len(action_value) == self.hardware.n_flex_channels):
                    try:
                        # If string of ones and zeros, convert to the integer value.
                        output_value = int(action_value, base=2)
                    except ValueError:
                        raise SMAError("Error creating state: AnalogThreshEnable/Disable action value must contain only ones and zeros.")
                else:
                    raise SMAError(
                        "Error creating state: AnalogThreshEnable/Disable action value must be either a list or string of ones and zeros and of "
                        "length equal to the number of flex channels where each bit indicates the flex channel to enable/disable thresholds on. "
                        "Binary is MSB first so the rightmost bit will be flex channel index 0."
                        "Note that a zero bit in the AnalogThreshEnable action does not disable thresholds on that flex channel and a zero bit "
                        "in the AnalogThreshDisable action does not enable thresholds on that flex channel."
                    )
            
            # Check if output_code refers to a UART serial channel (aka module).
            if (output_code < self.hardware.channels.events_positions.output_USB):
                if isinstance(action_value, list):
                    # This means implicit programming of serial message library.
                    if (len(action_value) == 0) or (len(action_value) > self.hardware.serial_message_max_bytes):
                        raise SMAError("Error creating state: serial message cannot be empty or greater than %s bytes.", self.hardware.serial_message_max_bytes)
                    
                    self.serial_message_mode = 1
                    if str(action_value) not in self.serial_messages[output_code]:
                        if self.n_serial_messages[output_code] < 256:
                            # This means the serial message is new and has not yet been loaded.
                            # So convert the serial message list to a string and use that to create a key in the dictionary
                            # for the specified UART channel (output_code indicates the index of UART channel) and set the
                            # value of the key to be the serial message number (aka the index). Then use the message index to
                            # create another key in the same dictionary and set the value of that key to be the actual serial
                            # message list. This will allow for instant retrieval of the message index when the message has
                            # been loaded and is used again. The message index is used by the Bpod to retrieve the message
                            # within the Bpod's serial message library (firmware stores all loaded serial messages in an array).
                            msg_index = self.n_serial_messages[output_code]
                            self.serial_messages[output_code][str(action_value)] = msg_index  # This allows instant checking whether message was loaded already or not.
                            self.serial_messages[output_code][msg_index] = action_value  # This allows instant retrieval of the message (used later when building the state machine matrix).
                            self.n_serial_messages[output_code] += 1  # increment the index.
                            output_value = msg_index  # Assign the index to the output value because the Bpod will use the index to retrieve the stored serial message.
                        else:
                            raise SMAError("Error creating state: Cannot load more than 256 different serial messages on a single UART channel.")
                    else:
                        # This means the serial message is not new and is already stored in the serial message library.
                        # So convert the serial message list to a string and use that as a key in the dictionary for the
                        # specified UART channel (output_code indicates the index of the UART channel) to find the message's index.
                        msg_index = self.serial_messages[output_code][str(action_value)]
                        output_value = msg_index  # Assign the index to the output value because the Bpod will use the index to retrieve the stored serial message.

            
            self.output_matrix[state_name_idx].append((output_code, output_value))

        self.total_states_added += 1

    def set_global_timer_legacy(self, timer_id=None, timer_duration=None):
        """
        Set global timer (legacy version)

        :param int timer_ID:
        :param float timer_duration: timer duration in seconds
        """
        self.global_timers.timers[timer_id - 1] = timer_duration

    def set_global_timer(
        self,
        timer_id,
        timer_duration,
        on_set_delay=0,
        channel=None,
        on_message=1,
        off_message=0,
        loop_mode=0,
        loop_intervals=0,
        send_events=1,
        oneset_triggers=None,
    ):
        """
        Sets the duration of a global timer. Unlike state timers, global timers can be triggered from any state (as an
        output action), and handled from any state (by causing a state change).

        :param int timer_ID: the number of the timer you are setting (an integer, 1-5).
        :param float timer_duration: the duration of the timer, following timer start (0-3600 seconds)
        :param float on_set_delay:
        :param str channel: channel/port name Ex: 'PWM2'
        :param int on_message:
        """
        timer_channel_idx = 255
        if channel is not None:
            try:
                timer_channel_idx = self.hardware.channels.output_channel_names.index(
                    channel
                )  # type: int
            except:
                raise SMAError(
                    "Error: {0} is an invalid output channel name.".format(channel)
                )

        index = timer_id - 1

        self.global_timers.timers[index] = timer_duration
        self.global_timers.on_set_delays[index] = on_set_delay
        self.global_timers.channels[index] = timer_channel_idx
        self.global_timers.on_messages[index] = on_message
        self.global_timers.off_messages[index] = off_message

        self.global_timers.loop_mode[index] = loop_mode
        self.global_timers.loop_intervals[index] = loop_intervals
        self.global_timers.send_events[index] = send_events

        if len(self.global_timers.onset_matrix) < index:
            for i in range(len(self.global_timers.onset_matrix), index + 1):
                self.global_timers.onset_matrix.append(0)

        if oneset_triggers is not None:
            self.global_timers.onset_matrix[index] = oneset_triggers

    def set_global_counter(
        self, counter_number=None, target_event=None, threshold=None
    ):
        """
        Sets the threshold and monitored event for one of the 5 global counters. Global counters can count instances of
        events, and handle when the count exceeds a threshold from any state (by triggering a state change).

        :param int counter_number: the number of the counter you are setting (an integer, 1-5).
        :param str target_event: port where to listen for event to count
        :param int threshold: number of times that should be count until trigger timer
        """
        event_code = self.hardware.channels.event_names.index(target_event)
        self.global_counters.attached_events[counter_number - 1] = event_code
        self.global_counters.thresholds[counter_number - 1] = threshold

    def set_condition(self, condition_number, condition_channel, channel_value):
        """
        Set condition

        :param int condition_number:
        :param str condition_channel:
        :param int channel_value:
        """
        channel_code = self.hardware.channels.input_channel_names.index(
            condition_channel
        )
        self.conditions.channels[condition_number - 1] = channel_code
        self.conditions.values[condition_number - 1] = channel_value


class SMAError(Exception):
    pass
