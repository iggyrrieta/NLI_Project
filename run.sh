#! /bin/bash

docker build -t nli .
docker run -it -p 5000:5000 -e PULSE_SERVER=docker.for.mac.localhost -v ~/.config/pulse:/root/.config/pulse nli
