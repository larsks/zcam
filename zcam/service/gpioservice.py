import logging

from RPi import GPIO

import zcam.app

LOG = logging.getLogger(__name__)


class GpioServiceApp(zcam.app.ZmqClientApp):
    def __init__(self, sensorname, bouncetime=None, **kwargs):
        self.sensorname = sensorname
        self.bouncetime = bouncetime
        super().__init__(**kwargs)

    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--pin')
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            ('pin', self.name, '{}_pin'.format(self.sensorname)),
        ]

    def main(self):
        pin = self.config.get(self.name, '{}_pin'.format(self.sensorname))
        LOG.info('starting %s on pin %d', self.name, pin)
        GPIO.setup(GPIO.BCM)
        GPIO.setmode(pin, GPIO.IN)

        waitargs = {}
        if self.bouncetime:
            waitargs['bouncetime'] = self.bouncetime

        while True:
            GPIO.wait_for_edge(pin, GPIO.BOTH, **waitargs)
            LOG.debug('%s event on pin %s', self.name, pin)
            self.send_message('sensor.{}'.format(self.sensorname),
                              value=GPIO.input(pin))
