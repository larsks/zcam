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
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            'pin', 'bouncetime',
        ]

    def main(self):
        pin = int(self.get('pin'))
        bouncetime = self.get('bouncetime', None)

        waitargs = {}
        if bouncetime:
            waitargs['bouncetime'] = int(bouncetime)

        LOG.info('starting gpio sensor %s on pin %d', self.name, pin)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN)

        while True:
            GPIO.wait_for_edge(pin, GPIO.BOTH, **waitargs)
            LOG.debug('%s event on pin %s', self.name, pin)
            self.send_message('{}'.format(self.name),
                              tags=dict(pin=pin, instance=self.args.instance),
                              fields=dict(value=GPIO.input(pin)))


def main():
    app = GpioService()
    app.run()
