import logging

from RPi import GPIO

import zcam.app.zmq
import zcam.schema.gpio

LOG = logging.getLogger(__name__)


class GpioService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.sensor.gpio'
    schema = zcam.schema.gpio.GpioSchema(strict=True)

    def main(self):
        pin = self.config['pin']
        bouncetime = self.config.get('bouncetime')
        edge = self.config['edge']
        pull = self.config['pull']

        waitargs = {}
        if bouncetime:
            waitargs['bouncetime'] = int(bouncetime)

        LOG.info('starting gpio sensor %s on pin %d pull %d edge %d',
                 self.name, pin, pull, edge)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=pull)

        while True:
            GPIO.wait_for_edge(pin, edge, **waitargs)
            value = GPIO.input(pin)
            LOG.debug('%s event %s on pin %s', self.name, value, pin)
            self.send_message('{}'.format(self.name),
                              tags=dict(pin=pin, instance=self.instance),
                              fields=dict(value=value))


def main():
    app = GpioService()
    app.run()
