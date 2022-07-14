from common.db import SQLite

from config.config import DBFILE


class CreadorsDb():

    def __init__(self, dbfile):
        self.dbfile = dbfile
        create_query = f'''
        create table if not exists streamers (
            streamer_id integer primary key autoincrement,
            twitch_username string not null,
            twitch_user_id integer unique not null,
            discord_username string not null,
            discord_user_id integer not null,
            create_date integer default current_timestamp,
            update_date integer default current_timestamp
        )'''
        with SQLite(self.dbfile) as con:
            con.execute(create_query)

    def add_streamer(self, twitch_username, twitch_user_id, discord_username, discord_user_id):
        insert_query = f'''
        insert into streamers(twitch_username, twitch_user_id, discord_username, discord_user_id) values(?,?,?,?)
        on conflict(twitch_user_id) do update set
         twitch_username=excluded.twitch_username,
         twitch_user_id=excluded.twitch_user_id,
         discord_username=excluded.discord_username,
         discord_user_id=excluded.discord_user_id,
         update_date=excluded.update_date
        ;
        '''
        with SQLite(self.dbfile) as con:
            con.execute(insert_query, (twitch_username,
                        twitch_user_id, discord_username, discord_user_id))
