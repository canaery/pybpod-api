# !/usr/bin/python3
# -*- coding: utf-8 -*-

import logging, csv, uuid
from pyforms import conf
from datetime import datetime

import pybpodapi
#from pybpodapi.state_machine import StateMachine
from pybpodapi.com.messaging.trial                  import Trial
from pybpodapi.com.messaging.event_occurrence       import EventOccurrence
from pybpodapi.com.messaging.state_occurrence       import StateOccurrence
from pybpodapi.com.messaging.softcode_occurrence    import SoftcodeOccurrence
from pybpodapi.com.messaging.session_info           import SessionInfo

logger = logging.getLogger(__name__)

class Session(object):
    """
    Stores information about bpod run, including the list of trials.
    
    :ivar list(Trial) trials: a list of trials
    :ivar int firmware_version: firmware version of Bpod when experiment was run
    :ivar int bpod_version: version of Bpod hardware when experiment was run
    :ivar datetime start_timestamp: it stores session start timestamp

    """

    INFO_PROTOCOL_NAME      = 'PROTOCOL-NAME'
    INFO_SESSION_STARTED    = 'SESSION-STARTED'
    INFO_SESSION_ENDED      = 'SESSION-ENDED'
    INFO_SERIAL_PORT        = 'SERIAL-PORT'
    INFO_BPODAPI_VERSION    = 'BPOD-API-VERSION'

    def __init__(self, path=None):
        self.history            = []                # type: list[Trial]
        self.trials             = []                # type: list[Trial]
        self.firmware_version   = None              # type: int
        self.bpod_version       = None              # type: int
        self.start_timestamp    = datetime.now()    # type: datetime

        self.log_function = conf.PYBPOD_API_PUBLISH_DATA_FUNC

        if path:
            with open(path, 'w') as csvfile:
                csvwriter = csv.writer(path)
                json.dump(data2save, jsonfile)
            self.csv = CSVWriter(
                path,
                columns_headers=['TYPE', 'PC-TIME', 'BPOD-INITIAL-TIME', 'BPOD-FINAL-TIME', 'MSG', '+INFO'],
                software='PyBpod API v'+str(pybpodapi.__version__),
                def_url='http://pybpod-api.readthedocs.org',
                def_text='This file contains data recorded during a session from the PyBpod system'
            )
            self.csvwriter.open()
        else:
            self.csvwriter  = None


    def __del__(self):
        if self.csvwriter: 
            self.csvwriter.writerow( SessionInfo( self.INFO_SESSION_ENDED, datetime.now() ).tolist() )
            self.csvwriter.close()
        


    def __add__(self, msg):
        """
        Add new trial to this session and associate a state machine to it

        :param pybpodapi.model.state_machine sma: state machine associated with this trial
        """
        if isinstance(msg, Trial): 
            self.trials.append(msg)
        elif not isinstance(msg, SessionInfo): 
            self.current_trial += msg

        self.history.append(msg)

        if self.csvwriter:  self.csvwriter.writerow( msg.tolist() )

        self.log_function(msg)      
        return self


    def add_trial_events(self):

        current_trial = self.current_trial  # type: Trial
        sma           = current_trial.sma


        visitedStates = [0] * current_trial.sma.total_states_added
        # determine unique states while preserving visited order
        uniqueStates = []
        nUniqueStates = 0
        uniqueStateIndexes = [0] * len(current_trial.states)

        for i in range(len(current_trial.states)):
            if current_trial.states[i] in uniqueStates:
                uniqueStateIndexes[i] = uniqueStates.index(current_trial.states[i])
            else:
                uniqueStateIndexes[i] = nUniqueStates
                nUniqueStates += 1
                uniqueStates.append(current_trial.states[i])
                visitedStates[current_trial.states[i]] = 1

        # Create a 2-d matrix for each state in a list
        uniqueStateDataMatrices = [[] for i in range(len(current_trial.states))]

        # Append one matrix for each unique state
        for i in range(len(current_trial.states)):
            uniqueStateDataMatrices[uniqueStateIndexes[i]] += [
                (current_trial.state_timestamps[i], current_trial.state_timestamps[i + 1])]

        for i in range(nUniqueStates):
            thisStateName = sma.state_names[uniqueStates[i]]

            for state_dur in uniqueStateDataMatrices[i]:
                self += StateOccurrence(thisStateName, state_dur[0], state_dur[1] )
                
        logger.debug("State names: %s", sma.state_names)
        logger.debug("nPossibleStates: %s", sma.total_states_added)
        for i in range(sma.total_states_added):
            thisStateName = sma.state_names[i]
            if not visitedStates[i]:
                self += StateOccurrence(thisStateName, float('NaN'), float('NaN') )
                
        logger.debug("Trial states: %s", [str(state) for state in current_trial.states_occurrences])

        # save events occurrences on trial
        #current_trial.events_occurrences = sma.raw_data.events_occurrences  # type: list

        logger.debug("Trial events: %s", [str(event) for event in current_trial.events_occurrences])

        logger.debug("Trial info: %s", str(current_trial))

    @property
    def current_trial(self):
        """
        Get current trial
        
        :rtype: Trial 
        """
        return self.trials[-1] if len(self.trials)>0 else None


    @current_trial.setter
    def current_trial(self, value):
        """
        Get current trial
        
        :rtype: Trial 
        """
        self.trials[-1] = value