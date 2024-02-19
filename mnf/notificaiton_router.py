import logging
import os
from typing import Dict
import yaml
import Quartz

from mnf.notification import Notification
from mnf.notification_forwarder import BaseNotificationForwarder

logger = logging.getLogger(__name__)


class NotificationRouter:

    def __init__(self, config_path: str) -> None:

        self.config_path = config_path
        self._load_config()
        # Initialize cg session
        self.cg_session = Quartz.CGSessionCopyCurrentDictionary()

    def _load_config(self):
        with open(self.config_path, "r") as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
        self.config = config
        self.forwarders: Dict[str, BaseNotificationForwarder] = {}
        assert "forwarders" in config, "No forwarders defined"
        for name, forwarder_config in config["forwarders"].items():
            if name == "slack":
                from mnf.notification_forwarder import SlackNotificationForwarder

                forwarder = SlackNotificationForwarder(**forwarder_config)
                self.forwarders[name] = forwarder
        self._config_updated_at = os.path.getmtime(self.config_path)

    def _check_config_update(self):
        if os.path.getmtime(self.config_path) > self._config_updated_at:
            logger.info("Config file updated, reloading...")
            self._load_config()
            self._config_updated_at = os.path.getmtime(self.config_path)

    def route(self, notification: Notification) -> None:
        self._check_config_update()
        if self._should_send(notification):
            logger.info(f"Sending notification {notification}")
            self.forwarders["slack"].send_notification(notification)

    def _should_send(self, notification: Notification) -> bool:
        should_send = True
        # Check locked_only
        if self.config["router"]["locked_only"] and not self.sys_is_locked():
            should_send = False
            logger.info(
                f"Skipping {notification} because system is not locked and lock_only is set to true"
            )
        elif notification.app_id in self.config["router"]["block_list"]:
            should_send = False
            logger.info(f"Skipping {notification} because it is in the block list")
        return should_send

    def sys_is_locked(self) -> bool:
        return "CGSSessionScreenIsLocked" in self.cg_session.keys()
