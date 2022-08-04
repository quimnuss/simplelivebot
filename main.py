import curlify
import requests
import typer
from typing import List

from services.twitch import Twitch
from config.config import *

app = typer.Typer()


@app.command()
def subscribe(twitch_username: str = TWITCH_USERNAME, esubtype: str = 'stream.online', channel_id: int = None):
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    twitch.subscribe(twitch_username=twitch_username,
                     esubtype=esubtype, channel_id=channel_id)


@app.command()
def unsubscribe(twitch_username: str):
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)
    twitch.unsubscribe(twitch_username=twitch_username)


@app.command()
def unsubscribe_all():
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    esublist = twitch.get_event_subscriptions()

    # delete all event subscriptions
    logging.info(esublist)
    for esub in esublist.data:
        response = twitch.delete_event_subscription(esub.id)
        if response.status_code == 204:
            logging.info(f'Deleted subscription {esub.id}')


def get_subscriptions():
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)
    return twitch.get_event_subscriptions()


@app.command()
def check_subscriptions():

    esublist = get_subscriptions()

    logging.info(esublist)


@app.command()
def ids_to_username(ids: List[int]):

    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)
    usernames = twitch.get_usernames_from_channel_ids(channel_ids=ids)
    logging.info(usernames)


if __name__ == '__main__':
    app()

# c = curlify.to_curl(response.request)
# print(c)
# import ipdb
# ipdb.set_trace()
