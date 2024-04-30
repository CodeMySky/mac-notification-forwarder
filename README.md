# mac-notification-forwarder
A flexible python application to forward Mac OS Notifications to Other Platforms

# Setup
Required python version: 3.10.
Poetry is used to manage packages, to install poetry 1.7.1
```
curl -sSL https://install.python-poetry.org | python3 -
```
To install libraries
```
poetry install
```
- [Install slack app](https://slack.com/oauth/v2/authorize?client_id=155947593521.6629501796849&scope=app_mentions:read,channels:join,channels:read,chat:write,chat:write.public,groups:write,im:write,mpim:write,reminders:write&user_scope=)
- Get slack api key and save it to `SLACK_API_KEY` variable, to get slack oauth token, go to https://api.slack.com/apps/A06JHERPEQZ/oauth
- If channel setting is set to a channel id, all messages will be send to that channel, if default, it will create channels based on app id


# To Run
```
poetry run python run.py
```