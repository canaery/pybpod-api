# !/usr/bin/python3
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)


class ReceiveMessageHeader(object):
    """
    Define names for message headers received from the Bpod device.

    The message header is the first byte (character) on a message received.
    """
    
    #: Bpod writes 0xDE every 100ms on its primary COM port.
    #: 0xDE in decimal is 222 which refers to firmware version 22.
    PRIMARY_PORT_PING = 222

    #: Success code from HANDSHAKE command
    HANDSHAKE_OK = "5"

    #: Handshake response on the secondary serial port after sending
    #: the SECONDARY_PORT_HANDSHAKE command on the primary serial port.
    SECONDARY_PORT_HANDSHAKE_OK = 222

    #: Handshake response on the analog serial port after sending
    #: the ANALOG_PORT_HANDSHAKE command on the primary serial port.
    ANALOG_PORT_HANDSHAKE_OK = 223

    #: Success code from ENABLE_PORTS command
    ENABLE_PORTS_OK = 1

    #: Success code from SET_FLEX_CHANNEL_TYPES command
    SET_FLEX_CHANNEL_TYPES_OK = 1
    
    #: Success code from SET_ANALOG_INPUT_THRESHOLDS command
    SET_ANALOG_INPUT_THRESHOLDS_OK = 1

    #: Success code from SET_ANALOG_INPUT_THRESHOLD_POLARITY command
    SET_ANALOG_INPUT_THRESHOLD_POLARITY_OK = 1

    #: Success code from SET_ANALOG_INPUT_THRESHOLD_MODE command
    SET_ANALOG_INPUT_THRESHOLD_MODE_OK = 1

    #: Success code from ENABLE_ANALOG_INPUT_THRESHOLD command
    ENABLE_ANALOG_INPUT_THRESHOLD_OK = 1

    #: Success code from SYNC_CHANNEL_MODE command
    SYNC_CHANNEL_MODE_OK = 1

    #: Success code from RUN_STATE_MACHINE command
    STATE_MACHINE_INSTALLATION_STATUS = 1

    #: Success code from LOAD_SERIAL_MESSAGE command
    LOAD_SERIAL_MESSAGE_OK = 1

    #: Success code from RESET_SERIAL_MESSAGES command
    RESET_SERIAL_MESSAGES = 1

    #: Success code from RESET_CLOCK command
    RESET_CLOCK_OK = 1
    
    #: Module requested event
    MODULE_REQUESTED_EVENT = ord("#")

    #: Module events names
    MODULE_EVENT_NAMES = ord("E")

    #: Success code from DISCONNECT command
    DISCONNECT_OK = "1"
