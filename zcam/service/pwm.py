import logging
import time

from pathlib import Path

import zcam.app.zmq

LOG = logging.getLogger(__name__)

default_pwm = '/sys/class/pwm/pwmchip0/pwm0'


class PwmService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.device.pwm'

    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--pwm')
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            'pwm',
        ]

    def main(self):
        self.pwm = Path(self.get('pwm'))
        if not self.pwm.is_dir():
            raise ValueError('invalid pwm path')

        self.sub.subscribe('{}.play'.format(self.name))

        while True:
            topic, msg = self.receive_message()
            if b'tune' in msg:
                self.play(msg[b'tune'])

    def play_tone(self, freq, duration):
        '''Play a single tone using pwm'''
        freq, duration = float(freq), float(duration)
        LOG.debug('play %f for %f seconds', freq, duration)

        if freq == 0:
            time.sleep(duration)
            return

        self.set_frequency(freq)

        try:
            self.enable_output()
            time.sleep(duration)
        finally:
            self.disable_output()

    def enable_output(self):
        '''Enable pwm output'''

        with (self.pwm / 'enable').open('wb') as fd:
            fd.write(b'1\n')

    def disable_output(self):
        '''Disable pwm output'''
        with (self.pwm / 'enable').open('wb') as fd:
            fd.write(b'0\n')

    def set_period(self, period, duty_cycle=0.5):
        '''Set pwm period (specified in ns)'''
        LOG.debug('set_period period=%s, duty_cycle=%s',
                  period, duty_cycle)

        period_bytes = bytes('%s' % int(period), 'ascii')

        try:
            # try to reset duty_cycle, but ignore any errors (which
            # probably mean both period and duty_cycle were already
            # 0)
            self.set_duty_cycle(0, 0)
        except OSError:
            pass

        with (self.pwm / 'period').open('wb') as fd:
            fd.write(period_bytes)
        self.set_duty_cycle(period, duty_cycle)

    def set_duty_cycle(self, period, duty_cycle=0.5):
        LOG.debug('set_duty_cycle period=%s, duty_cycle=%s',
                  period, duty_cycle)

        if duty_cycle > 1 or duty_cycle < 0:
            raise ValueError('0 <= duty_cycle <= 1')

        duty_cycle = duty_cycle * period
        duty_cycle_bytes = bytes('%s' % int(duty_cycle), 'ascii')
        with (self.pwm / 'duty_cycle').open('wb') as fd:
            fd.write(duty_cycle_bytes)

    def set_frequency(self, freq, **kwargs):
        '''Convert a frequency in Hz to a period in ns'''

        period = (1.0 / freq) * 1e+9
        self.set_period(period, **kwargs)

    def play(self, tune):
        LOG.debug('play tune %s', tune)
        for freq, duration in tune:
            freq = float(freq)
            duration = float(duration)
            self.play_tone(freq, duration)


def main():
    app = PwmService()
    app.run()
