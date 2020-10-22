##########################################################################
#INFO: This a proposed class, totally hardcoded now. Using old movie 
#      assistant example
##########################################################################

import speech_recognition as sr # importing speech recognition package from google api 
import playsound # to play saved mp3 file 
from gtts import gTTS # google text to speech 
import os # to save/open files 
import requests # to get API responses
import json # to get detailed info from API responses

#TODO: These scripts are empty
import processing_layer
import semantic_layer

class Dmanager:
    def __init__(self, path):
        self.name = "Human"
        self.topic = ""
        self.num = 0
        self.path = path

    def start(self):

        self.assistant_voice("Hello, I am a movie assistant. What's your name?") 
        self.name = self.get_audio()
        self.assistant_voice(f"Hello, {self.name}") 

        #Start chat
        self.chat()

    def chat(self):
        
        while(1): 
            ##########################################################################
            #TODO: The first question should be a random pick from a bagOfwords file
            ##########################################################################
            self.assistant_voice("What movie do you want to check?") 
            text = self.get_audio()
    
            if text == 0: 
                continue
            ##########################################################################
            #TODO: The following is just a test, this should be inside processing
            #      layer script. Now it is hardcoded.
            ##########################################################################
            if "exit" in str(text) or "bye" in str(text) or "sleep" in str(text): 
                self.assistant_voice("Ok bye, "+ self.name+'.') 
                break
            else:
                # Go to omdbapi to check movie (we can take info from here to talk about a movie)
                apikey = 'efcac389' #iñaki api key
                response = requests.get(f"http://www.omdbapi.com/?t={text}&apikey={apikey}")

                if (response.status_code == 200):
                    #Find value -> "Ratings":[{"Source":"Internet Movie Database","Value":"8.8/10"},...]
                    details_movie = json.loads(response.text)
                    rating = float(details_movie['Ratings'][0]['Value'].split("/")[0])
                    if (rating < 5.):   
                        self.assistant_voice(f"This movie only gets a {rating}, I don't think you like it...") 
                        text = get_audio()
                    elif (rating > 5.) and (rating < 8.):
                        self.assistant_voice(f"This movie only gets a {rating}, not bad at all...") 
                        text = get_audio()
                    else:
                        self.assistant_voice(f"OH! This movie gets a {rating}, you should watch it...") 
                        break
                else:
                    self.assistant_voice("Sorry I can't find this movie") 
                    break
        self.assistant_voice(f"Bye")

    def assistant_voice(self, output): 
    
        # num to rename every audio file  
        # with different name to remove ambiguity 
        self.num += 1
        print("Movie Assistant : ", output) 
    
        toSpeak = gTTS(text = output, lang ='en', slow = False) 
        # saving the audio file given by google text to speech 
        file = f"{self.path}/Audio_{str(self.num)}.mp3"  
        toSpeak.save(file) 
        
        # playsound package is used to play the same file. 
        playsound.playsound(file, True)  
        return {file}
        
    def get_audio(self): 
    
        rObject = sr.Recognizer() 
        audio = '' 
    
        with sr.Microphone() as source: 
            print("Speak (5sec to speak)...") 
            
            # recording the audio using speech recognition 
            audio = rObject.listen(source, phrase_time_limit = 3)
    
        try: 
    
            text = rObject.recognize_google(audio, language ='en-US') 
            print("You : ", text) 
            return text 
    
        except: 
    
            self.assistant_voice("Could not understand you, say again") 
            return self.get_audio()   