from setuptools import setup, find_packages

setup(
    name='zcam',
    version='0.1',
    author='Lars Kellogg-Stedman',
    author_email='lars@oddbit.com',
    url='https://github.com/larsks/zcam',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'zcam-service-activity = zcam.service.activity:main',
            'zcam-service-button = zcam.service.button:main',
            'zcam-service-camera = zcam.service.camera:main',
            'zcam-service-controller = zcam.service.controller:main',
            'zcam-service-dht = zcam.service.dht:main',
            'zcam-service-gpio = zcam.service.gpio:main',
            'zcam-service-heartbeat = zcam.service.heartbeat:main',
            'zcam-service-keypad = zcam.service.keypad:main',
            'zcam-service-led = zcam.service.led:main',
            'zcam-service-messages = zcam.service.messages:main',
            'zcam-service-metrics = zcam.service.metrics:main',
            'zcam-service-motion = zcam.service.motion:main',
            'zcam-service-passcode = zcam.service.passcode:main',
            'zcam-service-proxy = zcam.service.proxy:main',
            'zcam-service-record = zcam.service.record:main',
            'zcam-sendmessage = zcam.tools.sendmessage:main',

            'zmqcat = zcam.tools.zmqcat:main',
            'zmqone = zcam.tools.zmqone:main',
        ],
    }
)
