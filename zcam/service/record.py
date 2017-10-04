import collections
import logging
import threading
import zmq

import zcam.app.zmq
import zcam.event
import zcam.schema.config

LOG = logging.getLogger(__name__)


class RecordService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.service.record'
    schema = zcam.schema.config.RecordSchema(strict=True)

    def prepare(self):
        super().prepare()

        self.buffer = collections.deque(maxlen=self.config['framebuffer'])
        self.lock = threading.Lock()
        self.recording = False

    def create_sockets(self):
        super().create_sockets()
        self.sub.subscribe('zcam.activity')

    def main(self):
        self.t_mon = threading.Thread(target=self.monitor, daemon=True)
        self.t_mon.start()

        while True:
            topic, message = self.receive_message()

            if topic == b'zcam.activity.start':
                self.start_recording()
            elif topic == b'zcam.activity.stop':
                self.stop_recording()
            else:
                LOG.error('received unexpected message %s', topic)

    def start_recording(self):
        if self.recording:
            LOG.error('request to start recording when already recording')

        self.event = zcam.event.Event(self.config['datadir'])
        self.recording = True
        self.t_rec = threading.Thread(target=self.record, args=(self.event,))
        self.t_rec.start()
        self.send_message('{}.recording.start'.format(self.name),
                          value=1,
                          event=self.event.dump())

    def stop_recording(self):
        if not self.recording:
            LOG.error('request to stop recording when not recording')
            return

        self.recording = False
        self.t_rec.join()
        self.event.end()
        self.send_message('{}.recording.stop'.format(self.name),
                          value=0,
                          event=self.event.dump())

    def camera(self):
        camera = self.socket(zmq.SUB)
        camera.subscribe('')
        camera.connect(self.config['hires_connect_uri'])

        return camera

    def monitor(self):
        camera = self.camera()

        while True:
            with self.lock:
                frame = camera.recv()
                self.buffer.append(frame)

    def record(self, event):
        camera = self.camera()

        event.mkdir()
        with self.lock, (event.eventdir / 'video.h264').open('wb') as fd:
            for frame in self.buffer:
                fd.write(frame)
            self.buffer.clear()
            while self.recording:
                frame = camera.recv()
                fd.write(frame)


def main():
    app = RecordService()
    app.run()
