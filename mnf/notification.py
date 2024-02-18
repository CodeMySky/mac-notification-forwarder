from dataclasses import dataclass


@dataclass
class Notification:
    app_id: str
    title: str
    body: str
