import json
import logging
import time

import zcam.app.base
import zcam.app.zmq

LOG = logging.getLogger(__name__)


class SendMessage(zcam.app.zmq.ZmqClientApp):
    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--json',
                       action='store_true')
        p.add_argument('topic')
        p.add_argument('msg', nargs='*')
        return p

    def main(self):
        # this gives the zmq connection thread time to
        # connect to the remote socket.  See
        # http://zguide.zeromq.org/page:all#Getting-the-Message-Out
        time.sleep(0.1)
        if self.args.json:
            msg = json.loads(self.args.msg[0])
        else:
            msg = {k: v
                   for k, v in [kv.split('=')
                                for kv in self.args.msg.split(' ')]}

        LOG.info('sending message %s %s', self.args.topic, msg)
        self.send_message(self.args.topic, **msg)


def main():
    app = SendMessage()
    app.run()
