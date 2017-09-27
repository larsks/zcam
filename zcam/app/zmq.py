import abc
import logging
import msgpack
import zmq

from zcam.app.base import BaseApp

LOG = logging.getLogger(__name__)


class ZmqBaseApp(BaseApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.create_context()
        self.create_sockets()

    def create_context(self):
        self.ctx = zmq.Context()

    @abc.abstractmethod
    def create_sockets(self):
        raise NotImplemented()


class ZmqClientApp(ZmqBaseApp):
    def create_sockets(self):
        suburi = self.get('sub_connect_uri')
        puburi = self.get('pub_connect_uri')
        LOG.info('publishing events on %s', suburi)
        LOG.info('listening for events on %s', puburi)

        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.connect(suburi)

        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect(puburi)

    def send_message(self, tag, **message):
        self.pub.send_multipart([
            bytes(tag, 'utf8'),
            msgpack.dumps(message)])

    def receive_message(self):
        msg = self.sub.recv_multipart()
        return (msg[0], msgpack.loads(msg[1]))

    def cleanup(self):
        super().cleanup()
        self.pub.close()
        self.sub.close()
        self.ctx.term()
