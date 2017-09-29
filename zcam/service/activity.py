import logging

import zcam.app.zmq
import zcam.schema.config
import zcam.timer

LOG = logging.getLogger(__name__)


class ActivityService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.service.activity'
    schema = zcam.schema.config.ActivitySchema(strict=True)

    def main(self):
        self.sub.subscribe('zcam.sensor.gpio.motion')


def main():
    app = ActivityService()
    app.run()
