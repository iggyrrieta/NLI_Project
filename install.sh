#!/bin/bash

echo "====================================="
echo "NLI_PROJECT INSTALLATION"
echo "====================================="
while true; do
    read -p "which OS are you using [1:LINUX, 2:MACOS 3: WINDOWS]: " os
    case $os in
        [1]* ) 
            echo "=================================="
            echo "Installing LINUX APT dependencies"
            echo "=================================="
            # INSTALL PACKAGES AND DEPENDENCIES
            sudo apt update && sudo apt install -y \
                python-gobject \
                python3-pyaudio \
                portaudio19-dev \
                python3-pyaudio

             break;;

        [2]* )
            echo "Sorry not implemented yet..."
            break;;

        [3]* )
            echo "Sorry not implemented yet..."
            break;;

        * ) echo "Please answer 1 or 2 or 3";;
    esac
done

# This is python using pip so should be general
echo "=================================="
echo "Installing APT dependencies"
echo "=================================="
python3 -m pip install -U \
  requests \
  flask \
  SpeechRecognition \
  playsound \
  gTTS \
  pyaudio \
  pandas \
  sklearn \
  spacy \
  jupyter \
  jupyterlab \
  textacy \
  wikipedia

echo "=================================="
echo "Installing SPACY DICTIONARIES"
echo "=================================="
  python -m spacy download en_core_web_lg

echo "END"
echo "=====================================================";

echo "======================================================"
echo "Installation completed!"
echo "======================================================"
