import os
import unittest
from common.creadors import CreadorsDb
from common.db import SQLite
from faker import Faker


class TestCreadorsDb(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbfile = 'testdb.sqlite3'

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.dbfile)

    def test__add_streamer(self):
        creadorsdb = CreadorsDb(self.dbfile)
        creadorsdb.add_streamer('test_ttv', 12345, 'test_disc', 12345, 56789)

        with SQLite(self.dbfile) as con:
            result = con.execute('''
                select twitch_username, twitch_user_uid, discord_username, discord_user_uid
                from streamers;
            ''').fetchall()

        expected = [('test_ttv', 12345, 'test_disc', 12345)]

        self.assertListEqual(result, expected)

    def test__list_streamers(self):
        creadorsdb = CreadorsDb(self.dbfile)
        fake = Faker()

        names = [fake.first_name(), fake.first_name()]
        [creadorsdb.add_streamer(
            f'{name}_ttv', fake.random_int(), f'{name}_disc', fake.random_int(), 56789) for name in names]

        result = creadorsdb.get_streamers_by_discord_user(
            [f'{name}_disc' for name in names])

        expected = [(f'{name}_disc',
                     f'{name}_ttv') for name in names]

        self.assertListEqual(result, expected)
