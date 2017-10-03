from pathlib import Path

from marshmallow import Schema
from marshmallow.fields import Field, LocalDateTime, TimeDelta


class PathField(Field):
    def _deserialize(self, value, *args, **kwargs):
        return Path(value)

    def _serialize(self, value, *args, **kwargs):
        return str(value)


class EventMessage(Schema):
    datadir = PathField(required=True)
    eventdir = PathField(required=True)
    eventtime = LocalDateTime(required=True)
    duration = TimeDelta()
