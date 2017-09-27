import logging
import time

import zcam.app.base
import zcam.app.zmq

LOG = logging.getLogger(__name__)


class SendMessage(zcam.app.zmq.ZmqClientApp):
    def create_parser(self):
        p = super().create_parser()
        p.add_argument('topic')
        p.add_argument('kv', nargs='*',
                       type=zcam.app.base.KeyValueArgument)
        return p

    def main(self):
        msg = {k: v for k, v in self.args.kv}
        LOG.info('sending message %s %s', self.args.topic, msg)
        self.send_message(self.args.topic, **msg)

        # give zmq a chance to send the message
        time.sleep(1)


def main():
    app = SendMessage()
    app.run()
