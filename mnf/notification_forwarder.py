from abc import abstractmethod
import os
from slack_sdk import WebClient

from mnf.notification import Notification

from dotenv import load_dotenv

load_dotenv()


class BaseNotificationForwarder:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def send_notification(self, notification: Notification) -> None:
        pass


class SlackNotificationForwarder(BaseNotificationForwarder):

    def __init__(self) -> None:
        super().__init__()
        slack_api_key = os.environ.get("SLACK_API_KEY")
        assert slack_api_key is not None, "SLACK_API_KEY is not set"
        self.client = WebClient(slack_api_key)

    def send_notification(self, notification: Notification) -> None:
        self.client.chat_postMessage(
            channel="C04HHD8RW6M", text=f"{notification.title}\n{notification.body}"
        )
        return
