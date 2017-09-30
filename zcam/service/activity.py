import datetime
import logging

import zcam.app.zmq
import zcam.schema.config
import zcam.timer

LOG = logging.getLogger(__name__)

IDLE = 0
ACTIVE = 1
COOLDOWN = 3


class ActivityService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.service.activity'
    schema = zcam.schema.config.ActivitySchema(strict=True)

    def prepare(self):
        super().prepare()
        self.interval = self.config['interval']
        self.extend = self.config['extend']
        self.limit = self.config['limit']
        self.cooldown = self.config['cooldown']
        self.state = IDLE
        self.stopwatch = zcam.timer.StopWatch()

    def main(self):
        self.sub.subscribe('zcam.sensor.gpio.motion')

        while True:
            topic, msg = self.receive_message()

            if msg[b'fields'][b'value']:
                if self.state == COOLDOWN:
                    LOG.info('ignoring motion during cooldown')
                elif self.state == IDLE:
                    self.start_active()
                elif self.state == ACTIVE:
                    self.continue_active()

    def start_active(self):
        LOG.info('start activity')
        self.state = ACTIVE
        self.stopwatch.start()
        self.send_message('{}.start'.format(self.name), value=1)

        self.timer = zcam.timer.DynamicTimer(
            interval=self.interval,
            function=self.end_active,
            limit=self.limit)
        self.timer.start()

    def continue_active(self):
        LOG.info('continue activity')
        self.timer.extend(self.extend)

    def end_active(self):
        LOG.info('end activity')
        self.state = COOLDOWN
        duration = self.stopwatch.stop()
        self.send_message('{}.stop'.format(self.name),
                          value=0,
                          duration=duration.total_seconds())

        LOG.debug('cooldown for %d seconds', self.cooldown)
        self.timer = zcam.timer.DynamicTimer(
            interval=self.cooldown,
            function=self.end_cooldown)
        self.timer.start()

    def end_cooldown(self):
        LOG.info('end cooldown')
        self.state = IDLE


def main():
    app = ActivityService()
    app.run()
