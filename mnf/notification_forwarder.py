from abc import abstractmethod
import os
import logging
from slack_sdk import WebClient

from mnf.notification import Notification

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class BaseNotificationForwarder:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def send_notification(self, notification: Notification) -> None:
        pass


class SlackNotificationForwarder(BaseNotificationForwarder):

    def __init__(self, channel_setting: str) -> None:
        super().__init__()
        slack_api_key = os.environ.get("SLACK_API_KEY")
        if slack_api_key is None:
            logger.error("SLACK_API_KEY is not set")
        self.client = WebClient(slack_api_key)
        self.channel_setting = channel_setting
        self.channel_to_id_map = {}
        channels = self.client.conversations_list()
        for channel in channels["channels"]:
            self.channel_to_id_map[channel["name"]] = channel["id"]

    def create_or_get_channel_id(self, name: str) -> str:
        if self.channel_setting != "default":
            return self.channel_setting
        name = name.lower().split(".")[-1]
        if name not in self.channel_to_id_map:
            logger.info(f"Creating new channel {name}")
            try:
                res = self.client.conversations_create(name=name)
                self.channel_to_id_map[name] = res["channel"]["id"]
                slack_user = os.environ.get("SLACK_USER_ID")
                if slack_user is not None and slack_user != '':
                    self.client.conversations_invite(
                        channel=res["channel"]["id"], users=slack_user
                    )
            except Exception as e:
                logger.error(e)

        return self.channel_to_id_map[name]

    def send_notification(self, notification: Notification) -> None:
        channel_id = self.create_or_get_channel_id(notification.app_id)
        self.client.chat_postMessage(
            channel=channel_id, text=f"{notification.title}\n{notification.body}"
        )
        return
