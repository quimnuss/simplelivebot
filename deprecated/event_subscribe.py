import curlify
import requests
import typer

from services.twitch import Twitch
from config.config import *


def subscribe(twitch_username: str = None):
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)
    twitch_username = twitch_username or TWITCH_USERNAME
    channel_id = twitch.get_channel_id_from_username(username=twitch_username)

    esubtype = 'channel.follow'

    try:
        response = twitch.event_subscribe(
            esubtype=esubtype, channel_id=channel_id)
        print(f"Status {response.status_code}. Body: {response.json()}")
    except requests.HTTPError as e:
        print(f"Error request: {e.request}")
        curl_request = curlify.to_curl(e.request)
        print(f"Curl version: {curl_request}")
    except Exception as e:
        print(
            f"Error subscribing to {esubtype} response code: {e}")

        raise e


if __name__ == '__main__':
    typer.run(subscribe)

# c = curlify.to_curl(response.request)
# print(c)
# import ipdb
# ipdb.set_trace()
