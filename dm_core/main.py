import os
import pandas as pd

# ROOT FOLDER : Make things easier setting the root folder as the origin
import sys
root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.insert(0, root_path)
# NLU
from nlu_core.main import Core as nlu_core
# Conversation trackers
from dm_core.ct_interest import ConversationTracker as ct_interest
from dm_core.ct_restaurant import ConversationTracker as ct_restaurant

class Core:
    """Agent that interacts with the user.
       - sr_core -> dm_core <-> nlu_core
                            <-> ct_{intent}
                             -> nlg_core
    """

    def __init__(self, db_name='data.csv'):
        
        # Init. Reset all when instantiate
        self.client_in = '' # Just the client conversation input (text), received from speech recognition module
        self.c_pred = ''    # Conversation prediction, based on that we'll move to one ct or another
        self.c_prob = None
        self.ct = None      # Conversation tracker (ct) selected
        self.c_started = False # Check if conversation started

        # Access to database
        self.root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        self.db_path = f'{self.root_path}/data/{db_name}'
        
        # Read db file
        data = pd.read_csv(self.db_path, delimiter=',')
        self.agent_slots = set(data['intent'])

    def __repr__(self):
        return '\n'.join([
            'DIALOGUE MANAGER',
            '----------------',
            f'STARTED: {self.c_started}',
            f'LAST_TEXT: {self.client_in}',
            f'AGENT SLOTS: {self.agent_slots}',
            f'INTENT: {self.c_pred}',
            f'TRACKER: {self.ct}',
            '----------------'
            ])
         
    def _get_intent(self):
        ''' GET INTENT FROM NLU_CORE
            Call -> nlu_core
            Get  -> prediction and probabilities from an input text
        '''
        nlu = nlu_core()
        prediction, probabilities = nlu.predict_intent(self.client_in)

        # Using [0] because the output we get is a numpy.ndarray
        if prediction[0] in self.agent_slots:  
            self.c_pred = prediction[0]
            self.c_prob = probabilities[0]
        else:
            self.c_pred = 'Intent not found'
            self.c_prob = None


    def _get_ct(self):
        ''' MOVE TO CONVERSATION TRACKER
            Based on the _get_intent() obtained,
            call the specific conversation tracker
            We only call this function at first text received from client
        '''      
        if self.c_pred in self.agent_slots:
            # Move to conversation tracker of that specific intent
            # TODO: It is a bit hardcoded now, modify it in future
            if self.c_pred == 'greet':
                #TODO: I don't know what we should do here. Probably create a bagOfGreets.txt
                #      and randomly pick one of those. They must be very generic...
                #      Probably we should get a good response based on the specific question
                self.ct = None # provisional

            if self.c_pred == 'goodbye':
                #TODO: I don't know what we should do here. Probably create a bagOfGoodbyes.txt
                #      and randomly pick one of those. They must be very generic...
                #      Probably we should get a good response based on the specific question
                self.ct = None # provisional

            if self.c_pred == 'restaurant_search':
                self.ct = ct_restaurant()
            if self.c_pred == 'interest_search':
                self.ct = ct_interest()

            # Start tracker
            self.ct.start()

        else:
            self.ct = None


    def new_entry(self, client_in):

        self.client_in = client_in

        # First entry
        if not self.c_started:
            #Get intent. This verifications process does the following:
            #  - Call function '_get_intent()' which is supposed to be called
            #    in order to get the intent of the conversation.
            #  - In case the intent doesn't exist we don't set the conversation 
            #    to True and we wait to get another input to check if we can
            #    get a good intent. 
            #  - In case the intent exists then we call the function '_get_ct'
            #    that check the intent and calls the correct conversation tracker.
            #    In case the intent is a 'greet' or 'goodbye' it just doesn't set 'self.ct'
            #    If 'self.ct' is not set then conversation doesn't start and next input text
            #    will be check follwing same process.
            self._get_intent()
            if self.c_pred in self.agent_slots: 
                #Get conversation tracker
                self._get_ct()
                if self.ct is not None:
                    self.c_started = True
                    self.ct.new_entry(client_in)

        # All other entries
        else:
            # Directly pointing the current conversation tracker (ct)
            self.ct.new_entry(client_in)