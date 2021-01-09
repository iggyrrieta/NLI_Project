# =======================================================================
# A bunch of useful functions than can be used in multiple scripts
# =======================================================================
import re
import json
import requests


def del_stopwords(text):
    ''' Delete stopwords from a given text
    '''
    with open('../data/stopwords.txt', 'r') as file:
        stopwords = [line.rstrip('\n') for line in file]

    word_tokens = text.split()
    filtered_sentence = []

    for w in word_tokens:
        if w not in stopwords:
            filtered_sentence.append(w)

    return filtered_sentence


def only_alpha(self, text):
    ''' Delete special characters
    '''
    text = re.sub(r'[^A-Za-zÑñ]', ' ', text)

    return text


def gmaps_info(text):
    ''' GMAPS API connection.
    '''
    try:
        # Access to API using key
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
        inputtype = "textquery"
        fields = "formatted_address,name,rating,opening_hours"
        # TODO REMOVED THIS KEY
        api_key = '-----------------------'

        # Get info 
        info = requests.get(f"{url}input={text}&inputtype={inputtype}&fields={fields}&key={api_key}").json()

        gmaps_info = {'text': text, 'options': info['candidates']}

    except Exception as e:
        print("An error occurred using google maps API", e)
        gmaps_info = {'text': text, 'options': ''}

    # gmaps_info = {'text': text,
    # 'address': info['candidates'][0]['formatted_address'] if info['status']=='OK' else 'Not found',
    # 'name': info['candidates'][0]['name'] if info['status']=='OK' else 'Not found',
    # 'rating': info['candidates'][0]['rating'] if info['status']=='OK' else 'Not found',
    # 'opening_hours': info['candidates'][0]['opening_hours'] if info['status']=='OK' and 'opening_hours' in info['candidates'][0].keys() else 'Not found'}

    return gmaps_info
