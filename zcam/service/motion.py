import logging

import zcam.service.gpioservice

LOG = logging.getLogger(__name__)


class MotionSensorApp(zcam.service.gpioservice.GpioServiceApp):
    def __init__(self, **kwargs):
        super().__init__('motion', **kwargs)


def main():
    app = MotionSensorApp()
    app.run()
