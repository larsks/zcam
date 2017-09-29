import logging
import zmq

import zcam.app.zmq
import zcam.schema.config

LOG = logging.getLogger(__name__)


class ProxyApp(zcam.app.zmq.ZmqBaseApp):
    namespace = 'zcam.service.proxy'
    schema = zcam.schema.config.ProxySchema(strict=True)

    def main(self):
        zmq.proxy(self.pub, self.sub)

    def create_sockets(self):
        suburi = self.config['sub_bind_uri']
        puburi = self.config['pub_bind_uri']

        LOG.info('publishing messages on %s', puburi)
        LOG.info('collecting messages on %s', suburi)

        self.pub = self.ctx.socket(zmq.XPUB)
        self.pub.bind(puburi)
        self.pub.setsockopt(zmq.LINGER, 500)

        self.sub = self.ctx.socket(zmq.XSUB)
        self.sub.bind(suburi)
        self.sub.setsockopt(zmq.LINGER, 500)

    def cleanup(self):
        if self.pub:
            self.pub.close()
        if self.sub:
            self.sub.close()
        super().cleanup()


def main():
    app = ProxyApp()
    app.run()
