import logging
import sched
from sys import argv
import time
from mnf.notificaiton_router import NotificationRouter

from mnf.notification_monitor import MacNotificationMonitor
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--config", "-c", default="config.yaml", type=str, help="Path to config file"
)
parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")


def main(argv):
    args = parser.parse_args(argv[1:])
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    s = sched.scheduler(time.monotonic, time.sleep)
    notification_router = NotificationRouter(args.config)
    monitor = MacNotificationMonitor(notification_router=notification_router)
    s.enter(0, 1, monitor.check_system_notifications, (s,))
    s.run()


if __name__ == "__main__":
    main(argv)
