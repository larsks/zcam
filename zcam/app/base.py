import argparse
import configparser
import logging
import marshmallow

import zcam.schema.config

LOG = logging.getLogger(__name__)
UNSET = object()


def InstanceSetter(app):
    class _InstanceSetter(argparse.Action):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.app = app

        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values)
            self.app.instance = values

    return _InstanceSetter


class BaseApp(object):
    namespace = 'zcam'
    schema = zcam.schema.config.BaseSchema(strict=True)
    instance = 'default'

    def __init__(self):
        self.configparser = self.create_configparser()
        self.argparser = self.create_argparser()

    @property
    def name(self):
        return '{}.{}'.format(self.namespace, self.instance)

    def create_argparser(self):
        p = argparse.ArgumentParser()
        p.add_argument('--config-file', '-f',
                       default=[],
                       action='append')
        p.add_argument('--instance',
                       default='default',
                       action=InstanceSetter(self))

        g = p.add_argument_group('Logging options')
        g.add_argument('--quiet', '-q',
                       action='store_const',
                       const='WARNING',
                       dest='loglevel')
        g.add_argument('--verbose', '-v',
                       action='store_const',
                       const='INFO',
                       dest='loglevel')
        g.add_argument('--debug', '-d',
                       action='store_const',
                       const='DEBUG',
                       dest='loglevel')

        g = p.add_argument_group('Config options')
        for fieldname, fieldspec in sorted(self.schema.fields.items()):
            if isinstance(fieldspec, marshmallow.fields.List):
                g.add_argument('--{}'.format(fieldname.replace('_', '-')),
                               action='append',
                               default=[])
            elif isinstance(fieldspec, marshmallow.fields.Boolean):
                g.add_argument('--{}'.format(fieldname.replace('_', '-')),
                               action='store_true',
                               dest=fieldname)
                g.add_argument('--no-{}'.format(fieldname.replace('_', '-')),
                               action='store_false',
                               dest=fieldname)
            else:
                g.add_argument('--{}'.format(fieldname.replace('_', '-')))

        p.set_defaults(loglevel='INFO')

        return p

    def create_configparser(self):
        return configparser.ConfigParser()

    def parse_args(self):
        self.args = self.argparser.parse_args()

    def read_config(self):
        for cf in self.args.config_file:
            self.configparser.read(cf)

    def validate_config(self):
        hier = self.name.split('.')
        config = {}
        for section in ['.'.join(hier[:i + 1]) for i in range(len(hier))]:
            LOG.debug('checking section %s', section)
            try:
                config.update(dict(self.configparser[section]))
            except KeyError:
                pass

        LOG.debug('config before args: %s', config)
        LOG.debug('args: %s', self.args)

        config.update({k: v for k, v in vars(self.args).items()
                       if v is not None})

        LOG.debug('config after args: %s', config)

        result, errors = self.schema.load(config)
        self.config = result

    def configure_logging(self):
        logging.basicConfig(level=self.args.loglevel)

    def configure_loglevels(self):
        for logspec in self.config.get('loglevels', []):
            name, level = logspec.split('=', 1)
            logger = logging.getLogger(name)
            logger.setLevel(level)

    def prepare(self):
        LOG.debug('preparing')
        pass

    def cleanup(self):
        LOG.debug('cleaning up')
        pass

    def main(self):
        raise NotImplemented()

    def run(self):
        try:
            self.parse_args()
            self.configure_logging()
            self.read_config()
            self.validate_config()
            self.configure_loglevels()

            LOG.info('starting %s', self.name)
            self.prepare()
            self.main()
        except KeyboardInterrupt:
            pass
        except marshmallow.exceptions.ValidationError as err:
            LOG.error('There was an error in the configuration:')
            for fieldname, errors in err.messages.items():
                for error in errors:
                    if fieldname == '_schema':
                        LOG.error('%s', error)
                    else:
                        LOG.error('In field %s: %s', fieldname, error)
        finally:
            self.cleanup()
