import hmac
from config.config import APP_SECRET

HMAC_PREFIX = 'sha256='


def verify_message(id, timestamp, signature, body):

    message = id.encode() + timestamp.encode() + body

    hmac_signature = HMAC_PREFIX + \
        hmac.new(APP_SECRET.encode(), message, digestmod='sha256').hexdigest()

    return hmac.compare_digest(hmac_signature, signature)


def usernames_to_urls(usernames: str):
    return [f'https://twitch.tv/{username}' for username in usernames.split(' ') if username]
