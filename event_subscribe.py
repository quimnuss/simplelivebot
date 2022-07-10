import curlify
import requests

from services.twitch import Twitch
from config.config import *

twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                callback_url=CALLBACK_URL)
channel_id = twitch.get_channel_id_from_username(username=TWITCH_USERNAME)

# TODO use list of usernames instead of channels ids and save them
# base code to channel ids not usernames which keep changing
assert channel_id == TWITCH_CHANNEL_ID

esubtype = 'channel.follow'

try:
    response = twitch.event_subscribe(
        esubtype=esubtype, channel_id=TWITCH_CHANNEL_ID)
    print(f"Satus {response.status_code}. Body: {response.json()}")
except requests.HTTPError as e:
    print(f"Error request: {e.request}")
    curl_request = curlify.to_curl(e.request)
    print(f"Curl version: {curl_request}")
except Exception as e:
    print(
        f"Error subscribing to {esubtype} response code: {e}")

    raise e


# c = curlify.to_curl(response.request)
# print(c)
# import ipdb
# ipdb.set_trace()
