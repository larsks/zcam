from marshmallow import post_load, pre_dump
from marshmallow.fields import String, Integer
from marshmallow.validate import Regexp, OneOf
from RPi import GPIO

from zcam.schema.config import PinSchema

GPIO_EDGE_IN = {
    'falling': GPIO.FALLING,
    'rising': GPIO.RISING,
    'both': GPIO.BOTH,
}

GPIO_EDGE_OUT = {v: k for k, v in GPIO_EDGE_IN.items()}

GPIO_PUD_IN = {
    'up': GPIO.PUD_UP,
    'down': GPIO.PUD_DOWN,
    'off': GPIO.PUD_OFF,
}

GPIO_PUD_OUT = {v: k for k, v in GPIO_PUD_IN.items()}


class GpioSchema(PinSchema):
    edge = String(
        missing='both',
        validate=OneOf(['rising', 'falling', 'both']))
    pull = String(
        missing='off',
        validate=OneOf(['up', 'down', 'off']))
    bouncetime = Integer()
    timeout = Integer()
    pub_bind_uri = String(
        validate=Regexp(r'tcp://[^:]+:\d+'))

    @post_load
    def transform_gpio_constants_in(self, data):
        data['pull'] = GPIO_PUD_IN[data['pull']]
        data['edge'] = GPIO_EDGE_IN[data['edge']]

    @pre_dump
    def transform_gpio_constants_out(self, data):
        data['pull'] = GPIO_PUD_OUT[data['pull']]
        data['edge'] = GPIO_EDGE_OUT[data['edge']]


class ButtonSchema(GpioSchema):
    bouncetime = Integer(missing=100)
    pull = String(
        missing='down',
        validate=OneOf(['up', 'down', 'off']))
