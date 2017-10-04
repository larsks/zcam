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
    loglevels = List(String())


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


class ActivitySchema(BaseSchema):
    interval = Integer(missing=10)
    extend = Integer(missing=10)
    limit = Integer(missing=120)
    cooldown = Integer(missing=30)


class MessagesSchema(BaseSchema):
    subscription = List(String())


class LedSchema(PinSchema):
    subscription = String(required=True)


class ControllerSchema(BaseSchema):
    passcode = String()
    passcode_instance = String()
    arm = Boolean(missing=False)
    statefile = String()
    buzzer_pwm = String(missing='pwmchip0:0')
    arm_hotkey = String(
        validate=Regexp('([^:]+:)?KEY_.*'))


class PathSchema(BaseSchema):
    datadir = String(missing='.')


class CameraSchema(PathSchema):
    res_hi_x = Integer(missing=800)
    res_hi_y = Integer(missing=600)
    res_lo_x = Integer(missing=320)
    res_lo_y = Integer(missing=240)
    res_image_x = Integer(missing=800)
    res_image_y = Integer(missing=600)
    framerate = Integer(missing=30)
    flip_x = Boolean(missing=False)
    flip_y = Boolean(missing=False)
    image_interval = Integer(missing=2)

    hires_bind_uri = String(
        missing='tcp://*:7710',
        validate=Regexp('^tcp://[^:]+:\d+'))
    lores_bind_uri = String(
        missing='tcp://*:7711',
        validate=Regexp('^tcp://[^:]+:\d+'))
    image_bind_uri = String(
        missing='tcp://*:7711',
        validate=Regexp('^tcp://[^:]+:\d+'))
