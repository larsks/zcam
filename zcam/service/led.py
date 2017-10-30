import logging

from RPi import GPIO

import zcam.app.zmq
import zcam.led
import zcam.schema.config

LOG = logging.getLogger(__name__)


class LedService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.device.led'
    schema = zcam.schema.config.LedSchema(strict=True)

    def main(self):
        pin = self.config['pin']
        subscription = self.config['subscription']
        self.sub.subscribe(subscription)

        GPIO.setmode(GPIO.BCM)
        led = zcam.led.LED(pin, state=0)

        while True:
            topic, msg = self.receive_message()
            try:
                led.set(msg[b'value'])
            except KeyError:
                LOG.error('received invalid message')


def main():
    app = LedService()
    app.run()
