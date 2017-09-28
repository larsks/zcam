import logging

from RPi import GPIO

import zcam.app.zmq

LOG = logging.getLogger(__name__)


class GpioService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.sensor.gpio'

    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--pin')
        p.add_argument('--bouncetime')
        g = p.add_mutually_exclusive_group()
        g.add_argument('--pull-up',
                       action='store_true')
        g.add_argument('--pull-down',
                       action='store_true')
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            'pin', 'bouncetime',
            'pull_up', 'pull_down'
        ]

    def main(self):
        pin = int(self.get('pin'))
        bouncetime = self.get('bouncetime', None)
        pull_up = self.get('pull_up', 'false').lower() == 'true'
        pull_down = self.get('pull_down', 'false').lower() == 'true'

        if pull_up and pull_down:
            raise ValueError('pull_up and pull_down are mutually exclusive')

        if pull_up:
            pud = GPIO.PUD_UP
        elif pull_down:
            pud = GPIO.PUD_DOWN
        else:
            pud = GPIO.PUD_OFF

        waitargs = {}
        if bouncetime:
            waitargs['bouncetime'] = int(bouncetime)

        LOG.info('starting gpio sensor %s on pin %d', self.name, pin)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=pud)

        while True:
            GPIO.wait_for_edge(pin, GPIO.BOTH, **waitargs)
            value = GPIO.input(pin)
            LOG.debug('%s event %s on pin %s', self.name, value, pin)
            self.send_message('{}'.format(self.name),
                              tags=dict(pin=pin, instance=self.args.instance),
                              fields=dict(value=value))


def main():
    app = GpioService()
    app.run()
