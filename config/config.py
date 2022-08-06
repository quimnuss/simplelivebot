from dotenv import load_dotenv
import os
import logging
logging.basicConfig(level=logging.INFO)

load_dotenv()

APP_ID = os.getenv('TWITCH_APP_ID')
APP_SECRET = os.getenv('TWITCH_APP_SECRET')

TWITCH_USERNAME = os.getenv("TWITCH_TARGET_USERNAME")

# TODO get channel id from target_username
# meanwhile, here: https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
APP_API_URL = os.getenv('APP_API_BASE_URL')
APP_API_TTV_CALLBACK_ENDPOINT = os.getenv('APP_API_TTV_CALLBACK_ENDPOINT')
TWITCH_CALLBACK_URL = f'{APP_API_URL}/{APP_API_TTV_CALLBACK_ENDPOINT}'

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
