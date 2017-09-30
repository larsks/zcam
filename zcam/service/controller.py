import logging

import zcam.app.zmq
import zcam.schema.config

LOG = logging.getLogger(__name__)


class ControllerService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.service.controller'
    schema = zcam.schema.config.ControllerSchema(strict=True)

    def prepare(self):
        super().prepare()
        self.passcode = self.config.get('passcode')
        self.passcode_instance = self.config.get('passcode_instance')
        self.armed = False
        self.active = False

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

        while True:
            topic, msg = self.receive_message()

            if topic.startswith(b'zcam.service.activity'):
                self.handle_activity(topic, msg)
            elif topic.startswith(b'zcam.device.passcode'):
                self.handle_passcode_attempt(topic, msg)
            elif topic.startswith(b'zcam.sensor.button.btn_arm'):
                self.handle_arm_button(topic, msg)

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
            LOG.warning('armed')

    def disarm(self):
        if self.armed:
            self.armed = False
            self.send_message('zcam.disarm')
            LOG.warning('disarmed')


def main():
    app = ControllerService()
    app.run()
