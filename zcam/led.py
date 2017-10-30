import logging
from RPi import GPIO

LOG = logging.getLogger(__name__)


class LED(object):
    def __init__(self, pin, state=None):
        self.pin = pin
        self.state = None
        self.setup()

        if state:
            self.set(state)

    def setup(self):
        GPIO.setup(self.pin, GPIO.OUT)

    def set(self, state):
        if state not in (0, 1):
            raise ValueError('led state must be 0 or 1')

        GPIO.output(self.pin, state)
        self.state = state

    def on(self):
        self.set(1)

    def off(self):
        self.set(0)
