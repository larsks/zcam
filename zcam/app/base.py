import abc
import argparse
import configparser
import logging

import zcam.config

LOG = logging.getLogger(__name__)
UNSET = object()


def KeyValueArgument(value):
    try:
        k, v = value.split('=', 1)
        return k, v
    except ValueError:
        raise argparse.ArgumentError('values must of the form <key>=<value>')


class BaseApp(abc.ABC):
    namespace = 'zcam'

    def __init__(self,
                 default_config_file=None,
                 default_config_values=None):

        self.default_config_file = default_config_file
        self.default_config_values = default_config_values

        self.parser = self.create_parser()
        self.config = self.create_config()

        self.parse_args()
        self.read_config()
        self.overrides = self.create_overrides()
        self.apply_overrides()
        self.configure_logging()

    @property
    def name(self):
        return '.'.join(x for x in [self.namespace, self.args.instance]
                        if x is not None)

    def get(self, option, default=UNSET):
        '''Resolve a configuration value.

        Look for the named configuration value in the current section
        section (determined by `self.name`) and in any superior
        sections (determined by stripping dot-delimited components from
        the section name).
        '''

        components = self.name.split('.')
        hier = reversed([
            '.'.join(components[:i + 1])
            for i in range(len(components))
        ])

        for section in hier:
            LOG.debug('looking for %s in %s', option, section)
            try:
                return self.config.get(section, option)
            except (configparser.NoOptionError, configparser.NoSectionError):
                continue

        if default is not UNSET:
            return default
        else:
            raise KeyError(option)

    def set(self, option, value):
        return self.config.set(self.name, option, value)

    def options(self):
        return self.config.items(section=self.name)

    def configure_logging(self):
        logging.basicConfig(level=self.args.loglevel)

    def create_parser(self):
        p = argparse.ArgumentParser()
        p.add_argument('--config-file', '-f',
                       default=[],
                       action='append')
        p.add_argument('--option', '-o',
                       action='append',
                       type=KeyValueArgument,
                       metavar='OPTION=VALUE',
                       default=[])
        p.add_argument('--instance',
                       default='default')

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
        for option, value in self.args.option:
            self.set(option, value)

        for option in self.overrides:
            val = getattr(self.args, option, None)
            if val is not None:
                self.set(option, str(val))

    @abc.abstractmethod
    def main(self):
        raise NotImplemented()

    def run(self):
        LOG.info('starting %s', self.name)
        try:
            self.main()
        except KeyboardInterrupt:
            pass
