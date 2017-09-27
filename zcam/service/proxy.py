import logging
import zmq

import zcam.app
import zcam.config

LOG = logging.getLogger(__name__)


class ProxyApp(zcam.app.ZmqApp):
    def __init__(self, **kwargs):
        super().__init__(
            default_config_values=zcam.config.DEFAULTS,
            **kwargs)

    def main(self):
        LOG.info('pub socket is %s', self.puburi)
        LOG.info('sub socket is %s', self.suburi)
        zmq.proxy(self.pub, self.sub)

    @property
    def puburi(self):
        return self.config.get(self.name, 'puburi')

    @property
    def suburi(self):
        return self.config.get(self.name, 'suburi')

    def create_sockets(self):
        self.pub = self.ctx.socket(zmq.PUB)
        self.sub = self.ctx.socket(zmq.SUB)

        self.pub.bind(self.config.get(self.name, 'puburi'))
        self.sub.bind(self.config.get(self.name, 'suburi'))


def main():
    app = ProxyApp()
    app.run()
