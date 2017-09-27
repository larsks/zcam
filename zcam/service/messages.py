import logging

import zcam.app.zmq

LOG = logging.getLogger(__name__)


class LogMessagesApp(zcam.app.zmq.ZmqClientApp):
    def create_parser(self):
        p = super().create_parser()
        p.add_argument('subscription',
                       nargs='*')
        return p

    def main(self):
        if not self.args.subscription:
            self.args.subscription = ['']

        for sub in self.args.subscription:
            LOG.debug('subscribing to %s', repr(sub))
            self.sub.subscribe(bytes(sub, 'utf8'))

        while True:
            tag, msg = self.receive_message()
            LOG.debug('%s: %s', tag, msg)


def main():
    app = LogMessagesApp()
    app.run()
