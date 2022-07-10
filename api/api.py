from fastapi import FastAPI, Body, Header, Request
from fastapi.responses import PlainTextResponse
from typing import Union
from .schemas import Subscription, TtvChallenge

app = FastAPI()


def challenge_process():
    # TODO test that the challenge is legit
    # https://dev.twitch.tv/docs/eventsub/handling-webhook-events/#verifying-the-event-message
    pass


@app.get("/")
async def root():
    return {"message": "Hello World"}

# test with twitch-cli
# twitch-cli_1.1.6_Linux_x86_64/twitch event verify-subscription subscribe -F http://localhost:8000 -s TWITCH_APP_SECRET

# TODO we could explore the redirect option to distinguish challenge and legit event
# https://stackoverflow.com/questions/62282100/fastapi-redirectresponse-custom-headers
# e.g. https://github.com/tiangolo/fastapi/issues/199
#


@app.post("/ttv_callback")
async def root(request: Request, twitch_eventsub_message_type: Union[str, None] = Header(default=None), data=Body()):
    print(data)

    if twitch_eventsub_message_type == 'webhook_callback_verification':
        ttv_challenge = TtvChallenge(**data)
        return PlainTextResponse(str(ttv_challenge.challenge))
    print("We got a sub event!")
    print(request.headers)
    print(data)

    return {"message": "Hello World"}


# @app.post("/")
# async def root(subchallenge: TtvChallenge, request: Request):
#     # we have to filter by header :(
#     # we can't use proper pydantic validation
#     return {subchallenge.challenge}
