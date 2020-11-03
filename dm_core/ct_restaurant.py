class ConversationTracker:
    """Tracking of conversations."""

    def __init__(self):
        self.c_started = False  # Check if conversation started
        self.last_input = ''

    def __repr__(self):
        return 'RESTAURANT_SEARCH (ct_restaurant.ConversationTracker)'

    def start(self):
        ''' Start conversation tracker
        '''
        self.history = []

    def _db_conn(self):
        ''' API connection.
        '''

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