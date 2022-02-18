import requests, shutil, os
from util.tests.client import ApiClient
from util.tests.unit_test_client import UnitTestClient
from util.tests.case import BaseTestCase

class DistributeUploadTest(BaseTestCase):

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

    def test_org_app_upload_ipa(self):
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

        r = self.client.org.get_package(org_name, app_name, internal_build)
        self.assert_status_200(r)

        r = self.client.org.get_package_list(org_name, app_name)
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        package = {'description': 'hello'}
        r = self.client.org.modify_package(org_name, app_name, internal_build, package)
        self.assert_status_200(r)
        r = self.client.org.get_package(org_name, app_name, internal_build)
        self.assert_status_200(r)
        self.assertEqual(r.json()['description'], package['description'])

        r = self.client.org.remove_package(org_name, app_name, internal_build)
        self.assert_status_204(r)
        r = self.client.org.get_package(org_name, app_name, internal_build)
        self.assert_status_404(r)

        r = self.client.org.get_package_list(org_name, app_name)
        self.assert_status_200(r)
        self.assert_list_length(r, 0)


    def test_org_app_upload_apk(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        app = self.generate_android_app()
        org_name = org['name']
        app_name = app['name']
        r = self.client.org.create_app(org_name, app)
        self.assert_status_201(r)

        r = self.client.org.upload_app(org_name, app_name, self.apk_path)
        self.assert_status_201(r)

        r = self.client.org.get_package(org_name, app_name, 1)
        self.assert_status_200(r)

        r = self.client.org.get_package_list(org_name, app_name)
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

    def test_user_app_upload_ipa(self):
        app = self.generate_ios_app()
        r = self.client.app.create(app)
        self.assert_status_201(r)

        ownername = 'admin'
        app_name = app['name']

        r = self.client.app.upload_app(ownername, app_name, self.ipa_path)
        self.assert_status_201(r)
        internal_build = r.json()['internal_build']

        r = self.client.app.get_package(ownername, app_name, internal_build)
        self.assert_status_200(r)

        r = self.client.app.get_package_list(ownername, app_name)
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        package = {'description': 'hello'}
        r = self.client.app.modify_package(ownername, app_name, internal_build, package)
        self.assert_status_200(r)
        r = self.client.app.get_package(ownername, app_name, internal_build)
        self.assert_status_200(r)
        self.assertEqual(r.json()['description'], package['description'])

        r = self.client.app.remove_package(ownername, app_name, internal_build)
        self.assert_status_204(r)
        r = self.client.app.get_package(ownername, app_name, internal_build)
        self.assert_status_404(r)

        r = self.client.app.get_package_list(ownername, app_name)
        self.assert_status_200(r)
        self.assert_list_length(r, 0)

    def test_user_app_upload_apk(self):
        app = self.generate_android_app()
        r = self.client.app.create(app)
        self.assert_status_201(r)

        ownername = 'admin'
        app_name = app['name']

        r = self.client.app.upload_app(ownername, app_name, self.apk_path)
        self.assert_status_201(r)

        r = self.client.app.get_package(ownername, app_name, 1)
        self.assert_status_200(r)

        r = self.client.app.get_package_list(ownername, app_name)
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
