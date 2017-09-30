import json
import logging
from pathlib import Path
import rpi_pwm

import zcam.app.zmq
import zcam.schema.config
import zcam.tunes

LOG = logging.getLogger(__name__)


class ControllerService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.service.controller'
    schema = zcam.schema.config.ControllerSchema(strict=True)

    def prepare(self):
        super().prepare()
        self.passcode = self.config.get('passcode')
        self.passcode_instance = self.config.get('passcode_instance')
        self.arm_on_start = self.config.get('arm')
        self.statefile = self.config.get('statefile')
        if self.statefile:
            self.statefile = Path(self.statefile).expanduser()

        self.armed = False
        self.active = False

        buzzer_pwm = self.config.get('buzzer_pwm')
        if buzzer_pwm:
            self.buzzer = rpi_pwm.PWM(*buzzer_pwm.split(':'))
        else:
            self.buzzer = None

        self.load_state()

    def load_state(self):
        if not self.statefile:
            return

        try:
            with self.statefile.open('r') as fd:
                state = json.load(fd)
                if state.get('armed'):
                    self.arm_on_start = True
        except FileNotFoundError:
            pass

    def save_state(self):
        if not self.statefile:
            return

        with self.statefile.open('w') as fd:
            state = dict(armed=self.armed)
            json.dump(state, fd)

    def main(self):
        self.sub.subscribe('zcam.service.activity')
        self.sub.subscribe('zcam.sensor.button.btn_arm')

        if self.passcode_instance:
            LOG.info('listening for passcodes from %s', self.passcode_instance)
            self.sub.subscribe('zcam.device.passcode.{}'.format(
                self.passcode_instance))
        else:
            LOG.info('listening for all passcodes')
            self.sub.subscribe('zcam.device.passcode')

        if self.arm_on_start:
            self.arm()

        while True:
            topic, msg = self.receive_message()

            if topic.startswith(b'zcam.service.activity'):
                self.handle_activity(topic, msg)
            elif topic.startswith(b'zcam.device.passcode'):
                self.handle_passcode_attempt(topic, msg)
            elif topic.startswith(b'zcam.sensor.button.btn_arm'):
                self.handle_arm_button(topic, msg)

    def play(self, tune):
        if not self.buzzer:
            return

        tune = getattr(zcam.tunes, 'TUNE_{}'.format(tune.upper()), None)
        if not tune:
            return

        self.buzzer.play(tune)

    def handle_activity(self, topic, message):
        if not self.armed:
            return

        if message[b'value'] and not self.active:
            LOG.info('start recording activity')
            self.active = True
        elif self.active:
            LOG.info('stop recording activity')
            self.active = False

    def handle_passcode_attempt(self, topic, message):
        if not self.passcode:
            return

        if self.passcode == message[b'passcode'].decode('utf8'):
            LOG.info('received correct passcode')
            self.toggle_armed()
        else:
            self.play('error')
            LOG.error('received incorrect passcode')

    def handle_arm_button(self, topic, message):
        if message[b'value']:
            self.arm()

    def toggle_armed(self):
        if self.armed:
            self.disarm()
        else:
            self.arm()

    def arm(self):
        if not self.armed:
            self.armed = True
            self.send_message('zcam.arm')
            self.save_state()
            self.play('armed')
            LOG.warning('armed')

    def disarm(self):
        if self.armed:
            self.armed = False
            self.send_message('zcam.disarm')
            self.save_state()
            self.play('disarmed')
            LOG.warning('disarmed')


def main():
    app = ControllerService()
    app.run()
