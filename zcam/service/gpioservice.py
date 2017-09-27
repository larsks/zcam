import logging

from RPi import GPIO

import zcam.app

LOG = logging.getLogger(__name__)


class GpioService(zcam.app.ZmqClientApp):

    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--pin')
        p.add_argument('--bouncetime')
        p.add_argument('name')
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            ('pin', self.name, '{}_pin'.format(self.args.name)),
            ('bouncetime', self.name, '{}_bouncetime'.format(self.args.name)),
        ]

    def main(self):
        pin = self.config.getint(self.name,
                                 '{}_pin'.format(self.args.name))
        bouncetime = self.config.getint(
            self.name,
            '{}_bouncetime'.format(self.args.name),
            fallback=None)

        LOG.info('starting gpio sensor %s on pin %d', self.args.name, pin)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN)

        waitargs = {}
        if bouncetime:
            waitargs['bouncetime'] = bouncetime

        while True:
            GPIO.wait_for_edge(pin, GPIO.BOTH, **waitargs)
            LOG.debug('%s event on pin %s', self.name, pin)
            self.send_message('sensor.gpio.{}'.format(self.args.name),
                              pin=pin,
                              value=GPIO.input(pin))


def main():
    app = GpioService()
    app.run()
