import tempfile
from util.tests.client import ApiClient, UnitTestClient
from util.tests.case import BaseTestCase

class OrganizationCreateTest(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.client: ApiClient = ApiClient(UnitTestClient('/api/'))

    def test_register(self):
        client = UnitTestClient('/api/')
        anonymous_user = ApiClient(client)
        user = {
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'user1*Pawd'
        }
        r = anonymous_user.user.register(user)
        self.assert_status_201(r)
        client.set_token(r.json()['token'])
        r = anonymous_user.user.me()
        self.assert_status_200(r)

        client.set_token(None)
        r = anonymous_user.user.me()
        self.assert_status_401(r)

        user = {
            'username': 'user1',
            'password': 'user1*Pawd'
        }
        r = anonymous_user.user.login(user)
        self.assert_status_200(r)
        client.set_token(r.json()['token'])
        r = anonymous_user.user.me()
        self.assert_status_200(r)
