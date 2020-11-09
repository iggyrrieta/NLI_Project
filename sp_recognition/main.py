
import speech_recognition as sr # importing speech recognition package from google api
import playsound # to play saved mp3 file
from gtts import gTTS # google text to speech
import subprocess # to call the `say` command


class SPCore:
    def __init__(self, path):
        self.num = 0
        self.path = path

    def assistant_voice(self, output):

        try:
            # num to rename every audio file
            # with different name to remove ambiguity
            self.num += 1
            print("Tour Guide Assistant : ", output)

            # to_speak = gTTS(text = output, lang ='en', slow = False)
            # # saving the audio file given by google text to speech
            # file = f"{self.path}/Audio_{str(self.num)}.mp3"
            # to_speak.save(file)

            # # playsound package is used to play the same file.
            # playsound.playsound(file, True)
            # return {file}

            subprocess.check_output(["say", f"{output}"])

        except Exception as e:
            print("An error occurred when agent trying to speak", e)
            print("Trying again...")
            self.assistant_voice(output)

    def get_audio(self):

        r_object = sr.Recognizer()
        audio = ''

        with sr.Microphone() as source:
            print("Speak (5sec to speak)...")

            # recording the audio using speech recognition
            audio = r_object.listen(source, phrase_time_limit = 3)

        try:

            text = r_object.recognize_google(audio, language ='en-US')
            print("You : ", text)
            return text

        except:

            self.assistant_voice("Could not understand you, say again")
            return self.get_audio()