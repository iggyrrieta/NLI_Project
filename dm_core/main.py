import os
import sys
import pandas as pd

# ROOT FOLDER : Make things easier setting the root folder as the origin
# root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
# sys.path.insert(0, root_path)

# SP
from sp_recognition.main import SPCore
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
        self.agent_actions = []  # All the actions of the agent
        self.detected_entities = None
        self.detected_pos_dobj = None

        # Access to database
        self.root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        self.db_path = f'{self.root_path}/NLI_Project/data/{db_name}'

        # Read db file
        print(self.db_path)
        data = pd.read_csv(self.db_path, delimiter=',')
        self.agent_intents = ['greet', 'goodbye', 'restaurant_search', 'interest_search', 'yes', 'no']

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
                self.next_agent_action = 'Hi there!'

            if self.predicted == 'goodbye':
                self.conversation_tracker = None
                self.next_agent_action = 'Bye :(, come back soon!'

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
        else:
            self.conversation_tracker = None

    def start(self, path):
        '''Subscribtion to topic self.conversation_tracker
           Get the current info from that topic
        '''
        # Instiantiate Speech recognition
        # self.speechrecognition = SPCore(path)
        # First talk: INTRO
        # self.speechrecognition.assistant_voice("Hello, I am a Tourist Guide Assistant. How can I help you?")
        print("Hello, I am a Tourist Guide Assistant. How can I help you?")

        while (1):

            # client_in = self.speechrecognition.get_audio()
            client_in = input()
            # We start conversation with client_in input
            self.new_utterance(client_in)
            agent_action = self.conversation_tracker.next_agent_action

            if agent_action in ['Bye', 'goodbye', 'exit']:
                break
            else:
                # self.speechrecognition.assistant_voice(agent_action)
                print(agent_action)

        # self.speechrecognition.assistant_voice("Bye")
        print("Bye")

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
