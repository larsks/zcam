import influxdb
import logging

import zcam.app.zmq

LOG = logging.getLogger(__name__)

default_host = '127.0.0.1'
default_port = '8086'
default_database = 'zcam'


class MetricsPublisher(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.service.metrics'

    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--host')
        p.add_argument('--port')
        p.add_argument('--database')
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            'host', 'port', 'database'
        ]

    def main(self):
        host = self.get('host', default_host)
        port = int(self.get('port', default_port))
        database = self.get('database', default_database)

        client = influxdb.InfluxDBClient(host=host, port=port)

        client.create_database(database)
        client.switch_database(database)

        self.sub.subscribe('zcam.sensor')

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
