import argparse
import sys
import zmq


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--subscription', '-s',
                   action='append',
                   default=[])
    p.add_argument('uri')

    return p.parse_args()


def main():
    args = parse_args()
    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)

    if not args.subscription:
        args.subscription.append('')

    for topic in args.subscription:
        sub.subscribe(topic)

    sys.stdout.buffer.write(sub.recv())
