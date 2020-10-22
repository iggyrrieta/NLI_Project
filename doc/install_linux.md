# Linux (debian) requirements

In case you are working in a virtual environment:

```bash
pip install SpeechRecognition # importing speech recognition package from google api 
pip install playsound # to play saved mp3 file
pip install gTTS # google text to speech 
pip install requests # to get API responses
```

Now, the folLowing can only be installed as an administrator:

```bash
sudo apt install python-gobject # to play saved mp3 file
sudo apt install python3-pyaudio # to play saved mp3 file
sudo apt-get install portaudio19-dev python-pyaudio
```

This library needs to be installed after the others:

```bash
pip install PyAudio
```

As we are working with our own virtual environment we must create a link to some libraries of those packages we just installed as `sudo` into our environment.

Here I am linking the environment I use, called `ds`

```bash
# Link to gi library (from python-object)
ln -s /usr/lib/python3/dist-packages/gi/ /home/iggy/.pyenv/versions/ds/lib/python3.6/site-packages/

```

Install Flask:

```
pip install Flask
```

