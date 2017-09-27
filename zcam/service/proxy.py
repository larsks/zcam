import logging
import zmq

import zcam.app

LOG = logging.getLogger(__name__)


class ProxyApp(zcam.app.ZmqBaseApp):

    def main(self):
        LOG.info('pub socket is %s', self.puburi)
        LOG.info('sub socket is %s', self.suburi)
        zmq.proxy(self.pub, self.sub)

    @property
    def puburi(self):
        return self.config.get(self.name, 'pub_bind_uri')

    @property
    def suburi(self):
        return self.config.get(self.name, 'sub_bind_uri')

    def create_sockets(self):
        self.pub = self.ctx.socket(zmq.PUB)
        self.sub = self.ctx.socket(zmq.SUB)

        self.pub.bind(self.puburi)
        self.sub.bind(self.suburi)


def main():
    app = ProxyApp()
    app.run()
