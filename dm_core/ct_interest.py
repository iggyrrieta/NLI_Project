import os
import sys
import requests
import json
import wikipedia

# ROOT FOLDER : Make things easier setting the root folder as the origin
root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.insert(0, root_path)
# Utils
import dm_core.utils as utils

class ConversationTracker:
    """Tracking of conversations."""

    def __init__(self):
        self.c_started = False  # Check if conversation started
        self.last_input = ''    # Last text from the client
        self.gmaps_info = None  # Info obtained from google maps
        self.wiki_info = None   # Info obtained from wikipedia
        self.info = None        # info variable, which contains all CT data
        self._id = 0            # self.info idenfitier

        # Agent, based on inform/request/action methodology
        self.agent_slots = ['art', 'music', 'sport', 'culture']
        self.agent_inform = self.agent_slots 
        self.agent_request = self.agent_slots 
        self.agent_actions = []   # All the actions of the agent

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
        self.history = []

    def _gmaps_info(self, text):
        ''' GMAPS API connection.
        '''
        self.gmaps_info = utils.gmaps_info(text)

    def _wiki_info(self, text):
        ''' WIKIPEDIA API connection.
        '''
        self.wiki_info  = utils.del_stopwords(wikipedia.summary(text))
        
        
    def new_utterance(self, text, entity):
        ''' Receive new text entry
        '''     
        self.c_started = True
        self.last_input = text
        # Get gmaps API results
        self._gmaps_info(text)
        # Get wikipedia API results
        self._wiki_info(text)
        
        # TODO combine both wiki and gmaps info in 1 structure
        
        # Utterance id
        self._id += 1 
        # Add to history
        self.history.append(f"{self._id} - {self.last_input}")
        # Go analyze this text
        self.publish(self.info, entity)

    def publish(self, text, ent):
        '''Publish all processed info
           to be used by dm subscribe
        '''
        # TODO I HAVE NO IDEA HOW TO EXTRACT THE INFO I WANT, I AM NOT GETTING 
        # ANY ENTITY WHEN TESTING!!!

        #If I receive entities then we can do samething similar implemented as a test in dm
        pass


    def print_history(self):
        ''' Print current history
        '''
        for text in self.history:
            print(text)
    
    def reset(self):
        ''' Remove conversation
        '''
        self.history = []
        self.c_started = False
        self.last_input = ''
        self.gmaps_info = None
        self.wiki_info = None
        self.info = None
        self._id = 0