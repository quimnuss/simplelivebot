import os
import logging
from common.db import SQLite

from config.config import DBFILE


class CreadorsDb():

    def __init__(self, dbfile):
        self.dbfile = dbfile
        create_query = f'''
        create table if not exists streamers (
            streamer_id integer primary key autoincrement,
            twitch_username string,
            twitch_user_uid integer unique,
            discord_username string,
            discord_user_uid integer unique,
            discord_channel_uid integer,
            create_date integer default current_timestamp,
            update_date integer default current_timestamp
        )'''
        with SQLite(self.dbfile) as con:
            result = con.execute(create_query)
            logging.info(
                f'Creation database result: {result} abs path: {os.path.abspath(self.dbfile)}')

    def clear_db(self):
        if os.path.exists(self.dbfile):
            os.remove(self.dbfile)
        else:
            logging.error(f"Database file {self.dbfile} does not exist")

    def add_streamer(self, twitch_username, twitch_user_uid, discord_username, discord_user_uid, discord_channel_uid):
        insert_query = f'''
        insert into
        streamers(twitch_username, twitch_user_uid, discord_username, discord_user_uid, discord_channel_uid)
        values(?,?,?,?,?)
        on conflict(twitch_user_uid) do update set
         twitch_username=excluded.twitch_username,
         twitch_user_uid=excluded.twitch_user_uid,
         discord_username=excluded.discord_username,
         discord_user_uid=excluded.discord_user_uid,
         discord_channel_uid=excluded.discord_channel_uid,
         update_date=excluded.update_date
        ;
        '''
        with SQLite(self.dbfile) as con:
            con.execute(insert_query, (twitch_username,
                        twitch_user_uid, discord_username, discord_user_uid, discord_channel_uid))

    def remove_streamer_by_twitch_username(self, twitch_username, discord_channel_uid):
        query = f'''
        delete from streamers where twitch_username = ? and discord_channel_uid = ?;
        '''
        with SQLite(self.dbfile) as con:
            con.execute(query, (twitch_username, discord_channel_uid))


    def get_streamers_by_discord_user(self, disc_usernames):
        if len(disc_usernames) > 900:
            logging.error("Too many usernames, select will fail.")

        query = f'''
        select discord_username, twitch_username from streamers where discord_username in ({', '.join('?'*len(disc_usernames))});
        '''
        with SQLite(self.dbfile) as con:
            return con.execute(query, disc_usernames).fetchall()

    def get_streamers_by_discord_guild(self, discord_channel_uid):
        query = f'''
        select discord_username, twitch_username from streamers where discord_channel_uid = ?;
        '''
        with SQLite(self.dbfile) as con:
            return con.execute(query, (discord_channel_uid,)).fetchall()


    def get_channel_streamers_without_twitch_username(self, discord_channel_uid):
        query = f'''
        select discord_username from streamers where discord_channel_uid = ? and twitch_username is null;
        '''
        with SQLite(self.dbfile) as con:
            return con.execute(query, (discord_channel_uid,)).fetchall()
