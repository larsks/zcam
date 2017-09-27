import influxdb
import logging

import zcam.app

LOG = logging.getLogger(__name__)


class MetricsPublisher(zcam.app.ZmqClientApp):

    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--host')
        p.add_argument('--port')
        p.add_argument('--database')
        p.add_argument('name')
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            ('host', self.name, '{}_host'.format(self.args.name)),
            ('port', self.name, '{}_port'.format(self.args.name)),
            ('database', self.name, '{}_database'.format(self.args.name)),
        ]

    def main(self):
        host = self.config.get(
            self.name,
            '{}_host'.format(self.args.name),
            fallback='localhost')
        port = self.config.getint(
            self.name,
            '{}_port'.format(self.args.name),
            fallback=8086)
        database = self.config.getint(
            self.name,
            '{}_database'.format(self.args.name),
            fallback='zcam')

        client = influxdb.InfluxDBClient(
            host=host, port=port)

        client.create_database(database)
        client.switch_database(database)

        self.sub.subscribe('sensor')

        while True:
            topic, data = self.receive_message()
            try:
                LOG.debug('sending metric %s with fields %s',
                          topic, data[b'fields'])
                client.write_points([dict(
                    measurement=topic,
                    tags=data.get(b'tags', {}),
                    fields=data[b'fields'],
                )])
            except Exception as err:
                LOG.error('malformed message: %s', err)


def main():
    app = MetricsPublisher()
    app.run()
