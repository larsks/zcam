import evdev
import logging

import zcam.app.zmq
import zcam.schema.config

LOG = logging.getLogger(__name__)
KEY_STATES = ['up', 'down', 'hold']


def lookup_device(name):
    '''Look for an input device by name.

    This may fail if you have a multifunction input device that
    reports itself as, e.g., both a keyboard and a mouse.
    '''

    LOG.debug('looking for input device "%s"', name)
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    for dev in devices:
        if dev.name == name:
            LOG.debug('found input device "%s"', dev.fn)
            return dev


class KeypadService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.device.keypad'
    schema = zcam.schema.config.KeypadSchema(strict=True)

    def main(self):
        device = self.config.get('device')
        device_name = self.config.get('device_name')

        if device is None and device_name:
            device = lookup_device(device_name)

        if device is None:
            raise ValueError('unable to find a keypad')

        keypad = evdev.InputDevice(device)

        if self.config.get('grab'):
            LOG.info('grabbing device %s', device)
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
