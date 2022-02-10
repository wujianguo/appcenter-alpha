import requests, shutil, os
from util.tests.client import ApiClient, UnitTestClient
from util.tests.case import BaseTestCase

class ReleaseTest(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.client: ApiClient = ApiClient(UnitTestClient('/api/', 'admin'))
        self.org_index = 0
        self.app_index = 0
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
        self.apk_path = 'downloads/android-sample.apk'
        if not os.path.exists(self.apk_path):
            url = 'https://raw.githubusercontent.com/bitbar/test-samples/master/apps/android/bitbar-sample-app.apk'
            with requests.get(url, stream=True) as r:
                with open(self.apk_path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
        self.ipa_path = 'downloads/ios-sample.ipa'
        if not os.path.exists(self.ipa_path):
            url = 'https://raw.githubusercontent.com/bitbar/test-samples/master/apps/ios/bitbar-ios-sample.ipa'
            with requests.get(url, stream=True) as r:
                with open(self.ipa_path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)

    def generate_org(self):
        self.org_index += 1
        org = {
            'name': 'org_name_' + str(self.org_index),
            'display_name': 'org_display_name_' + str(self.org_index),
            'visibility': 'Private'
        }
        return org

    def generate_ios_app(self):
        self.app_index += 1
        app = {
            'name': 'app_name_' + str(self.app_index),
            'display_name': 'app_display_name_' + str(self.app_index),
            'release_type': 'Alpha',
            'platform': 'ObjectiveCSwift',
            'visibility': 'Private',
            'os': 'iOS'
        }
        return app

    def generate_android_app(self):
        self.app_index += 1
        app = {
            'name': 'app_name_' + str(self.app_index),
            'display_name': 'app_display_name_' + str(self.app_index),
            'release_type': 'Alpha',
            'platform': 'JavaKotlin',
            'visibility': 'Private',
            'os': 'Android'
        }
        return app

    def test_org_app_release(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        app = self.generate_ios_app()
        org_name = org['name']
        app_name = app['name']
        r = self.client.org.create_app(org_name, app)
        self.assert_status_201(r)

        r = self.client.org.upload_app(org_name, app_name, self.ipa_path)
        self.assert_status_201(r)
        internal_build = r.json()['internal_build']

        release = {
            'release_notes': 'release_notes',
            'internal_build': internal_build,
            'enabled': True
        }
        env = 'production'
        r = self.client.org.create_release(org_name, app_name, env, release)
        self.assert_status_201(r)
        release_id = r.json()['release_id']

        r = self.client.org.get_release(org_name, app_name, release_id)
        self.assert_status_200(r)
        r = self.client.org.get_release_list(org_name, app_name, env)
        self.assert_list_length(r, 1)

        modify_release = {
            'release_notes': 'release_notes2'
        }
        r = self.client.org.modify_release(org_name, app_name, release_id, modify_release)
        self.assert_status_200(r)
        r = self.client.org.get_release(org_name, app_name, release_id)
        self.assertEqual(r.json()['release_notes'], modify_release['release_notes'])

        r = self.client.org.remove_release(org_name, app_name, release_id)
        self.assert_status_204(r)
        r = self.client.org.get_release(org_name, app_name, release_id)
        self.assert_status_404(r)

    def test_user_app_release(self):
        app = self.generate_ios_app()
        ownername = 'admin'
        app_name = app['name']
        r = self.client.app.create(app)
        self.assert_status_201(r)

        r = self.client.app.upload_app(ownername, app_name, self.ipa_path)
        self.assert_status_201(r)
        internal_build = r.json()['internal_build']

        release = {
            'release_notes': 'release_notes',
            'internal_build': internal_build,
            'enabled': True
        }
        env = 'production'
        r = self.client.app.create_release(ownername, app_name, env, release)
        self.assert_status_201(r)
        release_id = r.json()['release_id']

        r = self.client.app.get_release(ownername, app_name, release_id)
        self.assert_status_200(r)
        r = self.client.app.get_release_list(ownername, app_name, env)
        self.assert_list_length(r, 1)

        modify_release = {
            'release_notes': 'release_notes2'
        }
        r = self.client.app.modify_release(ownername, app_name, release_id, modify_release)
        self.assert_status_200(r)
        r = self.client.app.get_release(ownername, app_name, release_id)
        self.assertEqual(r.json()['release_notes'], modify_release['release_notes'])

        r = self.client.app.remove_release(ownername, app_name, release_id)
        self.assert_status_204(r)
        r = self.client.app.get_release(ownername, app_name, release_id)
        self.assert_status_404(r)
