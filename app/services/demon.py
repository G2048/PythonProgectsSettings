import argparse
import atexit
import logging.config
import os
import signal
import sys
import time

from app.configs.log_settings import LogConfig

logger = logging.getLogger('stdout')


class Daemon:
    """Class for Creating and maintaining Demon process"""

    def __init__(self, filename):
        self.pidfile = f'/var/lock/{filename}d'
        self.stdin = '/dev/null'
        self.stdout = '/dev/null'
        self.stderr = '/dev/null'

    async def demonification(self):
        """Fork, magic and run the function"""
        self.create_child()
        os.chdir('/')
        os.setsid()
        os.umask(0)
        self.create_child()
        pid = str(os.getpid())
        logger.info(f'Demon was created! Pid is: {pid}')
        open(self.pidfile, 'w').write(pid)
        logger.debug(f'{self.pidfile}')
        atexit.register(self.delpid)
        signal.signal(signal.SIGCHLD, self.handle_signal)

        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin)
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        logger.debug(f'Start function {self.fn}')
        # loop = asyncio.new_event_loop()
        # await loop.create_task(self.fn(*self.fn_args))
        # asyncio.set_event_loop(loop)
        # await asyncio.gather(self.fn, *self.fn_args)
        await self.fn(*self.fn_args)

    def delpid(self):
        """Only remove pidfile"""
        try:
            os.remove(self.pidfile)
        except FileNotFoundError as e:
            logger.error(e)
            sys.stderr.write(f'{e}\n')

    @staticmethod
    def handle_signal(signum, frame):
        pass

    @staticmethod
    def create_child():
        try:
            pid = os.fork()
            if pid:
                sys.exit(0)
        except OSError as e:
            logger.error('Create daemon is failed!')
            logger.error(f'Error: {e.errno} {e.strerror}')
            sys.stderr.write('Create daemon is failed!\n')
            sys.stderr.write(f'Error: {e.errno} {e.strerror}\n')
            sys.exit(1)

    async def start(self, fn, *args):
        """You must specify a function to be called when the daemon is started"""

        self.fn = fn
        self.fn_args = args
        if os.path.exists(self.pidfile):
            logger.warning(f'{self.pidfile} already exists. Daemon is already running!')
            sys.stderr.write(
                f'{self.pidfile} already exists. Daemon is already running!\n'
            )
            self.stop()
        else:
            logger.debug(self.fn_args)
            await self.demonification()

    def stop(self):
        """Stop the existing daemon"""

        if os.path.exists(self.pidfile):
            try:
                pid = int(open(self.pidfile).read())
            except OSError as e:
                logger.error(f'Error: {e}')
                sys.stderr.write(f'Error: {e}\n')
                sys.exit(1)
        else:
            logger.warning(f"Pid file {self.pidfile} don't exist!")
            sys.stderr.write(f"Pid file {self.pidfile} don't exist!\n")
            return -1

        try:
            os.kill(pid, 15)
            logger.warning(f'Daemon with pid {pid} was terminated!')
            sys.stdout.write(f'Daemon with pid {pid} was terminated!\n')
            self.delpid()
        except OSError as e:
            os.kill(pid, 9)
            logger.warning(f'Send kill -9 to process {pid}')
            sys.stderr.write(f'Error {pid}\n')
            sys.stderr.write(f'Send kill -9 to process {pid}\n')
            self.delpid()
            sys.exit(1)
        finally:
            if os.path.exists(f'/proc/{pid}'):
                os.kill(pid, 9)
                logger.warning(f'Send kill -9 to process {pid}')
                sys.stderr.write(f'Send kill -9 to process {pid}\n')


def cmd_parser():
    RAWHELP = """Create and manipulating the Daemon process.\n
    Test running: sudo python3 daemon.py -d
    Test kill: sudo python3 daemon.py -k
    Watch daemon from log: tail -f testd.log
    File lock: /var/lock/reviewbi.lock",
    """
    parser = argparse.ArgumentParser(
        description=RAWHELP, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.description = 'Simple service for reviewbi service'
    parser.epilog = ''

    parser.add_argument('-h', '--hour', action='store', type=int, default=7)
    parser.add_argument('-m', '--minute', action='store', type=int, default=0)

    exgroup = parser.add_mutually_exclusive_group(required=True)
    exgroup.add_argument(
        '-u', '--start', action='store_true', help='Start a reviewbi service'
    )
    exgroup.add_argument(
        '-s',
        '--stop',
        action='store_true',
        help='Stop a reviewbi service',
    )
    exgroup.add_argument('-r', '--restart', action='store_true', help='Restart')
    return parser.parse_args()


if __name__ == '__main__':
    args = cmd_parser()

    logging.config.dictConfig(LogConfig)

    def handle_signal(signum, frame):
        logger.info(f'Signal {signum} is handling!')

    class Test:
        async def testd(self):
            while True:
                with open('/var/log/testd.log', 'a+') as f:
                    f.write('Daemon is running!\n')
                logger.info('Daemon is running!')
                time.sleep(5)

    signal.signal(15, handle_signal)
    demon = Daemon('testd')
    test_class = Test()
    testd = test_class.testd

    import asyncio

    async def main():
        if args.daemonize:
            await demon.start(testd)
        else:
            demon.stop()

    asyncio.run(main())
