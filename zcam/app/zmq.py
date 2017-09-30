import logging
import msgpack
import zmq

from zcam.app.base import BaseApp

LOG = logging.getLogger(__name__)


class ZmqBaseApp(BaseApp):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ctx = None

    def prepare(self):
        self.create_context()
        self.create_sockets()

    def create_context(self):
        self.ctx = zmq.Context()

    def cleanup(self):
        if self.ctx:
            self.ctx.term()
        super().cleanup()


class ZmqClientApp(ZmqBaseApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sub = None
        self.pub = None

    def create_sockets(self):
        suburi = self.config['sub_connect_uri']
        puburi = self.config['pub_connect_uri']
        LOG.info('publishing events on %s', suburi)
        LOG.info('collecting events on %s', puburi)

        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.connect(suburi)
        self.pub.setsockopt(zmq.LINGER, 500)

        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect(puburi)
        self.sub.setsockopt(zmq.LINGER, 500)

    def send_message(self, topic, **message):
        LOG.debug('%s sending topic %s with content %s',
                  self.name, topic, message)
        self.pub.send_multipart([
            bytes(topic, 'utf8'),
            msgpack.dumps(message)])

    def receive_message(self):
        topic, message = self.sub.recv_multipart()
        message = msgpack.loads(message)
        LOG.debug('%s received topic %s with content %s',
                  self.name, topic, message)

        return (topic, message)

    def cleanup(self):
        if self.pub:
            self.pub.close()
        if self.sub:
            self.sub.close()
        super().cleanup()
