import evdev
import logging

import zcam.app.zmq

LOG = logging.getLogger(__name__)
KEY_STATES = ['up', 'down', 'hold']

default_device = '/dev/input/event0'


def is_keypad(device):
    return (evdev.ecodes.KEY_KP1
            in device.capabilities()[evdev.ecodes.EV_KEY])


def lookup_device(name):
    LOG.debug('looking for input device "%s"', name)
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    for dev in devices:
        if dev.name == name and is_keypad(dev):
            return dev


class KeypadService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.device.keypad'

    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--device')
        p.add_argument('--device-name')
        p.add_argument('--no-grab', '-n',
                       action='store_true')
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            'device', 'device_name'
        ]

    def main(self):
        device = self.get('device', None)
        device_name = self.get('device', None)

        if device is None and device_name:
            device = lookup_device(device_name)

        if device is None:
            device = default_device

        keypad = evdev.InputDevice(device)

        if not self.args.no_grab:
            keypad.grab()

        LOG.info('starting keypad %s on device %s',
                 self.name, device)

        for event in keypad.read_loop():
            if event.type != evdev.ecodes.EV_KEY:
                continue

            key = evdev.categorize(event)
            eventdict = {
                'timestamp': event.timestamp(),
                'usec': event.usec,
                'keystate': KEY_STATES[key.keystate],
                'keycode': key.keycode,
                'value': event.value,
                'device': device,
                'instance': self.args.instance,
            }

            LOG.debug('keypad %s on device %s event %s',
                      self.name,
                      device,
                      eventdict)

            self.send_message(
                '{}.key.{}'.format(self.name, key.keycode),
                **eventdict)


def main():
    app = KeypadService()
    app.run()
