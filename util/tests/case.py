import os, shutil
from django.test import TestCase

class BaseTestCase(TestCase):

    def setUp(self):
        try:
            db_path = 'db.sqlite3'
            db_bak_path = 'db_bak.sqlite3'
            if os.path.exists(db_path):
                os.remove(db_path)
            shutil.copyfile(db_bak_path, db_path)
        except:
            pass

    def get_message(self, resp):
        try:
            return resp.json()
        except:
            return resp.status_code

    def assert_status(self, resp, status_code):
        self.assertEqual(resp.status_code, status_code, self.get_message(resp))

    def assert_status_200(self, resp):
        self.assert_status(resp, 200)

    def assert_status_201(self, resp):
        self.assert_status(resp, 201)

    def assert_status_204(self, resp):
        self.assert_status(resp, 204)

    def assert_status_400(self, resp):
        self.assert_status(resp, 400)

    def assert_status_401(self, resp):
        self.assert_status(resp, 401)

    def assert_status_403(self, resp):
        self.assert_status(resp, 403)

    def assert_status_404(self, resp):
        self.assert_status(resp, 404)

    def assert_status_409(self, resp):
        self.assert_status(resp, 409)

    def assert_list_length(self, resp, length):
        self.assertEqual(len(resp.json()), length)
