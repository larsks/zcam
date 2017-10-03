#!/bin/sh

. .venv/bin/activate

if [ -z "$1" ]; then
	exec screen -c screenrc $0 "start"
fi

set -x
exec 2> log

rpi() {
	uname -m | grep -q arm7
}

service() {
	cmd=$1
	shift
	echo "$cmd --debug -f zcam.conf $*; sleep inf"
}

screen -t proxy  sh -c "$(service zcam-service-proxy)"
rpi && screen -t led sh -c "$(service zcam-service-led --instance heartbeat)"
rpi && screen -t motion sh -c "$(service zcam-service-gpio --instance motion)"
rpi && screen -t door sh -c "$(service zcam-service-gpio --instance door)"
rpi && screen -t door sh -c "$(service zcam-service-button --instance btn_arm)"
rpi && screen -t dht sh -c "$(service zcam-service-dht)"
rpi && screen -t camera sh -c "$(service zcam-service-camera)"
screen -t keypad sh -c "$(service zcam-service-keypad)"
screen -t passcode sh -c "$(service zcam-service-passcode)"
screen -t activity sh -c "$(service zcam-service-activity)"
screen -t metrics sh -c "$(service zcam-service-metrics)"
screen -t controller sh -c "$(service zcam-service-controller)"
screen -t heatbeat sh -c "$(service zcam-service-heatbeat)"
