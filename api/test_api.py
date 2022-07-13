import unittest
import unittest
from api.api import verify_message


class TestApi(unittest.TestCase):

    def test__verify_signature(self):

        message_id = '689c5e5f-52ae-4b59-b629-d9aac04af6ff'
        message_timestamp = '2022-07-13T20:37:25.683133703Z'
        message_signature = 'sha256=1c874182e386f364f5ae6aa13cb2738c4f1ed41f6003831999365081b2b01b7f'

        # message = '689c5e5f-52ae-4b59-b629-d9aac04af6ff2022-07-13T20:37:25.683133703Zb\'{"subscription":{"id":"10e7b4f6-2036-4d5e-9c83-8c0cd9787b45","status":"webhook_callback_verification_pending","type":"channel.follow","version":"1","condition":{"broadcaster_user_id":"118905535"},"transport":{"method":"webhook","callback":"https://36e3-139-47-40-199.eu.ngrok.io/ttv_callback"},"created_at":"2022-07-13T20:37:25.676585046Z","cost":1},"challenge":"2RbP0DRI-O3PnSrk-pHDnUVNu0BS806tDrFaMWL_W3g"}\''

        body = b'{"subscription":{"id":"10e7b4f6-2036-4d5e-9c83-8c0cd9787b45","status":"webhook_callback_verification_pending","type":"channel.follow","version":"1","condition":{"broadcaster_user_id":"118905535"},"transport":{"method":"webhook","callback":"https://36e3-139-47-40-199.eu.ngrok.io/ttv_callback"},"created_at":"2022-07-13T20:37:25.676585046Z","cost":1},"challenge":"2RbP0DRI-O3PnSrk-pHDnUVNu0BS806tDrFaMWL_W3g"}'

        # message = message_id.encode() + message_timestamp.encode() + body

        result = verify_message(
            message_id, message_timestamp, message_signature, body)

        self.assertTrue(result)
