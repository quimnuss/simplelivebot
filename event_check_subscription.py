from services.twitch import Twitch
from config.config import *

twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                callback_url=CALLBACK_URL)

esublist = twitch.get_event_subscriptions()

print(esublist)
