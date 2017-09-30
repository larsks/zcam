import itertools
import logging
import time

import zcam.app.zmq
import zcam.schema.config

LOG = logging.getLogger(__name__)


class HeartbeatService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.heartbeat'
    schema = zcam.schema.config.BaseSchema(strict=True)

    def main(self):
        value = itertools.cycle((0, 1))
        while True:
            self.send_message('{}'.format(self.name),
                              value=next(value))
            time.sleep(1)


def main():
    app = HeartbeatService()
    app.run()
