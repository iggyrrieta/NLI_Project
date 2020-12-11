"""! @brief Main flow process control"""

import os
import sys
import pandas as pd
import logging.config
import random

# ROOT FOLDER : Make things easier setting the root folder as the origin
#root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
#sys.path.insert(0, root_path)

# SP
from sp_recognition.main import SPCore
# NLU
from nlu_core.main import NLUCore
from nlg_core.main import dm_nlg
# Conversation trackers
from dm_core.ct_interest import ConversationTracker as ct_interest
from dm_core.ct_restaurant import ConversationTracker as ct_restaurant

#==============================================================================
#   LOGGER
#
# This is the main logger
#==============================================================================
root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
logging.config.fileConfig(f"{root_folder}/data/log.ini")
logger = logging.getLogger('main_logger')
#==============================================================================

class DMCore:
    """Agent that interacts with the user.
       - sr_core -> dm_core <-> nlu_core
                            <-> ct_{intent}
                             -> nlg_core
    """

    def __init__(self, db_name='data.csv'):

        # Init. Reset all when instantiate
        self.user_utterance = ''  # Just the client conversation input (text), received from speech recognition module
        self.predicted = ''  # Conversation prediction, based on that we'll move to one ct or another
        self.all_intents_probability = None
        self.conversation_tracker = None  # Conversation tracker (ct) selected
        self.conversation_started = False  # Check if conversation started

        self.next_agent_action = None  # Defines next action to be performed by the agent, action
        self.next_agent_action_type = None  # Defines what type of action is performing the agent
        self.agent_actions = []  # All the actions of the agent
        self.detected_entities = None
        self.detected_pos_dobj = None

        # Access to database
        self.root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        self.db_path = f'{self.root_path}/NLI_Project/data/{db_name}'

        # Read db file
        data = pd.read_csv(self.db_path, delimiter=',')
        self.agent_intents = set(data.intent)

    def __repr__(self):
        return '\n'.join([
            'DIALOGUE MANAGER',
            '----------------',
            f'STARTED: {self.conversation_started}',
            f'LAST_TEXT: {self.user_utterance}',
            f'AGENT INTENTS: {self.agent_intents}',
            f'INTENT: {self.predicted}',
            f'TRACKER: {self.conversation_tracker}',
        ])

    def _get_intent(self):
        ''' GET INTENT FROM NLU_CORE
            Call -> nlu_core
            Get  -> prediction and probabilities from an input text
        '''
        nlu = NLUCore()
        prediction, probabilities = nlu.predict_intent(self.user_utterance)

        # Using [0] because the output we get is a numpy.ndarray
        if prediction in self.agent_intents:
            self.predicted = prediction
            self.all_intents_probability = probabilities

            self.detected_entities = nlu.extracted_entities
            self.detected_pos_dobj = nlu.extracted_pos_dobj
        else:
            self.predicted = 'Intent not found'
            self.all_intents_probability = None
            self.detected_entities = None

    def _set_conversation_tracker(self):
        """MOVE TO CONVERSATION TRACKER

            Based on the _get_intent() obtained,
            call the specific conversation tracker
            We only call this function at first text received from client
        :return:
        """
        if self.predicted in self.agent_intents:
            # Move to the specific conversation tracker detected per intent
            if self.predicted == 'greet':
                self.conversation_tracker = None
                self.next_agent_action = random.choice(dm_nlg.greet_client).format()

            if self.predicted == 'goodbye':
                self.conversation_tracker = None
                self.next_agent_action = random.choice(dm_nlg.gbye_client).format()

            if self.predicted == 'restaurant_search':
                # Prior doing the search itself, we should complete all the slots needed
                # i.e., restaurant_search needs cuisine and location slots to perform the search properly
                self.conversation_tracker = ct_restaurant()
                self.conversation_tracker.start()

            if self.predicted == 'interest_search':
                # Prior doing the search itself, we should complete all the slots needed
                # i.e., interest_search needs interest and location slots to perform the search properly
                self.conversation_tracker = ct_interest()
                self.conversation_tracker.start()

            # This is the "yes-no" case (which are agent_intents but a common answer too)
            # we probably reach this point after a CT reset (i.e saying no or yes to "any other help?")
            if self.predicted == 'no':
                # It means we are here from a reset in CT. I am not setting TC to None, 
                # we are going to exit at this point anyway
                if self.conversation_tracker is not None:
                    self.conversation_tracker = None
                    self.next_agent_action = random.choice(dm_nlg.general_fallback).format()
                else:
                    self.conversation_tracker = None
                    # Nonsenses no prediction
                    self.next_agent_action = random.choice(dm_nlg.intent_missing).format(missing=self.user_utterance)

            if self.predicted == 'yes':
                if self.conversation_tracker is not None:
                    self.conversation_tracker = None
                    self.next_agent_action = random.choice(dm_nlg.general_fallback).format()
                else:
                    self.conversation_tracker = None
                    # Nonsenses yes prediction
                    self.next_agent_action = random.choice(dm_nlg.intent_missing).format(missing=self.user_utterance)

        else:
            self.conversation_tracker = None
            # Nonsenses prediction
            self.next_agent_action = random.choice(dm_nlg.intent_missing).format(missing=self.user_utterance)
            

    def start(self, path=None):
        '''Subscribtion to topic self.conversation_tracker
           Get the current info from that topic
        '''
        # Instiantiate Speech recognition
        # self.speechrecognition = SPCore(path)
        # First talk: INTRO
        # self.speechrecognition.assistant_voice("Hello, I am a Tourist Guide Assistant. How can I help you?")
        logger.info("----------NEW CONEVERSATION STARTED----------")
        logger.info("[AGENT] Hello, I am a Tourist Guide Assistant. How can I help you?")

        while (1):

            # client_in = self.speechrecognition.get_audio()
            client_in = input("[in]: ")
            logger.info(f"[CLIENT] {client_in}")
            # We start conversation with client_in input
            self.new_utterance(client_in)
            # Special cases (goodbye, greet, no, yes, missing)

            if self.conversation_tracker is None:
                # Calling this just to refresh the random messages
                #self._set_conversation_tracker()
                agent_action = self.next_agent_action
                if self.predicted in ['goodbye', 'no']:
                    logger.info(f"[AGENT] {agent_action}")
                    # self.speechrecognition.assistant_voice(agent_action)
                    break
                logger.info(f"[AGENT] {agent_action}")
                # self.speechrecognition.assistant_voice(agent_action)    
            else:
                agent_action = self.conversation_tracker.next_agent_action
                logger.info(f"[AGENT] {agent_action}")
                # self.speechrecognition.assistant_voice(agent_action)

        logger.info("---------------------------------------------")

    def new_utterance(self, client_in):
        """
        Detects new utterance from the user, every time user inputs something goes here first to handle states
        :param client_in: Utterance of the user
        :return:
        """
        self.user_utterance = client_in
        self._get_intent()

        # Detect if conversation has been initiated
        if not self.conversation_started:
            self.initiate_conversation_tracker(client_in)

        # Keep working with the current conversation tracker
        else:
            if self.conversation_tracker.conversation_started(): # Conversation still occurring
                self.conversation_tracker.new_utterance(client_in, self.detected_entities, self.detected_pos_dobj,
                                                        self.predicted)
            else:  # Conversation has been reset
                self.initiate_conversation_tracker(client_in)

    def initiate_conversation_tracker(self, client_in):
        """
        Initializes conversation whether is the first one or it has finished for a particular conversation tracker
        :param client_in: Utterance of the user
        :return:
        """
        if self.predicted in self.agent_intents:
            self._set_conversation_tracker()
            if self.conversation_tracker is not None:
                self.conversation_started = True
                self.conversation_tracker.new_utterance(client_in, self.detected_entities, self.detected_pos_dobj,
                                                        self.predicted)
            else:
                self.conversation_started = False

    def agent_response(self, output):
        user_response = input(output)
        self.new_utterance(user_response)

    def chat(self):
        while (1):
            agent_action = self.next_agent_action
            self.agent_response(agent_action)

            if agent_action in ['goodbye', 'exit']:
                logger.info("Exiting (DMCore.chat)")
                break
            else:
                pass
        self.agent_response(f"Bye")
