# creadorslivebot

Bot to notify streams going live on a discord channel

# develop

Rename .env.example to .env and configure it.

install dependencies with

```
$ pip install -r requirements.txt
```

Start a nginx server to provide https with is required by twitch. Alternativelly you can start ngrok

```
$ ngrok http 8000
```

Then start the api

```
$ uvicorn api.api:app
```

And you can trigger events via the main.py script or via the discord commands if you add the bot to your server. At the moment the bot only listens to commands on the channel #bot-control

# deploy to heroku