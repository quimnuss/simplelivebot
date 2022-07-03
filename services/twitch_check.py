from pprint import pprint
from twitchAPI import Twitch, EventSub

import os
from dotenv import load_dotenv
load_dotenv()

# this will be called whenever someone follows the target channel
async def on_follow(data: dict):
    pprint(data)

TARGET_USERNAME = os.getenv('TWITCH_TARGET_USERNAME')
WEBHOOK_URL = os.getenv('TWITCH_WEBHOOK_URL')
APP_ID = os.getenv('TWITCH_APP_ID')
APP_SECRET = os.getenv('TWITCH_APP_SECRET')

twitch = Twitch(APP_ID, APP_SECRET)
twitch.authenticate_app([])

uid = twitch.get_users(logins=[TARGET_USERNAME])
user_id = uid['data'][0]['id']
# basic setup, will run on port 8080 and a reverse proxy takes care of the https and certificate
hook = EventSub(WEBHOOK_URL, APP_ID, 8080, twitch)
# unsubscribe from all to get a clean slate
hook.unsubscribe_all()
# start client
hook.start()
print('subscribing to hooks:')
hook.listen_channel_follow(user_id, on_follow)

try:
    input('press Enter to shut down...')
finally:
    hook.stop()
print('done')