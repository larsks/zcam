#!/bin/sh

. .venv/bin/activate

if [ -z "$1" ]; then
	exec screen -c screenrc $0 "start"
fi

set -x
exec 2> log

rpi() {
	uname -m | grep -q armv7
}

service() {
	cmd=$1
	shift
	echo "$cmd --debug -f zcam.conf $*; sleep inf"
}

screen -t proxy  sh -c "$(service zcam-service-proxy)"
rpi && screen -t led_heartbeat sh -c "$(service zcam-service-led --instance heartbeat)"
rpi && screen -t led_arm sh -c "$(service zcam-service-led --instance arm)"
rpi && screen -t led_motion sh -c "$(service zcam-service-led --instance motion)"
rpi && screen -t led_activity sh -c "$(service zcam-service-led --instance activity)"
rpi && screen -t motion sh -c "$(service zcam-service-gpio --instance motion)"
rpi && screen -t btn_arm sh -c "$(service zcam-service-button --instance btn_arm)"
rpi && screen -t dht sh -c "$(service zcam-service-dht)"
rpi && screen -t camera sh -c "$(service zcam-service-camera)"
screen -t keypad sh -c "$(service zcam-service-keypad)"
screen -t passcode sh -c "$(service zcam-service-passcode)"
screen -t activity sh -c "$(service zcam-service-activity)"
screen -t record sh -c "$(service zcam-service-record)"
screen -t metrics sh -c "$(service zcam-service-metrics)"
screen -t controller sh -c "$(service zcam-service-controller)"
screen -t heartbeat sh -c "$(service zcam-service-heartbeat)"
