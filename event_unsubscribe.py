import requests
import os

from api.schemas import EventSubList

from dotenv import load_dotenv
load_dotenv()

APP_ID = os.getenv('TWITCH_APP_ID')
APP_SECRET = os.getenv('TWITCH_APP_SECRET')
TWITCH_CLIENTID = os.getenv("TWITCH_CLIENTID")


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

sub_url = 'https://api.twitch.tv/helix/eventsub/subscriptions'

response = requests.get(sub_url, headers=headers)

response.raise_for_status()
esublist = EventSubList(**response.json())

# delete all event subscriptions
for esub in esublist.data:
    response = requests.delete(
        sub_url, headers=headers, json={'id': str(esub.id)})
    response.raise_for_status()
    if response.status_code == 204:
        print(f'Deleted subscription {esub.id}')
