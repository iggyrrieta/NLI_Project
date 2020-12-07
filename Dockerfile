FROM python:3.8

WORKDIR /NLI_Project


RUN apt update && apt install -y \
python-gobject \
python3-pyaudio \
portaudio19-dev \
python3-pyaudio \
espeak \
vorbis-tools \
sox \
alsa-utils \
libasound2 \
libasound2-plugins \
pulseaudio \
pulseaudio-utils \
--no-install-recommends \
&& rm -rf /var/lib/apt/lists/*

COPY poetry.lock .
COPY pyproject.toml .
RUN pip install poetry
RUN poetry install
RUN poetry run python -m spacy download en_core_web_lg
RUN usermod -aG audio,pulse,pulse-access root

CMD exec poetry run python -u test.py 2>&1