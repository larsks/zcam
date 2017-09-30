import influxdb
import logging

import zcam.app.zmq
import zcam.schema.config

LOG = logging.getLogger(__name__)


class MetricsPublisher(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.service.metrics'
    schema = zcam.schema.config.MetricsSchema(strict=True)

    def main(self):
        host = self.config['host']
        port = self.config['port']
        database = self.config['database']

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
                    fields=dict(value=data.value)
                )])
            except Exception as err:
                LOG.error('failed to write metric: %s', err)


def main():
    app = MetricsPublisher()
    app.run()
