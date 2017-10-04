import datetime
from pathlib import Path

import zcam.schema.messages


class Event(object):
    schema = zcam.schema.messages.EventMessage(strict=True)

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

    def mkdir(self):
        self.eventdir.mkdir(parents=True, exist_ok=True)

    def exists(self):
        return self.eventdir.is_dir()

    def dump(self):
        data, errors = self.schema.dump(self)
        return data
