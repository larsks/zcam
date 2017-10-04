import logging
import picamera
import time
import zmq

import zcam.app.zmq
import zcam.schema.config

LOG = logging.getLogger(__name__)


class Writer(object):

    def __init__(self, sock):
        self.sock = sock

    def write(self, data):
        self.sock.send(data)


class CameraService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.service.camera'
    schema = zcam.schema.config.CameraSchema(strict=True)
    eventmessage = zcam.schema.messages.EventMessage(strict=True)

    def prepare(self):
        super().prepare()
        self.camera = picamera.PiCamera(
            resolution=(self.config['res_hi_x'], self.config['res_hi_y']),
            framerate=self.config['framerate'],
        )

        self.camera.hflip = self.config['flip_x']
        self.camera.vflip = self.config['flip_y']
        self.res_lo_x = self.config['res_lo_x']
        self.res_lo_y = self.config['res_lo_y']
        self.res_image_x = self.config['res_image_x']
        self.res_image_y = self.config['res_image_y']
        self.image_interval = self.config['image_interval']

        self.hires = self.socket(zmq.PUB)
        self.lores = self.socket(zmq.PUB)
        self.image = self.socket(zmq.PUB)

    def main(self):
        self.hires.bind(self.config['hires_bind_uri'])
        self.lores.bind(self.config['lores_bind_uri'])
        self.image.bind(self.config['image_bind_uri'])

        self.camera.start_recording(Writer(self.hires),
                                    format='h264')
        self.camera.start_recording(Writer(self.lores),
                                    format='h264',
                                    splitter_port=2,
                                    resize=(self.res_lo_x, self.res_lo_y))

        for x in self.camera.capture_continuous(Writer(self.image),
                                                use_video_port=True):
            time.sleep(self.image_interval)


def main():
    app = CameraService()
    app.run()
