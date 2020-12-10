#! /bin/bash

REBUILT=false

while getopts "b" flag
do
    case $flag in
        b)
            echo "Build flag found, rebuilding Docker image."
            docker build -t nli .
            REBUILT=true
            ;;
        \?)
            cat << EOF
Usage: run.sh [-b]
-b  (re)build docker image

Optionally build and runs the app in a docker container.
EOF

            exit 1
            ;;
  esac
done

if [ "$REBUILT" != true ] ; then
    echo "Did not re-build image, consider using the -b flag to re-build."
fi
echo "Running app in container. Visit: http://127.0.0.1:5000"

docker run -it \
 -p 5000:5000 \
 -e PULSE_SERVER=docker.for.mac.localhost \
 -v ~/.config/pulse:/root/.config/pulse \
 -v "$(pwd)":/NLI_Project \
 --rm \
 nli
