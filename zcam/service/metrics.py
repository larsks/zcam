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
            'localhost')
        port = self.config.getint(
            self.name,
            '{}_port'.format(self.args.name),
            8086)
        database = self.config.getint(
            self.name,
            '{}_database'.format(self.args.name))

        client = influxdb.InfluxDBClient(
            host=host, port=port)

        client.create_database(database)
        client.switch_database(database)

        self.sub.subscribe('sensor')

        while True:
            topic, data = self.receive_message()
            self.client.write_points([dict(
                measurement=topic,
                tags=data['tags'],
                fields=data['fields'],
            )])


def main():
    app = MetricsPublisher()
    app.run()
