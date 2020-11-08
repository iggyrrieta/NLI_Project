import os
import sys
import requests
import json
import wikipedia

# ROOT FOLDER : Make things easier setting the root folder as the origin
#root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
#sys.path.insert(0, root_path)

# Utils
import dm_core.utils as utils

class ConversationTracker:
    """Tracking of conversations."""

    def __init__(self):
        self.c_started = False  # Check if conversation started
        self.last_input = ''    # Last text from the client
        self.last_entity = ''
        self.request_out = ''
        self.gmaps_info = None  # Info obtained from google maps
        self.wiki_info = None   # Info obtained from wikipedia
        self.info = None        # info variable, which contains all CT data
        self._id = 0            # self.info idenfitier

        # Agent, based on inform/request/action methodology
        self.agent_slots = ['date', 'info']
        self.agent_inform = self.agent_slots 
        self.agent_request = self.agent_slots 
        self.agent_actions = []   # All the actions of the agent
        self.previous_agent_action = None  # Defines previous action to be performed by the agent, action
        self.next_agent_action = None  # Defines next action to be performed by the agent, action
        self.next_agent_action_type = 'request'  # Defines what type of action is performing the agent

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
        #self.wiki_info  = utils.del_stopwords(wikipedia.summary(text))
        self.wiki_info  = wikipedia.summary(text)
        
    def new_utterance(self, text, entity):
        ''' Receive new text entry
        '''     
        self.c_started = True
        self.last_input = text
        self.last_entity = [i.text for i in entity]

        if self.next_agent_action_type == 'request':
            # Get gmaps API results
            self._gmaps_info(self.last_entity[0])
            # Get wikipedia API results
            self._wiki_info(self.last_entity[0])

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
        #for ent in self.last_entity:
        #    if ent[0] == 'something related to date time in spacy': # TODO CHANGE THIS
        #        self.agent_actions[0]['date'] = ''
        
        # slot not detected
        if self.next_agent_action_type == 'request':
            if self.agent_actions[0]['date'] == '':
                self.next_agent_action = f"Sure thing! I need some extra information, when do you want to visit {self.gmaps_info['name']}?"
                self.next_agent_action_type = 'inform'
            # Next step, look for the other slot
            elif self.agent_actions[1]['info'] == '':
                self.next_agent_action = f"Do you want me to explain you some info from {self.gmaps_info['name']}?"
                self.next_agent_action_type = 'inform'
            else:
                # END OF THE DEMO
                self.next_agent_action = "Bye"

        elif self.next_agent_action_type == 'inform': 
            if self.agent_actions[0]['date'] == '':
                self.agent_actions[0]['date'] = self.last_input
                self.next_agent_action = f"{self.gmaps_info['name']} is now {self.gmaps_info['opening_hours']}"
                self.next_agent_action_type = 'request'
            # Next step, look for the other slot
            elif self.agent_actions[1]['info'] == '':
                self.agent_actions[1]['info'] = self.last_input
                self.next_agent_action = f'Ok so.. {self.wiki_info}'
                self.next_agent_action_type = 'request'
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
        self.last_entity = ''
        self.request_out = ''
        self.gmaps_info = None
        self.wiki_info = None
        self.info = None
        self._id = 0