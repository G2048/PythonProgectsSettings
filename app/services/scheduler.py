import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import IntEnum

logger = logging.getLogger('stdout')


class Time(IntEnum):
    DAY = 86400
    HOUR = 3600
    MINUTE = 60
    SECOND = 1


class Job(ABC):
    @abstractmethod
    async def run(self):
        pass


class Scheduler:
    def __init__(self, hour: int, minute: int, time_frequency: Time, job: Job) -> None:
        # self.definer = definer
        self._frequency = time_frequency
        self._second_wakeup: timedelta = self.__start_date(hour, minute)
        self._hour = hour
        self._minute = minute
        self._job = job

    def _next_wakeup(self):
        start_date = datetime.now().replace(
            hour=self._hour, minute=self._minute, second=0, microsecond=0
        )
        next_start = start_date + timedelta(seconds=self._frequency)
        return timedelta(
            seconds=(next_start - datetime.now().replace(microsecond=0)).seconds
        )

    def __start_date(self, hour, minute):
        start_date = datetime.now().replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )
        delta = start_date - datetime.now().replace(microsecond=0)
        return timedelta(seconds=delta.seconds)

    async def start(self):
        # it is the start time
        logger.info(
            f'Start app in: {datetime.now() + self._second_wakeup}'  # noqa: E501
        )
        time.sleep(self._second_wakeup.seconds)
        # await asyncio.sleep(self._second_wakeup)
        while True:
            try:
                loop = asyncio.get_event_loop()
                # loop = asyncio.new_event_loop() if not loop.is_running()
                if not loop.is_running():
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(self._job.run())
                    loop.close()
                else:
                    # second_wakeup
                    await self._job.run()
            except Exception as e:
                logger.error(f'Something wrong for {self._job}: {e}')
            finally:
                self._second_wakeup = self._next_wakeup()
                logger.info(f'Next Wakeup: {datetime.now() + self._second_wakeup}')
                time.sleep(self._second_wakeup.seconds)
                # await asyncio.sleep(self._frequency)

    def stop(self):
        pass


class TestJob(Job):
    async def run(self):
        logger.info('job is running')
        print('job is running')


if __name__ == '__main__':
    HOUR = 14
    MINUTE = 57

    async def main():
        scheduler = Scheduler(HOUR, MINUTE, Time.MINUTE, TestJob())
        await scheduler.start()

    asyncio.run(main())
