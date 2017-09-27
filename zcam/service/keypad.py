import evdev
import logging

import zcam.app

LOG = logging.getLogger(__name__)
KEY_STATES = ['up', 'down', 'hold']


def is_keypad(device):
    return (evdev.ecodes.KEY_KP1
            in device.capabilities()[evdev.ecodes.EV_KEY])


def lookup_device(name):
    LOG.debug('looking for input device "%s"', name)
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    for dev in devices:
        if dev.name == name and is_keypad(dev):
            return dev


class KeypadService(zcam.app.ZmqClientApp):

    def create_parser(self):
        p = super().create_parser()
        p.add_argument('--device')
        p.add_argument('--device-name')
        p.add_argument('name')
        return p

    def create_overrides(self):
        return super().create_overrides() + [
            ('device', self.name,
             '{}_device'.format(self.args.name)),
            ('device_name', self.name,
             '{}_device_name'.format(self.args.name)),
        ]

    def main(self):
        device = self.config.get(
            self.name,
            '{}_device'.format(self.args.name),
            fallback=None)

        if device is None:
            device_name = self.config.get(
                self.name,
                '{}_device_name'.format(self.args.name),
                fallback=None)
            device = lookup_device(device_name)

        if device is None:
            device = '/dev/input/event0'

        keypad = evdev.InputDevice(device)
        keypad.grab()

        LOG.info('starting keypad %s on device %s',
                 self.args.name, device)

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
            }

            LOG.debug('keypad %s on device %s event %s',
                      self.args.name,
                      device,
                      event)

            self.send_message(
                'keypad.{}.{}'.format(self.args.name, key.keycode),
                **eventdict)


def main():
    app = KeypadService()
    app.run()
