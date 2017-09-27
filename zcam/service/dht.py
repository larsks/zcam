import Adafruit_DHT
import logging
import time

import zcam.app

LOG = logging.getLogger(__name__)


class DHTSensorApp(zcam.app.ZmqClientApp):

    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--pin')
        p.add_argument('--model')
        p.add_argument('--interval', type=float)
        p.add_argument('name')
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            ('pin', self.name, '{}_pin'.format(self.args.name)),
            ('model', self.name, '{}_model'.format(self.args.name)),
            ('interval', self.name, '{}_interval'.format(self.args.name)),
        ]

    def main(self):
        pin = self.config.getint(self.name,
                                 '{}_pin'.format(self.args.name))
        model = self.config.getint(self.name,
                                   '{}_model'.format(self.args.name),
                                   fallback='dht22')
        interval = self.config.getint(self.name,
                                      '{}_interval'.format(self.args.name),
                                      fallback=60)

        model_id = getattr(Adafruit_DHT, model.upper())

        LOG.info('starting dht sensor %s on pin %d',
                 self.args.name, pin)

        while True:
            humidity, temperature = Adafruit_DHT.read_retry(model_id, pin)
            if humidity is not None and temperature is not None:
                LOG.debug('dht sensor %s on pin %d '
                          'got humidity = %f, temp = %f',
                          self.args.name, pin, humidity, temperature)
                self.send_message(
                    'sensor.dht.{}.temperature'.format(self.args.name),
                    tags=dict(pin=pin, model=model),
                    fields=dict(value=temperature))
                self.send_message(
                    'sensor.dht.{}.humidity'.format(self.args.name),
                    tags=dict(pin=pin, model=model),
                    fields=dict(value=humidity))
            else:
                LOG.warning('dht sensor %s failed to read value from pin %d',
                            self.args.name, pin)

            time.sleep(interval)


def main():
    app = DHTSensorApp()
    app.run()
