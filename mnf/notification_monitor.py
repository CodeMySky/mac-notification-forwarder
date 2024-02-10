from abc import abstractmethod
import sched, time
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class BaseNotifcationMonitor:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_system_notifications(self, scheduler: sched.scheduler = None):
        pass


class MacNotificationMonitor(BaseNotifcationMonitor):

    def __init__(self):
        super().__init__()

    def check_system_notifications(self, scheduler: sched.scheduler = None):
        if scheduler is not None:
            scheduler.enter(1, 1, self.check_system_notifications, (scheduler,))
        logger.debug(f"Checking system notifications at {time.time()}")


def main():
    s = sched.scheduler(time.monotonic, time.sleep)
    monitor = MacNotificationMonitor()
    s.enter(0, 1, monitor.check_system_notifications, (s,))
    s.run()


if __name__ == "__main__":
    main()
