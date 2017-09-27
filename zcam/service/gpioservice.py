import logging
import zmq

from RPi import GPIO

import zcam.app

LOG = logging.getLogger(__name__)


class GpioServiceApp(zcam.app.ZmqClientApp):
    def __init__(self, sensorname, bouncetime=None, **kwargs):
        super().__init__(**kwargs)
        self.sensorname = sensorname
        self.bouncetime = bouncetime

    def main(self):
        pin = self.config.get(self.name, '{}_pin' % self.sensorname)
        GPIO.setup(GPIO.BCM)
        GPIO.setmode(pin, GPIO.IN)

        waitargs = {}
        if self.bouncetime:
            waitargs['bouncetime'] = self.bouncetime

        while True:
            GPIO.wait_for_edge(pin, GPIO.BOTH, **waitargs)
            self.send_message('sensor.{}'.format(self.sensorname),
                              value=GPIO.input(pin))
