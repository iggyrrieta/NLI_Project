import requests
import random
from string import Template
from collections import defaultdict
from nlg_core.main import restaurant_nlg
import os
import logging

#==============================================================================
#   LOGGER
#
# This is the ct_restaurant logger
#==============================================================================
root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
logging.config.fileConfig(f"{root_folder}/data/log.ini")
logger = logging.getLogger('ct_restaurant_logger')
#==============================================================================


class ConversationTracker:
    """Tracking of conversations."""

    # Couple of convenience class variables.
    # Add your key here
    API_KEY = "-----------------"
    ENDPOINT_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext"
    FIELDS = "formatted_address,name,opening_hours,rating"
    PATHS = {
        "search" : Template(f"$baseurl/json?input=$input&key={API_KEY}&language=en&fields={FIELDS}&inputtype=textquery")
    }

    def __init__(self):
        self.c_started = False  # Check if conversation started
        self.last_input = ''

        self.city_id = None
        self.place = None
        self.cuisine = None
        self.nearby_restaurant = None

        self._id = 0  # self.info identifier
        self.info = None

        # Agent, based on inform/request/action methodology
        self.agent_slots = ['location', 'cuisine']
        self.agent_inform = self.agent_slots
        self.agent_request = self.agent_slots
        self.agent_actions = []  # All the actions of the agent
        self.previous_agent_action = None  # Defines previous action to be performed by the agent, action
        self.next_agent_action = None  # Defines next action to be performed by the agent, action
        self.next_agent_action_type = 'request'  # Defines what type of action is performing the agent

        # Initialize the required slots
        for slot in self.agent_request:
            self.agent_actions.append({slot: ''})

    def __repr__(self):
        return 'RESTAURANT_SEARCH (ct_restaurant.ConversationTracker)'

    def start(self):
        ''' Start conversation tracker
        '''
        logger.info("----------NEW CT_RESTAURANT TRACK STARTED----------")

    def _get_nearby_restaurants(self, search_term):
        ''' Call GMaps API to get resturants nearby with chosen cuisine.
        '''
        url = ConversationTracker.PATHS["search"].substitute(
            baseurl=ConversationTracker.ENDPOINT_URL,
            input=search_term)

        logger.info("Fetching nearby restaurants.")
        logger.info(f"Search query is: {search_term}")
        r = requests.get(url)
        logger.info("Fetched nearby restaurants.")
        content = r.json()

        logger.info(f"JSON response: {content}")

        self.nearby_restaurant = content["candidates"][0]


    def new_utterance(self, text, entities, pos_dobj, prediction):
        ''' Receive new text entry
        '''
        self.c_started = True
        self.last_input = text
        self.last_entity = [i.text for i in entities]

        # Fill cuisine slot
        t_ent = entities
        found_cuisine = False
        found_location = False

        for e in t_ent:
            logger.info(f"Entity {e.text} has label {e.label_}")
            if e.label_ == 'GPE' or e.label_ == 'LOC':
                self.agent_actions[0]['location'] = e.text
                found_location = True

            if e.label_ == 'PRODUCT' or e.label_ == 'NORP':
                self.agent_actions[1]['cuisine'] = e.text.lower()
                found_cuisine = True

            if found_location and found_cuisine:
                self.next_agent_action_type = 'inform'
                break

        logger.info(f"Slots: {self.agent_actions}")

        # Increment utterance id.
        self._id += 1
        # Append to log
        logger.info(f"{self._id} - {self.last_input}")
        # Analyze text.
        self.publish(self.info, entities)

    def publish(self, text, ent):
        '''Publish all processed info
           to be used by dm subscribe
        '''

        # Slots not detected
        if self.next_agent_action_type == 'request':
            logger.info("Slots not detected, requesting information.")

            # Check for location.
            if self.agent_actions[0]['location'] == '':
                self.next_agent_action = restaurant_nlg.request_location

                # See if cuisine is missing.
                if self.agent_actions[1]['cuisine'] == '':
                    self.next_agent_action_type = 'request'
                else:
                    self.next_agent_action_type = 'inform'

            # Check for cusine.
            elif self.agent_actions[1]['cuisine'] == '':
                self.next_agent_action = restaurant_nlg.request_cuisine

                # See if location is missing.
                if self.agent_actions[0]['location'] == '':
                    self.next_agent_action_type = 'request'
                else:
                    self.next_agent_action_type = 'inform'

            # Abort mission!
            else:
                self.next_agent_action = restaurant_nlg.finish
                self.reset()

        elif self.next_agent_action_type == 'inform':
            logger.info("All slots detected.")

            self.place = self.agent_actions[0]['location']
            self.cuisine = self.agent_actions[1]['cuisine']

            query = f"{self.cuisine} restaurants near {self.place}"
            logger.info(f"Finding nearby restaurants. Search term: {query}")
            self._get_nearby_restaurants(query)

            name = self.nearby_restaurant["name"]
            place = self.nearby_restaurant["formatted_address"]

            if self.nearby_restaurant["opening_hours"]["open_now"]:
                open = "open"
            else:
                open = "closed"

            self.next_agent_action = restaurant_nlg.inform_restaurant.format(
                                        name=name,
                                        place=place,
                                        open=open)
            self.next_agent_action_type = 'request'

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
        ''' Remove conversation
        '''
        self.history = []
        self.c_started = False
        self.last_input = ''

        for slot in self.agent_request:
            self.agent_actions.append({slot: ''})
