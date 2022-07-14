from dotenv import load_dotenv
import os
import logging
logging.basicConfig(level=logging.INFO)

load_dotenv()

TARGET_USERNAME = os.getenv('TWITCH_TARGET_USERNAME')
WEBHOOK_URL = os.getenv('TWITCH_WEBHOOK_URL')
APP_ID = os.getenv('TWITCH_APP_ID')
APP_SECRET = os.getenv('TWITCH_APP_SECRET')
TWITCH_CLIENTID = os.getenv("TWITCH_CLIENTID")

TWITCH_USERNAME = os.getenv("TWITCH_TARGET_USERNAME")

# TODO get channel id from target_username
# meanwhile, here: https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
APP_API_URL = os.getenv('APP_API_BASE_URL')
APP_API_TTV_CALLBACK_ENDPOINT = os.getenv('APP_API_TTV_CALLBACK_ENDPOINT')
TWITCH_CALLBACK_URL = f'{APP_API_URL}/{APP_API_TTV_CALLBACK_ENDPOINT}'
TWITCH_CHANNEL_ID = os.getenv('TWITCH_CHANNEL_ID')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_GUILD = os.getenv('DISCORD_GUILD')

DBFILE = os.getenv('DBFILE')
