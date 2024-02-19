from typing import Dict
import yaml

from mnf.notification import Notification
from mnf.notification_forwarder import BaseNotificationForwarder


class NotificationRouter:

    def __init__(self, config_path: str) -> None:
        with open(config_path, "r") as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
        self.config = config
        self.forwarders: Dict[str, BaseNotificationForwarder] = {}
        assert "forwarders" in config, "No forwarders defined"
        for name, forwarder_config in config["forwarders"].items():
            if name == "slack":
                from mnf.notification_forwarder import SlackNotificationForwarder

                forwarder = SlackNotificationForwarder(**forwarder_config)
                self.forwarders[name] = forwarder

    def route(self, notification: Notification) -> None:
        self.forwarders["slack"].send_notification(notification)
