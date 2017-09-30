#!/bin/sh

. .venv/bin/activate

if [ -z "$1" ]; then
	exec screen -c screenrc $0 "start"
fi

screen -t proxy       zcam-service-proxy -f zcam.conf                     --debug
screen -t led         zcam-service-led -f zcam.conf --instance heartbeat  --debug

screen -t motion      zcam-service-gpio --instance motion -f zcam.conf    --debug
screen -t door        zcam-service-gpio --instance door -f zcam.conf      --debug
screen -t btn_arm     zcam-service-button --instance btn_arm -f zcam.conf --debug
screen -t dht         zcam-service-dht -f zcam.conf                       --debug
screen -t keypad      zcam-service-keypad -f zcam.conf                    --debug
screen -t passcode    zcam-service-passcode -f zcam.conf                  --debug
screen -t activity    zcam-service-activity -f zcam.conf                  --debug

screen -t metrics     zcam-service-metrics -f zcam.conf                   --debug
screen -t messages    zcam-service-messages -f zcam.conf                  --debug
screen -t controller  zcam-service-controller -f zcam.conf                --debug
screen -t heartbeat   zcam-service-heartbeat -f zcam.conf                 --debug
