import zcam.service.gpio


class ButtonService(zcam.service.gpio.GpioService):
    namespace = 'zcam.sensor.button'
    default_bouncetime = 100
    default_pull = 'down'


def main():
    app = ButtonService()
    app.run()
