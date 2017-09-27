import abc
import argparse
import configparser
import logging
import msgpack
import zmq

import zcam.config

LOG = logging.getLogger(__name__)


class App(abc.ABC):

    def __init__(self,
                 name=None,
                 default_config_file=None,
                 default_config_values=None):

        self.default_config_file = default_config_file
        self.default_config_values = default_config_values
        self.name = name if name is not None else self.qual_name

        self.parser = self.create_parser()
        self.config = self.create_config()

        self.parse_args()
        self.read_config()
        self.overrides = self.create_overrides()
        self.apply_overrides()
        self.configure_logging()

    @property
    def qual_name(self):
        return self.__module__

    def configure_logging(self):
        logging.basicConfig(level=self.args.loglevel)

    def create_parser(self):
        p = argparse.ArgumentParser()
        p.add_argument('--config-file', '-f',
                       default=[],
                       action='append')

        g = p.add_argument_group('Logging options')
        g.add_argument('--verbose', '-v',
                       action='store_const',
                       const='INFO',
                       dest='loglevel')
        g.add_argument('--debug', '-d',
                       action='store_const',
                       const='DEBUG',
                       dest='loglevel')

        p.set_defaults(loglevel='WARNING')

        return p

    def create_overrides(self):
        return []

    def parse_args(self):
        self.args = self.parser.parse_args()

    def create_config(self):
        defaults = {}
        if self.default_config_values:
            defaults.update(self.default_config_values)
        defaults.update(zcam.config.DEFAULTS)

        config = configparser.ConfigParser(
            defaults=defaults,
        )
        return config

    def create_required_sections(self):
        if not self.config.has_section(self.name):
            self.config.add_section(self.name)

    def read_config(self):
        config_files = self.args.config_file + [self.default_config_file]
        for cfg in (path for path in config_files if path is not None):
            self.config.read(cfg)

        self.create_required_sections()

    def apply_overrides(self):
        for arg, section, option in self.overrides:
            val = getattr(self.args, arg, None)
            if val is not None:
                self.config.set(section, option, val)

    @abc.abstractmethod
    def main(self):
        raise NotImplemented()

    def run(self):
        try:
            self.main()
        except KeyboardInterrupt:
            pass


class ZmqBaseApp(App):

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
        suburi = self.config.get(self.name, 'sub_connect_uri')
        puburi = self.config.get(self.name, 'pub_connect_uri')
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
