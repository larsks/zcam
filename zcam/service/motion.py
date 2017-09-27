import logging
import zmq

from RPi import GPIO

import zcam.service.gpioservice
import zcam.config

LOG = logging.getLogger(__name__)


class MotionSensorApp(zcam.service.gpioservice.GpioServiceApp):
    def __init__(self, **kwargs):
        super().__init__('motion', **kwargs)
