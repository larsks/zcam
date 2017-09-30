from marshmallow import Schema, validates_schema, ValidationError
from marshmallow.fields import String, Integer, Boolean, List
from marshmallow.validate import Regexp


class BaseSchema(Schema):
    pub_connect_uri = String(
        missing='tcp://127.0.0.1:7700',
        validate=Regexp('^tcp://[^:]+:\d+'))
    sub_connect_uri = String(
        missing='tcp://127.0.0.1:7701',
        validate=Regexp('^tcp://[^:]+:\d+'))


class PathSchema(BaseSchema):
    datadir = String(missing='.')


class PinSchema(BaseSchema):
    pin = Integer(required=True)


class ProxySchema(BaseSchema):
    pub_bind_uri = String(
        required=True,
        missing='tcp://127.0.0.1:7700',
        validate=Regexp('^tcp://[^:]+:\d+'))
    sub_bind_uri = String(
        required=True,
        missing='tcp://127.0.0.1:7701',
        validate=Regexp('^tcp://[^:]+:\d+'))


class KeypadSchema(BaseSchema):
    device = String()
    device_name = String()
    grab = Boolean(missing=True)

    @validates_schema
    def validate_device(self, data):
        if all(data.get(option) is None
               for option in ['device', 'device_name']):
            raise ValidationError('you must provide device '
                                  'or device_name')


class PasscodeSchema(BaseSchema):
    keypad_instance = String()
    timeout = Integer(missing=10)


class MetricsSchema(BaseSchema):
    host = String(missing='localhost')
    port = Integer(missing=8086)
    database = String(required=True)


class CameraSchema(PathSchema):
    res_x = Integer(missing=800)
    res_y = Integer(missing=600)
    flip_x = Boolean(missing=False)
    flip_y = Boolean(missing=False)
    lead_time = Integer(missing=5)
    interval = Integer(missing=2)


class ActivitySchema(BaseSchema):
    interval = Integer(missing=10)
    extend = Integer(missing=10)
    limit = Integer(missing=120)
    cooldown = Integer(missing=30)


class MessagesSchema(BaseSchema):
    subscription = List(String)
