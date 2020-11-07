import json
import requests
from string import Template


class ConversationTracker:
    """Tracking of conversations."""

    # Store API Key as a Class variable.
    # TODO: Remove API key before making project public. ;)
    ZOMATO_API_KEY = "b91883b642bc6da65f15c8a1d6829288"
    ENDPOINT_URL = "https://developers.zomato.com/api/v2.1/"
    PATHS = {
        "cities" : Template("$baseurl/cities?q=$place_name"), # `city_id` obtained from this endpoint is needed by other endpoints.
        "cuisines": Template("$baseurl/cuisines?city_id=$city_id"), # Lists available cuisines in a location.
        "search" : Template("$baseurl/search?entity_id=city_id&q=$query_term")
    }
    REQUEST_HEADER = {
        "Accept" : "application/json",
        "user-key" : "b91883b642bc6da65f15c8a1d6829288"
    }

    def __init__(self):
        self.c_started = False  # Check if conversation started
        self.last_input = ''
        self.place_id = None

    def __repr__(self):
        return 'RESTAURANT_SEARCH (ct_restaurant.ConversationTracker)'

    def start(self):
        ''' Start conversation tracker
        '''
        self.history = []

    def _db_conn(self):
        ''' API connection.
        '''
        # Get place_id and store it.
        # Hard coding it for now.
        if self.place_id is None:
            url = PATHS["cities"].substitute(
                baseurl=ConversationTracker.ENDPOINT_URL,
                place_name="Kolkata")

            r = requests.get(url, ConversationTracker.REQUEST_HEADER)
            content = r.json()
            try:
                self.place_id = content[0]["id"]
            except Exception as e:
                print("An error occurred trying to fetch place_id.", e)


    def new_entry(self, text):
        ''' Receive new text entry
        '''
        self.c_started = True
        self.last_input = text
        self.history.append(text)
        # Go analyze this text
        self._analyze(self.last_input)

    def _analyze(self, text):
        # TODO: We should do some analysis or decide how to proceed

        # Get most recent input from user.
        statement = self.history[-1]

        # TODO: This needs to moved elsewhere.
        self._db_conn()

        return 0

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