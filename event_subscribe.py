import requests
import os
from dotenv import load_dotenv
load_dotenv()

TARGET_USERNAME = os.getenv('TWITCH_TARGET_USERNAME')
WEBHOOK_URL = os.getenv('TWITCH_WEBHOOK_URL')
CALLBACK_URL = os.getenv('TWITCH_CALLBACK_URL')
APP_ID = os.getenv('TWITCH_APP_ID')
APP_SECRET = os.getenv('TWITCH_APP_SECRET')
TWITCH_CLIENTID = os.getenv("TWITCH_CLIENTID")

# TODO get channel id from target_username
# meanwhile, here: https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
TWITCH_CHANNEL_ID = os.getenv('TWITCH_CHANNEL_ID')


def get_token():
    params = {'client_id': APP_ID, 'client_secret': APP_SECRET,
              'grant_type': 'client_credentials'}
    response = requests.post(
        url='https://id.twitch.tv/oauth2/token', data=params)
    token = response.json()['access_token']
    return token


token = get_token()

headers = {
    'Client-Id': APP_ID,
    'Authorization': f'Bearer {token}'
}

data = {
    'client_id': APP_ID,
    "type": "channel.follow",
    "version": "1",
    "condition": {"broadcaster_user_id": TWITCH_CHANNEL_ID},
    "transport": {"method": "webhook", "callback": CALLBACK_URL, "secret": APP_SECRET}
}

sub_url = 'https://api.twitch.tv/helix/eventsub/subscriptions'

response = requests.post(sub_url, headers=headers, json=data)

print(f"response code: {response.status_code}")
print(f"Body: {response.json()}")

# import curlify
# import ipdb
# c = curlify.to_curl(response.request)
# print(c)
# ipdb.set_trace()
