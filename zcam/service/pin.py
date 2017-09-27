from collections import defaultdict
import logging
import time

import zcam.app.zmq

LOG = logging.getLogger(__name__)
KEYMAP = {
    b'KEY_0': '0',
    b'KEY_1': '1',
    b'KEY_2': '2',
    b'KEY_3': '3',
    b'KEY_4': '4',
    b'KEY_5': '5',
    b'KEY_6': '6',
    b'KEY_7': '7',
    b'KEY_8': '8',
    b'KEY_9': '9',
    b'KEY_KP0': '0',
    b'KEY_KP1': '1',
    b'KEY_KP2': '2',
    b'KEY_KP3': '3',
    b'KEY_KP4': '4',
    b'KEY_KP5': '5',
    b'KEY_KP6': '6',
    b'KEY_KP7': '7',
    b'KEY_KP8': '8',
    b'KEY_KP9': '9',
    b'KEY_KPENTER': '\n',
    b'KEY_ENTER': '\n',
}

default_timeout = 10


class ExpiringBuffer(object):
    def __init__(self, timeout):
        self.last = time.time()
        self.timeout = timeout
        self.acc = []

    def append(self, c):
        now = time.time()
        if now - self.last > self.timeout:
            LOG.info('clearing buffer due to timeout (%d)',
                     self.timeout)
            self.acc = []

        self.acc.append(c)
        self.last = now

    def getvalue(self):
        return ''.join(self.acc)

    def clear(self):
        self.acc = []

    def __str__(self):
        return self.getvalue()


class PinService(zcam.app.zmq.ZmqClientApp):
    '''Receive keystrokes from keypads and assemble them into PINs.

    A PIN is sent to the message bus when the ENTER key on a keypad
    is pressed.
    '''

    namespace = 'zcam.device.pin'

    def __init__(self, **kwargs):
        self.pads = defaultdict(self.buffermaker)
        self.timeout = default_timeout
        super().__init__(**kwargs)

    def buffermaker(self):
        return ExpiringBuffer(self.timeout)

    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--keypad')
        p.add_argument('--timeout')
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            'keypad', 'timeout',
        ]

    def main(self):
        keypad = self.get('keypad', None)
        self.timeout = self.get('timeout', default_timeout)

        if keypad:
            LOG.debug('listening for messages from keypad instance %s',
                      keypad)
            self.sub.subscribe('zcam.device.keypad.{}'.format(keypad))
        else:
            LOG.debug('listening for messages from all keypads')
            self.sub.subscribe('zcam.device.keypad'.format(keypad))

        while True:
            tag, msg = self.receive_message()

            if msg[b'keycode'] not in KEYMAP:
                continue

            if msg[b'keystate'] != b'up':
                continue

            LOG.debug('pin service %s received message %s',
                      self.name, tag)

            key = KEYMAP[msg[b'keycode']]
            keypad = msg[b'instance']
            if key == '\n':
                self.handle_pin(keypad)
            else:
                self.pads[keypad].append(key)

    def handle_pin(self, keypad):
        pin = str(self.pads[keypad])
        self.pads[keypad].clear()
        LOG.debug('pin service %s sending pin %s',
                  self.name, repr(pin))
        self.send_message('{}'.format(self.name),
                          keypad=keypad,
                          pin=pin)


def main():
    app = PinService()
    app.run()
