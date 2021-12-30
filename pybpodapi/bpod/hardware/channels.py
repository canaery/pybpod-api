# !/usr/bin/python3
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)


class ChannelType(object):
    """
    Define if channel type is input or output.
    These values must be set according to Bpod firmware specification.
    """

    #: Input channel
    INPUT = 1

    #: Output channel
    OUTPUT = 2


class ChannelName(object):
    """
    Available channel names.
    These values must be set according to Bpod firmware specification.
    """

    #: Output channel with PWM support (e.g. Led)
    PWM = "PWM"

    #: Output channel for connecting a valve
    VALVE = "Valve"

    #: BNC channel
    BNC = "BNC"

    #: Wire channel
    WIRE = "Wire"

    #: Serial channel
    SERIAL = "Serial"

    #: Flex channel
    FLEX = "Flex"


class EventsPositions(object):
    """

    """

    def __init__(self):
        self.Event_USB = 0  # type: int
        self.Event_Port = 0  # type: int
        self.Event_BNC = 0  # type: int
        self.Event_Wire = 0  # type: int
        self.Event_Flex = 0  # type: int
        self.globalTimerStart = 0  # type: int
        self.globalTimerEnd = 0  # type: int
        self.globalTimerTrigger = 0  # type: int
        self.globalTimerCancel = 0  # type: int
        self.globalCounter = 0  # type: int
        self.globalCounterReset = 0  # type: int
        self.condition = 0  # type: int
        self.jump = 0  # type: int
        self.Tup = 0  # type: int
        self.output_USB = 0  # type: int
        self.output_VALVE = 0  # type: int
        self.output_BNC = 0  # type: int
        self.output_Wire = 0  # type: int
        self.output_PWM = 0  # type: int
        self.output_Flex = 0  # type: int
        self.analogThreshEnable = 0  # type: int
        self.analogThreshDisable = 0  # type: int

    def __str__(self):
        return (
            "Events Positions\n"
            "Event_USB: {Event_USB}\n"
            "Event_Port: {Event_Port}\n"
            "Event_BNC: {Event_BNC}\n"
            "Event_Wire {Event_Wire}\n"
            "Event_Flex: {Event_Flex}\n"
            "globalTimerStart: {globalTimerStart}\n"
            "globalTimerEnd: {globalTimerEnd}\n"
            "globalTimerTrigger: {globalTimerTrigger}\n"
            "globalTimerCancel: {globalTimerCancel}\n"
            "globalCounter: {globalCounter}\n"
            "globalCounterReset: {globalCounterReset}\n"
            "condition: {condition}\n"
            "jump: {jump}\n"
            "Tup: {Tup}\n"
            "output_USB: {output_USB}\n"
            "output_VALVE: {output_VALVE}\n"
            "output_BNC: {output_BNC}\n"
            "output_Wire: {output_Wire}\n"
            "output_PWM: {output_PWM}\n"
            "output_Flex: {output_Flex}\n"
            "analogThreshEnable: {analogThreshEnable}\n"
            "analogThreshDisable: {analogThreshDisable}\n"
            "".format(
               Event_USB=self.Event_USB,
               Event_Port=self.Event_Port,
               Event_BNC=self.Event_BNC,
               Event_Wire=self.Event_Wire,
               Event_Flex=self.Event_Flex,
               globalTimerStart=self.globalTimerStart,
               globalTimerEnd=self.globalTimerEnd,
               globalTimerTrigger=self.globalTimerTrigger,
               globalTimerCancel=self.globalTimerCancel,
               globalCounter=self.globalCounter,
               globalCounterReset=self.globalCounterReset,
               condition=self.condition,
               jump=self.jump,
               Tup=self.Tup,
               output_USB=self.output_USB,
               output_VALVE=self.output_VALVE,
               output_BNC=self.output_BNC,
               output_Wire=self.output_Wire,
               output_PWM=self.output_PWM,
               output_Flex=self.output_Flex,
               analogThreshEnable=self.analogThreshEnable,
               analogThreshDisable=self.analogThreshDisable
            )
        )


class Channels(object):
    """
    Bpod main class
    """

    def __init__(self):
        self.event_names = []
        self.input_channel_names = []
        self.output_channel_names = []
        self.events_positions = EventsPositions()

    def setup_input_channels(self, hardware, modules):
        """
        Generate event and input channel names
        """
        Pos = 0
        nUSB = 0
        nUART = 0
        nBNCs = 0
        nWires = 0
        nPorts = 0
        nFlex = 0

        for i in range(len(hardware.inputs)):
            if hardware.inputs[i] == "U":
                nUART += 1
                module = modules[nUART - 1]
                module_name = ""
                if module.connected:
                    module_name = module.name
                    self.input_channel_names += [module_name]
                else:
                    module_name = "Serial" + str(nUART)
                    self.input_channel_names += [module_name]

                n_module_event_names = len(module.event_names)

                for j in range(module.n_serial_events):
                    if j < n_module_event_names:
                        self.event_names += [module_name + "_" + module.event_names[j]]
                    else:
                        self.event_names += [module_name + "_" + str(j + 1)]
                    Pos += 1

            elif hardware.inputs[i] == "X":
                if nUSB == 0:
                    self.events_positions.Event_USB = Pos
                nUSB += 1
                self.input_channel_names += ["USB" + str(nUSB)]
                loops_n = int(hardware.max_serial_events / (len(modules) + 1))
                for j in range(loops_n):
                    self.event_names += ["SoftCode" + str(j + 1)]
                    Pos += 1
            
            elif hardware.inputs[i] == "P":
                if nPorts == 0:
                    self.events_positions.Event_Port = Pos
                nPorts += 1
                self.input_channel_names += ["Port" + str(nPorts)]
                self.event_names += [self.input_channel_names[-1] + "In"]
                Pos += 1
                self.event_names += [self.input_channel_names[-1] + "Out"]
                Pos += 1
            
            elif hardware.inputs[i] == "B":
                if nBNCs == 0:
                    self.events_positions.Event_BNC = Pos
                nBNCs += 1
                self.input_channel_names += ["BNC" + str(nBNCs)]
                self.event_names += [self.input_channel_names[-1] + "High"]
                Pos += 1
                self.event_names += [self.input_channel_names[-1] + "Low"]
                Pos += 1
            
            elif hardware.inputs[i] == "W":
                if nWires == 0:
                    self.events_positions.Event_Wire = Pos
                nWires += 1
                self.input_channel_names += ["Wire" + str(nWires)]
                self.event_names += [self.input_channel_names[-1] + "High"]
                Pos += 1
                self.event_names += [self.input_channel_names[-1] + "Low"]
                Pos += 1
            
            elif hardware.inputs[i] == "F":
                if nFlex == 0:
                    self.events_positions.Event_Flex = Pos
                
                # Check if channel is configured for digital input
                if hardware.flex_channel_types[nFlex] == 0:
                    nFlex += 1
                    self.input_channel_names += ["Flex" + str(nFlex)]
                    self.event_names += [self.input_channel_names[-1] + "High"]
                    Pos += 1
                    self.event_names += [self.input_channel_names[-1] + "Low"]
                    Pos += 1
                
                # Check if channel is configured for analog input
                elif hardware.flex_channel_types[nFlex] == 2:
                    nFlex += 1
                    self.input_channel_names += ["Flex" + str(nFlex)]
                    self.event_names += [self.input_channel_names[-1] + "Trig1"]
                    Pos += 1
                    self.event_names += [self.input_channel_names[-1] + "Trig2"]
                    Pos += 1

                # This means the flex channel must be configured as output
                else:
                    self.input_channel_names += ["---"]  # Placeholder to maintain appropriate index
                    self.event_names += ["---"]  # Placeholder for "high"/"trig1"
                    self.event_names += ["---"]  # Placeholder for "low"/"trig2"
                    nFlex += 1  # increment to maintain flex_channel_types index

        self.events_positions.globalTimerStart = Pos
        for i in range(hardware.n_global_timers):
            self.event_names += ["GlobalTimer" + str(i + 1) + "_Start"]
            Pos += 1

        self.events_positions.globalTimerEnd = Pos
        for i in range(hardware.n_global_timers):
            self.event_names += ["GlobalTimer" + str(i + 1) + "_End"]
            self.input_channel_names += ["GlobalTimer" + str(i + 1)]
            Pos += 1

        self.events_positions.globalCounter = Pos
        for i in range(hardware.n_global_counters):
            self.event_names += ["GlobalCounter" + str(i + 1) + "_End"]
            Pos += 1

        self.events_positions.condition = Pos
        for i in range(hardware.n_conditions):
            self.event_names += ["Condition" + str(i + 1)]
            Pos += 1

        self.event_names += ["Tup"]
        self.events_positions.Tup = Pos
        Pos += 1

        logger.debug("event_names: %s", self.event_names)
        logger.debug("events_positions: %s", self.events_positions)

    def setup_output_channels(self, hardware, modules):
        """
        Generate output channel names
        """
        nUSB = 0
        nUART = 0
        nVALVE = 0
        nBNCs = 0
        nWires = 0
        nPorts = 0
        nFlex = 0

        for i in range(len(hardware.outputs)):
            if hardware.outputs[i] == "U":
                nUART += 1
                module = modules[nUART - 1]
                module_name = ""
                if module.connected:
                    module_name = module.name
                    self.output_channel_names += [module_name]
                else:
                    module_name = "Serial" + str(nUART)
                    self.output_channel_names += [module_name]

            elif hardware.outputs[i] == "X":
                if nUSB == 0:
                    self.events_positions.output_USB = len(self.output_channel_names)
                nUSB += 1
                self.output_channel_names += ["SoftCode"]

            elif hardware.outputs[i] == "V":
                if nVALVE == 0:
                    self.events_positions.output_VALVE = len(self.output_channel_names)
                nVALVE += 1
                self.output_channel_names += ["Valve" + str(nVALVE)]  # Assume an SPI shift register mapping bits of a byte to 8 valves

            elif hardware.outputs[i] == "B":
                if nBNCs == 0:
                    self.events_positions.output_BNC = len(self.output_channel_names)
                nBNCs += 1
                self.output_channel_names += ["BNC" + str(nBNCs)]

            elif hardware.outputs[i] == "W":
                if nWires == 0:
                    self.events_positions.output_Wire = len(self.output_channel_names)
                nWires += 1
                self.output_channel_names += ["Wire" + str(nWires)]

            elif hardware.outputs[i] == "P":
                if nPorts == 0:
                    self.events_positions.output_PWM = len(self.output_channel_names)
                nPorts += 1
                self.output_channel_names += ["PWM" + str(nPorts)]
            
            elif hardware.outputs[i] == "F":
                if nFlex == 0:
                    self.events_positions.output_Flex = len(self.output_channel_names)
                
                # Check if channel is configured for digital output
                if hardware.flex_channel_types[nFlex] == 1:
                    nFlex += 1
                    self.output_channel_names += ["Flex" + str(nFlex) + "DO"]
                
                # Check if channel is configured for analog output
                elif hardware.flex_channel_types[nFlex] == 3:
                    nFlex += 1
                    self.output_channel_names += ["Flex" + str(nFlex) + "AO"]

                # This means the flex channel must be configured as input
                else:
                    self.output_channel_names += ["---"]  # placeholder to maintain appropriate index.
                    nFlex += 1  # increment to maintain the flex_channel_types index

        self.output_channel_names += ["GlobalTimerTrig"]
        self.events_positions.globalTimerTrigger = len(self.output_channel_names) - 1
        self.output_channel_names += ["GlobalTimerCancel"]
        self.events_positions.globalTimerCancel = len(self.output_channel_names) - 1
        self.output_channel_names += ["GlobalCounterReset"]
        self.events_positions.globalCounterReset = len(self.output_channel_names) - 1

        if hardware.machine_type > 3:
            self.output_channel_names += ["AnalogThreshEnable"]
            self.events_positions.analogThreshEnable = len(self.output_channel_names) - 1
            self.output_channel_names += ["AnalogThreshDisable"]
            self.events_positions.analogThreshDisable = len(self.output_channel_names) - 1
        
        logger.debug("output_channel_names: %s", self.output_channel_names)
        logger.debug("events_positions: %s", self.events_positions)

    def get_event_name(self, event_idx):
        """

        :param event_idx:
        :return:
        """

        try:
            event_name = self.event_names[event_idx]
        except IndexError:
            event_name = "unknown event name"

        return event_name

    def __str__(self):

        buff = "\n****************** EVENTS ******************\n"
        for idx, event in enumerate(self.event_names):
            buff += "{0: >3} : {1: <24}".format(idx, event)
            if ((idx + 1) % 3) == 0 and idx != 0:
                buff += "\n"

        buff += "\n\n****************** INPUT CHANNELS ******************\n"
        for idx, channel in enumerate(self.input_channel_names):
            buff += "{0: >3} : {1: <24}".format(idx, channel)
            if ((idx + 1) % 3) == 0 and idx != 0:
                buff += "\n"

        buff += "\n\n****************** OUTPUT CHANNELS ******************\n"
        for idx, channel in enumerate(self.output_channel_names):
            buff += "{0: >3} : {1: <24}".format(idx, channel)
            if ((idx + 1) % 3) == 0 and idx != 0:
                buff += "\n"

        return "SMA Channels\n" + buff + "\n\n"
