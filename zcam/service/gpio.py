import logging

from RPi import GPIO

import zcam.app.zmq

LOG = logging.getLogger(__name__)


class GpioService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.sensor.gpio'
    default_pull = None
    default_edge = None
    default_bouncetime = None

    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--pin')
        p.add_argument('--edge',
                       choices=['rising', 'falling', 'both'])
        p.add_argument('--bouncetime')
        p.add_argument('--pull',
                       choices=['up', 'down'])
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            'pin', 'bouncetime', 'edge', 'pull'
        ]

    def main(self):
        pin = int(self.get('pin'))
        bouncetime = self.get('bouncetime', self.default_bouncetime)
        edge = self.get('edge', self.default_edge)
        pull = self.get('pull', self.default_pull)

        if pull == 'up':
            _pull = GPIO.PUD_UP
        elif pull == 'down':
            _pull = GPIO.PUD_DOWN
        else:
            _pull = GPIO.PUD_OFF

        if edge == 'rising':
            _edge = GPIO.RISING
        elif edge == 'falling':
            _edge = GPIO.FALLING
        else:
            _edge = GPIO.BOTH

        waitargs = {}
        if bouncetime:
            waitargs['bouncetime'] = int(bouncetime)

        LOG.info('starting gpio sensor %s on pin %d pull %d edge %d',
                 self.name, pin, _pull, _edge)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=_pull)

        while True:
            GPIO.wait_for_edge(pin, _edge, **waitargs)
            value = GPIO.input(pin)
            LOG.debug('%s event %s on pin %s', self.name, value, pin)
            self.send_message('{}'.format(self.name),
                              tags=dict(pin=pin, instance=self.args.instance),
                              fields=dict(value=value))


def main():
    app = GpioService()
    app.run()
