# NLG
class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])

    Ref: https://stackoverflow.com/a/32107024/4626943
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


#############################
#     DIALOGUE MANAGER
#############################
dm_nlg = Map()

# IDEA: This random thing can also be a dictionay with level of happiness 
# detected using sentiment analysis. We probably don't have time but we can
# say this on the presentation

# intent = greet
dm_nlg.greet_client  = ['Hello!, How can I help you?',
             'Hey there!, I am here to help you. What are you looking for?',
             'Today is a perfect day to discover new places, what you have in mind?']

# intent = goodbye
dm_nlg.gbye_client  = ['Bye :(, come back soon!',
        'Ciao! Have a nice day!',
        'Adieu! ;)',
        'Auf Wiedersehen']

# intent = yes|no when there is not CT active
dm_nlg.general_fallback = ['Ok, I can tell you places to have fun or where to visit and eat',
                  "Cool! Let's start over :) tell what you would like to do?",
                  'So, would you like to know something else?']

# intent = missing
dm_nlg.intent_missing  = ["404! can you repeat please...sorry. Did not get what you mean when you say '{missing}'",
           'mmm... I did not get what you mean by "{missing}"',
           '"{missing}"?, what you mean?']

#############################
#     RESTAURANT CT
#############################
restaurant_nlg = Map()

restaurant_nlg.request_location = "Okay, what location do you want me to search a restaurant in?"
restaurant_nlg.request_cuisine = "What cuisine do you want to try?"

restaurant_nlg.inform_place = "Okay great, so I shall look for restaurants around {place}. "
restaurant_nlg.inform_restaurant = "You may visit {name}, it is located at {place}. It is now {open}."

restaurant_nlg.unavailable_cuisine = "Please, select one of the available cuisines :)"
restaurant_nlg.finish = "Is there anything else I can help you with?"

#############################
#     INTEREST CT
#############################
interest_nlg = Map()

interest_nlg.request_time = "Sure thing! I need some extra information, when do you want to visit {place}?"
interest_nlg.request_more_info = "Do you want me to give you some information about {place}?"
interest_nlg.inform_options = "I found {number_opt} place(s). The closest one is {opt_name}, located at {opt_address}"

interest_nlg.negative_response = "Oh, no problem then. Is there anything else I can help you with?"
interest_nlg.interest_not_found = f"Ok, this is embarrassing. I could not find any places related to what " \
                                         f"you are looking for. Can you re-phrase it for me? "

interest_nlg.tell_me_more = "Ok so ... {text}"
