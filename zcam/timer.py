import datetime
import logging
import threading
import time

LOG = logging.getLogger(__name__)


class TickingTimer(threading.Thread):
    '''A timer that ticks.

    Call a function after wait_interval seconds.  Call a second
    function every tick_interval seconds.
    '''

    def __init__(self,
                 tick_interval, tick_callback,
                 wait_interval, wait_callback,
                 args=None, kwargs=None,
                 tick_args=None, tick_kwargs=None,
                 stopflag=None):
        if (tick_interval >= wait_interval):
            raise ValueError('tick_interval must be smaller '
                             'than wait_interval')
        super().__init__(daemon=True)
        self.tick_interval = tick_interval
        self.tick_callback = tick_callback
        self.tick_args = tick_args if tick_args else []
        self.tick_kwargs = tick_kwargs if tick_kwargs else {}
        self.wait_interval = wait_interval
        self.wait_callback = wait_callback
        self.args = args if args else []
        self.kwargs = kwargs if kwargs else {}

        self.stopflag = stopflag if stopflag else threading.Event()

    def cancel(self):
        self.stopflag.set()

    def run(self):
        time_start = time.time()
        while True:
            now = time.time()
            delta = now - time_start
            if delta >= self.wait_interval:
                break

            self.tick_callback(*self.tick_args, **self.tick_kwargs)
            sleeptime = min((self.wait_interval - delta), self.tick_interval)
            if self.stopflag.wait(sleeptime):
                return

        self.wait_callback(*self.args, **self.kwargs)


class DynamicTimer(threading.Thread):

    '''Call a function after a specified interval.

    The extend method
    can be used to extend the interval while the timer is running.
    '''

    def __init__(self, interval, function,
                 limit=None,
                 stopflag=None,
                 args=None,
                 kwargs=None):
        super().__init__(daemon=True)
        self.function = function
        self.interval = interval
        self.limit = limit
        self.started_at = None
        self.expires_at = None
        self.args = args if args else []
        self.kwargs = kwargs if kwargs else {}

        self.stopflag = stopflag if stopflag else threading.Event()

    def cancel(self):
        self.stopflag.set()

    def run(self):
        now = time.time()

        self.started_at = now
        self.expires_at = now + self.interval
        if self.limit:
            self.expires_limit = now + self.limit

        LOG.debug('started timer %s', self)

        while True:
            sleeptime = self.expires_at - time.time()
            if self.stopflag.wait(sleeptime):
                LOG.info('stopping timer %s', self)
                return

            now = time.time()
            if now >= self.expires_at:
                LOG.debug('timer %s expired', self)
                break

            if self.limit and now >= self.expires_limit:
                LOG.debug('timer %s reached limit', self)
                break

        self.function(*self.args, **self.kwargs)

    def extend(self, extra):
        if not self.is_alive():
            raise ValueError('attempt to extend idle timer')

        self.expires_at = max(self.expires_at,
                              time.time() + extra)
        LOG.debug('extended timer %s', self)

    def __str__(self):
        if self.expires_at is None:
            when = 'not started'
        else:
            when = time.strftime('%Y-%m-%d %H:%M:%S',
                                 time.localtime(self.expires_at))

        return '<DynamicTimer %s>' % (when,)


class StopWatch(object):
    def start(self):
        self.time_start = datetime.datetime.now()
        self.delta = 0
        LOG.debug('started stopwatch @ %s', self.time_start)

    def stop(self):
        delta = datetime.datetime.now() - self.time_start
        delta_seconds = delta.total_seconds()
        LOG.debug('stopped stopwatch after %f', delta_seconds)
        self.delta = delta
        return delta

    def reset(self):
        self.delta = 0
