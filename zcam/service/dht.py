import Adafruit_DHT
import logging
import time

import zcam.app.zmq

LOG = logging.getLogger(__name__)

default_interval = 30
default_model = 'dht22'


class DHTSensorApp(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.sensor.dht'

    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--pin')
        p.add_argument('--model')
        p.add_argument('--interval')
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            'pin', 'model', 'interval'
        ]

    def main(self):
        pin = int(self.get('pin'))
        model = self.get('model', default_model)
        interval = int(self.get('interval', default_interval))

        model_id = getattr(Adafruit_DHT, model.upper())

        LOG.info('starting dht sensor %s on pin %d',
                 self.name, pin)

        while True:
            reading = Adafruit_DHT.read_retry(model_id, pin)
            if all(val is not None for val in reading):
                LOG.debug('dht sensor %s on pin %d '
                          'got humidity = %f, temp = %f',
                          self.name, pin, *reading)

                for i, label in enumerate(['humidity', 'temperature']):
                    self.send_message(
                        '{}.{}'.format(self.name, label),
                        tags=dict(pin=pin, instance=self.args.instance,
                                  model=model),
                        fields=dict(value=reading[i]))
            else:
                LOG.warning('dht sensor %s failed to read value from pin %d',
                            self.name, pin)

            time.sleep(interval)


def main():
    app = DHTSensorApp()
    app.run()
