from services.twitch import Twitch
from config.config import *

twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                callback_url=CALLBACK_URL)

esublist = twitch.get_event_subscriptions()

# delete all event subscriptions
print(esublist)
for esub in esublist.data:
    response = twitch.delete_event_subscription(esub.id)
    if response.status_code == 204:
        print(f'Deleted subscription {esub.id}')
