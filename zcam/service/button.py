import zcam.schema.gpio
import zcam.service.gpio


class ButtonService(zcam.service.gpio.GpioService):
    namespace = 'zcam.sensor.button'
    schema = zcam.schema.gpio.ButtonSchema(strict=True)


def main():
    app = ButtonService()
    app.run()
