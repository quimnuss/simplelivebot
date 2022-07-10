import logging
from services.twitch import Twitch
from config.config import *

twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                callback_url=TWITCH_CALLBACK_URL)

esublist = twitch.get_event_subscriptions()

# delete all event subscriptions
logging.info(esublist)
for esub in esublist.data:
    response = twitch.delete_event_subscription(esub.id)
    if response.status_code == 204:
        logging.info(f'Deleted subscription {esub.id}')
