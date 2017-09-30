import logging
from marshmallow.fields import List, String

import zcam.app.zmq
import zcam.schema.config

LOG = logging.getLogger(__name__)


class LogMessagesApp(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.service.messages'
    schema = zcam.schema.config.MessagesSchema(strict=True)

    def main(self):
        subscription = next(sub for sub in [self.config.get('subscription'), ['']]
                            if sub)
        for sub in subscription:
            LOG.debug('subscribing to %s', repr(sub))
            self.sub.subscribe(bytes(sub, 'utf8'))

        while True:
            tag, msg = self.receive_message()
            LOG.debug('%s: %s', tag, msg)


def main():
    app = LogMessagesApp()
    app.run()
