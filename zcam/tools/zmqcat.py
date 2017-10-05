import argparse
import logging
import sys
import zmq

LOG = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--subscription', '-s',
                   action='append',
                   default=[])
    p.add_argument('uri')

    return p.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level='DEBUG')

    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)

    LOG.info('connecting to %s', args.uri)
    sub.connect(args.uri)

    if not args.subscription:
        args.subscription.append('')

    for topic in args.subscription:
        LOG.info('subscribing to %s', repr(topic))
        sub.subscribe(topic)

    while True:
        data = sub.recv()
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
