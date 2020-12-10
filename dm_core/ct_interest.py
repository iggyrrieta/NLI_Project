import wikipedia
import re

# ROOT FOLDER : Make things easier setting the root folder as the origin
# root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
# sys.path.insert(0, root_path)

# Utils
import dm_core.utils as utils
from nlg_core.main import interest_nlg
import os
import logging

#==============================================================================
#   LOGGER
#
# This is the ct_interest logger
#==============================================================================
root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
logging.config.fileConfig(f"{root_folder}/data/log.ini")
logger = logging.getLogger('ct_interest_logger')
#==============================================================================


class ConversationTracker:
    """Tracking of conversations."""

    def __init__(self):
        self.c_started = False  # Check if conversation started
        self.last_input = ''  # Last text from the client
        self.last_entity = ''
        self.request_out = ''
        self.gmaps_info = None  # Info obtained from google maps
        self.wiki_info = None  # Info obtained from wikipedia
        self.info = None  # info variable, which contains all CT data
        self._id = 0  # self.info identifier

        # Agent, based on inform/request/action methodology
        self.agent_slots = ['info', 'place', 'type']
        self.agent_inform = self.agent_slots
        self.agent_request = self.agent_slots
        self.agent_actions = []  # All the actions of the agent
        self.previous_agent_action = None  # Defines previous action to be performed by the agent, action
        self.next_agent_action = None  # Defines next action to be performed by the agent, action
        self.next_agent_action_type = 'inform'  # Defines what type of action is performing the agent

        # Initialize the required slots
        for slot in self.agent_request:
            self.agent_actions.append({slot: ''})

    def __repr__(self):
        return '\n'.join([
            'INTEREST_SEARCH (ct_interest.ConversationTracker)',
            '----------------',
            f'AGENT SLOTS FOR INTENT: {self.agent_slots}',
            f'AGENT ACTIONS FOR INTENT: {self.agent_actions}',
            f'CONVERSATION LENGTH: {self._id} UTTERANCES RECEIVED'
        ])

    def start(self):
        ''' Start conversation tracker
        '''
        logger.info("----------NEW CT_INTEREST TRACK STARTED----------")

    def _gmaps_info(self, text):
        ''' GMAPS API connection.
        '''
        self.gmaps_info = utils.gmaps_info(text)

    def _wiki_info(self, text):
        ''' WIKIPEDIA API connection.
        '''

        # Remove parenthesis info from Wikipedia summary as it always include original language pronunciation
        wiki_aux = wikipedia.summary(text, sentences=2)
        start = wiki_aux.find('(')
        end = wiki_aux.find(')')

        self.wiki_info = wiki_aux.replace(wiki_aux[start:end + 1], '')

    def new_utterance(self, text, entities, pos_dobj, prediction):
        ''' Receive new text entry
        '''
        self.c_started = True
        self.last_input = text
        self.last_entity = [i.text for i in entities] if entities else [p for p in
                                                                        pos_dobj]  # TODO: change to return full token to analyze the type here

        if prediction not in ['yes', 'no']:
            if self.next_agent_action_type == 'inform' and len(self.last_entity) > 0:
                # Get gmaps API results
                self._gmaps_info(self.last_entity[0])
                # Get wikipedia API results
                self._wiki_info(self.last_entity[0])
            else:
                pass  # TODO: raise warning of not detected entity, handle not detected entity as new request to user

        # Utterance id
        self._id += 1
        # Add log
        logger.info(f"{self._id} - {self.last_input}")
        # Go analyze this text
        self.publish(self.info, entities, prediction)

    def publish(self, text, ent, prediction):
        """
        Publish all processed info to be used by DM subscribe
        :param text:
        :param ent:
        :param prediction:
        :return:
        """
        if self.next_agent_action_type == 'request':
            if prediction != 'no':
                if self.agent_actions[1]['place'] != '':
                    self.next_agent_action = interest_nlg.request_more_info.format(place=self.agent_actions[2]['type'])
                    self.next_agent_action_type = 'inform'
            else:
                self.next_agent_action = interest_nlg.negative_response.format()
                self.reset()

        elif self.next_agent_action_type == 'inform':
            # Next step, look for the other slot
            if self.agent_actions[1]['place'] == '':
                options = self.gmaps_info['options']

                if len(options) > 0:
                    self.next_agent_action = interest_nlg.inform_options.format(number_opt=len(options),
                                                                         opt_name=options[0]['name'],
                                                                         opt_address=options[0]['formatted_address'])
                    self.agent_actions[1]['place'] = options[0]['name']
                    self.agent_actions[2]['type'] = self.last_entity[0]
                    self.next_agent_action_type = 'request'
                else:
                    self.next_agent_action = interest_nlg.interest_not_found.format()
                    self.next_agent_action_type = 'inform'

            # Next step, look for the other slot
            elif self.agent_actions[0]['info'] == '':
                if prediction == 'no':
                    self.next_agent_action = interest_nlg.negative_response.format()
                    self.reset()
                else:
                    self.agent_actions[0]['info'] = self.last_input
                    self.next_agent_action = interest_nlg.tell_me_more.format(text=self.wiki_info)
                    self.next_agent_action_type = 'request'
                    self.agent_actions[1]['info'] = self.wiki_info

    def get_history(self):
        """
        Connection to log file to check previous iterations
        """
        #TODO: Add connection to log, to check previous iterations
        # This can be used to easily check all iterations. It is as it was
        # before but now we got all organized and saved locally

    def conversation_started(self):
        """
        Get whether if CT has started or reset
        :return:
        """
        return self.c_started

    def reset(self):
        """
        Reset conversation
        :return:
        """
        self.c_started = False
        self.last_input = ''
        self.last_entity = ''
        self.request_out = ''
        self.gmaps_info = None
        self.wiki_info = None
        self.info = None
        self._id = 0
