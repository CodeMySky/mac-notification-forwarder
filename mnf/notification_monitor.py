from abc import abstractmethod
import os
import plistlib
import sched, time
import sqlite3
import subprocess
import logging
from typing import Any, Dict, List
from mnf.notificaiton_router import NotificationRouter
from mnf.notification import Notification

logger = logging.getLogger(__name__)


class BaseNotifcationMonitor:
    def __init__(self, notification_router: NotificationRouter) -> None:
        self.notification_router = notification_router
        logger.info("Monitor started")

    @abstractmethod
    def check_system_notifications(self, scheduler: sched.scheduler = None):
        logger.debug(f"Checking system notifications at {time.time()}")
        if scheduler is not None:
            scheduler.enter(1, 1, self.check_system_notifications, (scheduler,))

        notifications = self._check_system_notifications()
        for notification in notifications:
            self.notification_router.route(notification)

    def _check_system_notifications(self) -> List[Notification]:
        return []


class MacNotificationMonitor(BaseNotifcationMonitor):
    # Mac notification table contains rec_id: INTEGER, app_id: INTEGER, uuid: BLOB, data: BLOB, request_date: REAL, request_last_date: REAL, delivered_date: REAL, presented:Bool, style: INTEGER, snooze_fire_date: REAL
    def __init__(self, notification_router: NotificationRouter):
        super().__init__(notification_router=notification_router)
        sys_tmp_path = (
            subprocess.run(["getconf", "DARWIN_USER_DIR"], stdout=subprocess.PIPE)
            .stdout.decode("utf-8")
            .rstrip()
        )
        db_path = os.path.join(
            sys_tmp_path, "com.apple.notificationcenter", "db2", "db"
        )
        if not os.path.exists(db_path):
            logger.warn(f"Notification database not found at {db_path}")
        connection = sqlite3.connect(db_path)
        self.cursor = connection.cursor()
        self.last_system_notification_time = self.check_last_system_notification_time()

    def _check_system_notifications(self) -> List[Notification]:
        records = self.cursor.execute(
            f"SELECT data, delivered_date FROM record WHERE delivered_date > {self.last_system_notification_time}"
        )
        notifications = []
        for record in records:
            data, delivered_date = record
            self.last_system_notification_time = delivered_date
            notification = self.parse_notification_data(data)
            notifications.append(notification)
        return notifications

    def check_last_system_notification_time(self) -> float:
        record = self.cursor.execute(
            "SELECT delivered_date FROM record ORDER BY delivered_date DESC LIMIT 1"
        ).fetchone()
        assert len(record) == 1
        return record[0]

    def parse_notification_data(self, raw_plist) -> Notification:
        data: Dict[str, Any] = plistlib.loads(raw_plist)
        notification = Notification(
            app_id=data["app"],
            title=data.get("req", {}).get("titl", ""),
            body=data.get("req", {}).get("body", ""),
        )
        return notification
