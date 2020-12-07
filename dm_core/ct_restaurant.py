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
    ENDPOINT_URL = "https://developers.zomato.com/api/v2.1"
    PATHS = {
        "locations" : Template("$baseurl/locations?query=$place_name"), # `city_id` obtained from this endpoint is needed by other endpoints.
        "cuisines": Template("$baseurl/cuisines?city_id=$city_id"), # Lists available cuisines in a location.
        "search" : Template("$baseurl/search?entity_id=$city_id&entity_type=city&cuisines=$cuisine")
    }
    REQUEST_HEADER = {
        "Accept"    : "application/json",
        "user-key"  : "b91883b642bc6da65f15c8a1d6829288", # TODO: Remove API key before making project public. ;)
        "user-agent": "tourist_guide"
    }

    def __init__(self):
        self.c_started = False  # Check if conversation started
        self.last_input = ''

        self.city_id = None
        self.place = None
        self.available_cuisines = defaultdict(str)
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

    def _get_city_id(self, place_name):
        ''' Call Zomato API to get `city_id`.
        '''
        # Get city_id and store it.
        # Hard coding it for now.
        if self.city_id is None:
            url = ConversationTracker.PATHS["locations"].substitute(
                baseurl=ConversationTracker.ENDPOINT_URL,
                place_name=place_name)

            logger.info("Fetching city_id.")
            r = requests.get(url, headers=ConversationTracker.REQUEST_HEADER)
            logger.info("Fetched city_id.")
            content = r.json()
            content = content["location_suggestions"][0]

            try:
                self.city_id = content["city_id"]
                self.place = content["title"]
                logger.info(f"Got {self.place}({self.city_id}) on query {place_name}.")
            except Exception as e:
                logger.error("An error occurred trying to fetch city_id.", e)

        if self.city_id is not None:
            url = ConversationTracker.PATHS["cuisines"].substitute(
                baseurl=ConversationTracker.ENDPOINT_URL,
                city_id=self.city_id)

            logger.info("Fetching available cuisines.")
            r = requests.get(url, headers=ConversationTracker.REQUEST_HEADER)
            logger.info("Fetched available cuisines.")
            content = r.json()
            content = content["cuisines"]
            content = random.sample(content, min(10, len(content)))

            for c in content:
                self.available_cuisines[c["cuisine"]["cuisine_name"].lower()] = c["cuisine"]["cuisine_id"]

    def _get_nearby_restaurants(self, cuisine):
        ''' Call Zomato API to get resturants nearby with chosen cuisine.
        '''
        if self.city_id is None:
            logger.error("Error `city_id` not set.")
        else:
            url = ConversationTracker.PATHS["search"].substitute(
                baseurl=ConversationTracker.ENDPOINT_URL,
                city_id=self.city_id,
                cuisine=cuisine)

            logger.info("Fetching nearby restaurants.")
            r = requests.get(url, headers=ConversationTracker.REQUEST_HEADER)
            logger.info("Fetched nearby restaurants.")
            content = r.json()

            self.nearby_restaurant = content["restaurants"][0]


    def new_utterance(self, text, entities, pos_dobj, prediction):
        ''' Receive new text entry
        '''
        self.c_started = True
        self.last_input = text
        self.last_entity = [i.text for i in entities]

        # if self.next_agent_action_type == 'request':
        #     self._get_city_id(self.last_entity[0])
        #     self._get_nearby_resturants(self.last_entity[0])

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

        # slot not detected
        if self.next_agent_action_type == 'request':
            logger.info("Slots not detected, requesting information.")
            if self.agent_actions[0]['location'] == '':
                self.next_agent_action = restaurant_nlg.request_location
                self.next_agent_action_type = 'inform'
            # Next step, look for the other slot
            elif self.agent_actions[1]['cuisine'] == '':
                self.next_agent_action = restaurant_nlg.request_cuisine
                self.next_agent_action_type = 'inform'
            else:
                # END OF THE DEMO
                self.next_agent_action = "Bye"

        elif self.next_agent_action_type == 'inform':
            logger.info("Slots detected.")
            if self.agent_actions[0]['location'] == '':
                self.agent_actions[0]['location'] = self.last_input

                self._get_city_id(self.last_input)

                self.next_agent_action = restaurant_nlg.inform_place.format(place=self.place)
                self.next_agent_action += restaurant_nlg.inform_cuisines.format(cuisines=', '.join(
                    self.available_cuisines.keys()))
                self.next_agent_action += restaurant_nlg.request_cuisine
                self.next_agent_action_type = 'inform'
            # Next step, look for the other slot
            elif self.agent_actions[1]['cuisine'] == '':
                self.agent_actions[1]['cuisine'] = self.last_input

                if self.last_input.lower() not in self.available_cuisines.keys():
                    logger.info(f"Cuisine {self.last_input.lower()} not in {', '.join(self.available_cuisines.keys())}")
                    self.next_agent_action = restaurant_nlg.unavailable_cuisine
                    self.next_agent_action_type = "inform"
                else:
                    logger.info("Finding nearby restaurants.")
                    self._get_nearby_restaurants(self.available_cuisines[self.last_input.lower()])
                    name = self.nearby_restaurant["restaurant"]["name"]
                    place = self.nearby_restaurant["restaurant"]["location"]["address"]
                    timings = self.nearby_restaurant["restaurant"]["timings"]

                    self.next_agent_action = restaurant_nlg.inform_restaurant.format(
                                                name=name,
                                                place=place,
                                                timings=timings)
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