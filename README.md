## Putting things together

Everything communicates via the proxy service, so start that first:

   zcam-service-proxy

This will look for configuration in the `zcam.service.proxy` section of
the configuration file, unless you pass in an alternate `--instance`.
For example, `zcam-service-proxy --instance testing` will look for
config in the `zcam.service.proxy.testing` section.  An example
configuration file that would support both services might look like:

    [zcam.service.proxy]
    pub_bind_uri = tcp://localhost:8888
    sub_bind_uri = tcp://localhost:8889

    [zcam.service.proxy.testing]
    pub_bind_uri = tcp://localhost:7778
    sub_bind_uri = tcp://localhost:7779

Once the proxy is running, you can start adding sensors. Let's add a
couple of motion sensors:

    zcam-service-gpio --type motion --instance back
    zcam-service-gpio --type motion --instance front

The first will look for configuration values in the
`zcam.sensor.gpio.motion.front` section of the configuration file,
while the second will use `zcam.sensor.gpio.motion.back`. The first
will report messages tagged `zcam.sensor.gpio.motion.back` and the
second will tag messages `zcam.sensor.gpio.motion.front`.

A keypad device will look for configuration in `zcam.keypad`,
unless you provide an alternate `--instance`.  For example, to use
config in the `zcam.keypad.local` section:

    zcam-service-keypad --instance local

## Events

Events are published on the message bus as a pair of messages.  The
first is a topic (a byte string), and the second is a msgpack-encoded
dictionary.

All sensors (anything that reports messages using the `zcam.sensor`
namespace) publish a dictionary of the form:

    {'tags': {...any metadata...},
     'fields': {'value': somevalue}}

There may be zero or more tags and there may be more than one field.

There is no standard content for messages generated by other publishers.