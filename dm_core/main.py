import os
import pandas as pd

# ROOT FOLDER : Make things easier setting the root folder as the origin
import sys

root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.insert(0, root_path)
# NLU
from nlu_core.main import NLUCore
# Conversation trackers
from dm_core.ct_interest import ConversationTracker as ct_interest
from dm_core.ct_restaurant import ConversationTracker as ct_restaurant


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
        self.agent_actions = []   # All the actions of the agent
        self.detected_entities = None

        # Access to database
        self.root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        self.db_path = f'{self.root_path}/NLI_Project/data/{db_name}'

        # Read db file
        data = pd.read_csv(self.db_path, delimiter=',')
        self.agent_intents =['greet', 'goodbye', 'restaurant_search', 'interest_search']

        # --- This code should be moved to the corresponding Conversational Tracker ---
        # Logic is really similar for every CT we use, detect missing slots and manage actions to ask them to the user
        # Doing it here for integration purposes and to have a better idea of the loop

        self.agent_inform_slots_restaurant = ['cuisine', 'location']
        self.agent_request_slots_restaurant = ['cuisine', 'location']

        # Initialize the required slots for restaurant_search intent
        for slot in self.agent_request_slots_restaurant:
            self.agent_actions.append({slot: ''})

        # ----------------------------------------------------------------------------

    def __repr__(self):
        return '\n'.join([
            'DIALOGUE MANAGER',
            '----------------',
            f'STARTED: {self.conversation_started}',
            f'LAST_TEXT: {self.user_utterance}',
            f'AGENT INTENTS: {self.agent_intents}',
            f'AGENT SLOTS FOR INTENT: {self.agent_slots}',
            f'INTENT: {self.predicted}',
            f'TRACKER: {self.conversation_tracker}',
            '----------------'
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
        else:
            self.predicted = 'Intent not found'
            self.all_intents_probability = None

    def _get_conversation_tracker(self):
        ''' MOVE TO CONVERSATION TRACKER
            Based on the _get_intent() obtained,
            call the specific conversation tracker
            We only call this function at first text received from client
        '''
        if self.predicted in self.agent_intents:
            # Move to the specific conversation tracker detected per intent
            if self.predicted == 'greet':
                self.conversation_tracker = None  # provisional
                self.next_agent_action = 'Hi there!'

            if self.predicted == 'goodbye':
                self.conversation_tracker = None  # provisional
                self.next_agent_action = 'Bye :(, come back soon!'

            if self.predicted == 'restaurant_search':
                # Prior doing the search itself, we should complete all the slots needed
                # i.e., restaurant_search needs cuisine and location slots to perform the search

                # --- All this should be done inside the specific conversational tracker ---
                # self.conversation_tracker = ct_restaurant()

                # Check if all the required slots are completed
                for ent in self.detected_entities:
                    if ent.label_ == 'NORP':
                       self.agent_actions[0]['cuisine'] = ent.text

                # Cuisine slot not detected
                self.next_agent_action_type = 'request'
                if self.agent_actions[0]['cuisine'] == '':
                    self.next_agent_action = 'Sure thing! I need some extra information, what type of cuisine are you looking for?'
                # Next step, look for the location slot
                elif self.agent_actions[0]['location'] == '':
                    self.next_agent_action = 'Are you looking for a particular location?'
                # All slots completed, moving to API search
                else:
                    self.next_agent_action_type = 'inform'
                    pass
                    # Perform API search with all the data
                # ------------------------------------------------------------------------
            if self.predicted == 'interest_search':
                # Prior doing the search itself, we should complete all the slots needed
                # i.e., interest_search needs interest and location slots to perform the search properly
                self.conversation_tracker = ct_interest()
        else:
            self.conversation_tracker = None

    def new_utterance(self, client_in):
        self.user_utterance = client_in

        # First entry
        if not self.conversation_started:
            # Get intent. This verifications process does the following:
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
            if self.predicted in self.agent_intents:

                # Get conversation tracker
                self._get_conversation_tracker()
                if self.conversation_tracker is not None:
                    self.conversation_started = True
                    #self.conversation_tracker.new_utterance(client_in)

        # All other entries
        else:
            # Directly pointing the current conversation tracker (ct)
            self.conversation_tracker.new_utterance(client_in)

    def start(self):
        self.agent_response("Hello, I am your assistant. How can I help you?")

        # Start chat
        self.chat()

    def agent_response(self, output):
        user_response = input(output)
        self.new_utterance(user_response)

    def chat(self):

        while (1):

            agent_action = self.next_agent_action
            self.agent_response(agent_action)

            if agent_action in ['goodbye', 'exit']:
                break
            else:
                pass
        self.agent_response(f"Bye")
