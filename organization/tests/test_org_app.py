from util.tests.client import ApiClient, UnitTestClient
from util.tests.case import BaseTestCase


class OrganizationApplicationTest(BaseTestCase):

    def setUp(self):
        self.client: ApiClient = ApiClient(UnitTestClient('/api/', 'admin'))
        self.org_index = 0
        self.app_index = 0

    def generate_org(self, visibility='Private'):
        self.org_index += 1
        org = {
            'name': 'org_name_' + str(self.org_index),
            'display_name': 'org_display_name_' + str(self.org_index),
            'visibility': visibility
        }
        return org

    def generate_app(self):
        self.app_index += 1
        app = {
            'name': 'app_name_' + str(self.app_index),
            'display_name': 'app_display_name_' + str(self.app_index),
            'release_type': 'Alpha',
            'platform': 'ObjectiveCSwift',
            'os': 'iOS'
        }
        return app
    
    def test_create_app_success(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        app = self.generate_app()
        r = self.client.org.create_app(org['name'], app)
        self.assert_status_201(r)
        r = self.client.org.get_app(org['name'], app['name'])
        self.assert_status_200(r)
        r = self.client.org.get_app_list(org['name'])
        self.assert_list_length(r, 1)

    def test_invalid_name(self):
        # 1. only letters, numbers, underscores or hyphens
        # 2. 0 < len(name) <= 32
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        app = self.generate_app()
        r = self.client.org.create_app(org['name'], app)
        self.assert_status_201(r)

        max_length = 32
        app = self.generate_app()
        app['name'] = 'a' * max_length
        r2 = self.client.org.create_app(org['name'], app)
        self.assert_status_201(r2)

        app = self.generate_app()
        app['name'] = 'a' * max_length + 'a'
        r3 = self.client.org.create_app(org['name'], app)
        self.assert_status_400(r3)

        app = self.generate_app()
        app['name'] = ''
        r4 = self.client.org.create_app(org['name'], app)
        self.assert_status_400(r4)

        app = self.generate_app()
        del app['name']
        r5 = self.client.org.create_app(org['name'], app)
        self.assert_status_400(r5)

    def test_duplicate_name(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        app = self.generate_app()
        r = self.client.org.create_app(org['name'], app)
        self.assert_status_201(r)

        app2 = self.generate_app()
        app2['name'] = app['name']
        r2 = self.client.org.create_app(org['name'], app2)
        self.assert_status_400(r2)

    def test_required(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        app = self.generate_app()
        del app['name']
        r = self.client.org.create_app(org['name'], app)
        self.assert_status_400(r)

        app = self.generate_app()
        del app['display_name']
        r = self.client.org.create_app(org['name'], app)
        self.assert_status_400(r)
        
        app = self.generate_app()
        del app['os']
        r = self.client.org.create_app(org['name'], app)
        self.assert_status_400(r)

        app = self.generate_app()
        del app['platform']
        r = self.client.org.create_app(org['name'], app)
        self.assert_status_400(r)

        app = self.generate_app()
        del app['release_type']
        r = self.client.org.create_app(org['name'], app)
        self.assert_status_400(r)

    def test_invalid_display_name(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        app = self.generate_app()
        r = self.client.org.create_app(org['name'], app)
        self.assert_status_201(r)

        max_length = 128
        app = self.generate_app()
        app['display_name'] = 'a' * max_length
        r2 = self.client.org.create_app(org['name'], app)
        self.assert_status_201(r2)

        app = self.generate_app()
        app['display_name'] = 'a' * max_length + 'a'
        r3 = self.client.org.create_app(org['name'], app)
        self.assert_status_400(r3)

        app = self.generate_app()
        app['display_name'] = ''
        r4 = self.client.org.create_app(org['name'], app)
        self.assert_status_400(r4)

    def test_modify_app_name(self):
        org = self.generate_org()
        r = self.client.org.create(org)
        self.assert_status_201(r)

        app = self.generate_app()
        r = self.client.org.create_app(org['name'], app)
        self.assert_status_201(r)

        new_name = 'new_name'
        data = {'name': new_name}
        r2 = self.client.org.modify_app(org['name'], app['name'], data)
        self.assert_status_200(r2)

        r3 = self.client.org.get_app(org['name'], app['name'])
        self.assert_status_404(r3)

        r4 = self.client.org.get_app(org['name'], new_name)
        self.assert_status_200(r4)
        old_value = r.json()
        old_value['name'] = new_name
        del old_value['update_time']
        new_value = r4.json()
        del new_value['update_time']
        self.assertDictEqual(new_value, old_value)
