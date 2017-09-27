import logging
import zmq

import zcam.app.zmq

LOG = logging.getLogger(__name__)


class ProxyApp(zcam.app.zmq.ZmqBaseApp):
    namespace = 'zcam.service.proxy'

    def main(self):
        zmq.proxy(self.pub, self.sub)

    def create_sockets(self):
        suburi = self.get('sub_bind_uri')
        puburi = self.get('pub_bind_uri')

        LOG.info('collecting messages on %s', suburi)
        LOG.info('publishing messages on %s', puburi)

        self.pub = self.ctx.socket(zmq.XPUB)
        self.pub.bind(puburi)

        self.sub = self.ctx.socket(zmq.XSUB)
        self.sub.bind(suburi)


def main():
    app = ProxyApp()
    app.run()
