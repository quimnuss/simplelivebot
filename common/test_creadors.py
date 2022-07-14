import os
import unittest
from common.creadors import CreadorsDb
from common.db import SQLite


class TestCreadorsDb(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbfile = 'testdb.sqlite3'

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.dbfile)

    def test__add_streamer(self):
        creadorsdb = CreadorsDb(self.dbfile)
        creadorsdb.add_streamer('test_ttv', 12345, 'test_disc', 12345)

        with SQLite(self.dbfile) as con:
            result = con.execute('''
                select twitch_username, twitch_user_id, discord_username, discord_user_id
                from streamers;
            ''').fetchall()

        expected = [('test_ttv', 12345, 'test_disc', 12345)]

        self.assertListEqual(result, expected)
