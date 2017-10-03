import datetime
import json
import logging
from pathlib import Path
import picamera

import zcam.app.zmq
import zcam.schema.config
import zcam.schema.messages

LOG = logging.getLogger(__name__)


class Event(object):

    def __init__(self, datadir, eventtime=None):
        if eventtime is None:
            eventtime = datetime.datetime.now()

        self.datadir = Path(datadir)
        self.eventtime = eventtime
        self.eventdir = (
            self.datadir / 'events' /
            eventtime.strftime('%y-%m-%d') /
            eventtime.strftime('%H:%M:%S')
        )

        def __str__(self):
            return str(self.eventtime)

    def end(self):
        self.duration = datetime.datetime.now() - self.eventtime


class CameraService(zcam.app.zmq.ZmqClientApp):
    namespace = 'zcam.service.camera'
    schema = zcam.schema.config.CameraSchema(strict=True)
    eventmessage = zcam.schema.messages.EventMessage(strict=True)

    def prepare(self):
        super().prepare()
        self.camera = picamera.PiCamera(
            resolution=(self.config['res_x'], self.config['res_y']),
            framerate=self.config['framerate'],
        )

        self.camera.hflip = self.config['flip_x']
        self.camera.vflip = self.config['flip_y']
        self.interval = self.config['interval']
        self.lead_time = self.config['lead_time']
        self.datadir = Path(self.config['datadir'])
        self.recording = False

        self.stream = picamera.PiCameraCircularIO(
            self.camera, seconds=self.lead_time)

    def main(self):
        self.sub.subscribe('zcam.activity')
        self.camera.start_recording(self.stream, format='h264')

        while True:
            topic, msg = self.receive_message()

            if topic == b'zcam.activity.start':
                self.start_event()
            elif topic == b'zcam.activity.stop':
                self.stop_event()
            else:
                LOG.error('received unexpected message %s', topic)

    def cleanup(self):
        self.camera.stop_recording()
        super().cleanup()

    def start_event(self):
        if self.recording:
            LOG.error('request to record when already recording')
            return

        self.event = Event(self.datadir)
        videopath = self.event.eventdir / 'video.h264'
        self.event.eventdir.mkdir(parents=True, exist_ok=True)
        event, errors = self.eventmessage.dump(self.event)

        LOG.info('start recording event %s', self.event)
        self.recording = True
        self.vidfd = videopath.open('wb')
        self.stream.copy_to(self.vidfd)
        self.camera.split_recording(self.vidfd)
        self.send_message('{}.recording.start'.format(self.name),
                          event=event)

    def stop_event(self):
        if not self.recording:
            LOG.error('request to stop recording when not recording')
            return

        LOG.info('stop recording event %s', self.event)
        self.recording = False
        self.stream.seek(0)
        self.stream.truncate()
        self.camera.split_recording(self.stream)
        self.vidfd.close()

        self.event.end()
        event, errors = self.eventmessage.dump(self.event)
        with (self.event.eventdir / 'event.json').open('w') as fd:
            json.dump(event, fd, indent=2)

        self.send_message('{}.recording.stop'.format(self.name),
                          event=event)


def main():
    app = CameraService()
    app.run()
