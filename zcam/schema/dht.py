from marshmallow import post_load, pre_dump
from marshmallow.fields import String, Integer
from marshmallow.validate import OneOf

import Adafruit_DHT

from zcam.schema.config import PinSchema

DHT_MODEL_IN = {
    'dht22': Adafruit_DHT.DHT22,
    'dht11': Adafruit_DHT.DHT11,
    'am2302': Adafruit_DHT.AM2302,
}

DHT_MODEL_OUT = {v: k for k, v in DHT_MODEL_IN.items()}


class DhtSchema(PinSchema):
    model = String(
        missing='dht22',
        validate=OneOf(['dht22', 'dht11']))
    interval = Integer(missing=30)

    @post_load
    def transform_dht_model_in(self, data):
        data['model'] = DHT_MODEL_IN[data['model']]

    @pre_dump
    def transform_dht_model_out(self, data):
        data['model'] = DHT_MODEL_OUT[data['model']]
