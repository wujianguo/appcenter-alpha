from util.tests.client import ApiClient, UnitTestClient
from util.tests.case import BaseTestCase


class ApplicationPermissionTest(BaseTestCase):

    def setUp(self):
        self.client: ApiClient = ApiClient(UnitTestClient('/api/', 'admin'))
        self.client_name = 'admin'
        self.app_index = 0

    def generate_app(self, visibility='Private'):
        self.app_index += 1
        app = {
            'name': 'app_name_' + str(self.app_index),
            'display_name': 'app_display_name_' + str(self.app_index),
            'release_type': 'Alpha',
            'platform': 'ObjectiveCSwift',
            'os': 'iOS',
            'visibility': visibility
        }
        return app

    def test_app_visibility(self):
        app1 = self.generate_app('Private')
        r1 = self.client.app.create(app1)
        self.assert_status_201(r1)

        app2 = self.generate_app('Internal')
        r2 = self.client.app.create(app2)
        self.assert_status_201(r2)

        app3 = self.generate_app('Public')
        r3 = self.client.app.create(app3)
        self.assert_status_201(r3)

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r4 = internal_user.app.get_list(self.client_name)
        self.assert_list_length(r4, 2)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r5 = anonymous_user.app.get_list(self.client_name)
        self.assert_list_length(r5, 1)

    def test_member_can_view_private_app(self):
        app = self.generate_app('Private')
        r1 = self.client.app.create(app)
        self.assert_status_201(r1)

        r2 = self.client.app.get_one(self.client_name, app['name'])
        self.assertDictEqual(r1.json(), r2.json())
        r = self.client.app.get_list(self.client_name)
        self.assert_list_length(r, 1)
        r = self.client.app.get_member(self.client_name, app['name'], 'admin')
        self.assert_status_200(r)
        r = self.client.app.get_member_list(self.client_name, app['name'])
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = internal_user.app.get_one(self.client_name, app['name'])
        self.assert_status_404(r3)
        r4 = internal_user.app.get_list(self.client_name)
        self.assert_list_length(r4, 0)
        r5 = internal_user.app.get_member(self.client_name, app['name'], 'admin')
        self.assert_status_404(r5)
        r = internal_user.app.get_member_list(self.client_name, app['name'])
        self.assert_status_404(r)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r6 = anonymous_user.app.get_one(self.client_name, app['name'])
        self.assert_status_404(r6)
        r7 = anonymous_user.app.get_list(self.client_name)
        self.assert_list_length(r7, 0)
        r8 = anonymous_user.app.get_member(self.client_name, app['name'], 'admin')
        self.assert_status_404(r8)
        r = anonymous_user.app.get_member_list(self.client_name, app['name'])
        self.assert_status_404(r)

    def test_internal_can_view_internal_app(self):
        app = self.generate_app('Internal')
        r1 = self.client.app.create(app)
        self.assert_status_201(r1)

        r2 = self.client.app.get_one(self.client_name, app['name'])
        self.assertDictEqual(r1.json(), r2.json())
        r = self.client.app.get_list(self.client_name)
        self.assert_list_length(r, 1)
        r = self.client.app.get_member(self.client_name, app['name'], 'admin')
        self.assert_status_200(r)
        r = self.client.app.get_member_list(self.client_name, app['name'])
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = internal_user.app.get_one(self.client_name, app['name'])
        self.assert_status_200(r3)
        r4 = internal_user.app.get_list(self.client_name)
        self.assert_list_length(r4, 1)
        r5 = internal_user.app.get_member(self.client_name, app['name'], 'admin')
        self.assert_status_200(r5)
        r = internal_user.app.get_member_list(self.client_name, app['name'])
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r6 = anonymous_user.app.get_one(self.client_name, app['name'])
        self.assert_status_404(r6)
        r7 = anonymous_user.app.get_list(self.client_name)
        self.assert_list_length(r7, 0)
        r8 = anonymous_user.app.get_member(self.client_name, app['name'], 'admin')
        self.assert_status_404(r8)
        r = anonymous_user.app.get_member_list(self.client_name, app['name'])
        self.assert_status_404(r)

    def test_anonymous_can_view_public_app(self):
        app = self.generate_app('Public')
        r1 = self.client.app.create(app)
        self.assert_status_201(r1)

        r2 = self.client.app.get_one(self.client_name, app['name'])
        self.assertDictEqual(r1.json(), r2.json())
        r = self.client.app.get_list(self.client_name)
        self.assert_list_length(r, 1)
        r = self.client.app.get_member(self.client_name, app['name'], 'admin')
        self.assert_status_200(r)
        r = self.client.app.get_member_list(self.client_name, app['name'])
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = internal_user.app.get_one(self.client_name, app['name'])
        self.assert_status_200(r3)
        r4 = internal_user.app.get_list(self.client_name)
        self.assert_list_length(r4, 1)
        r5 = internal_user.app.get_member(self.client_name, app['name'], 'admin')
        self.assert_status_200(r5)
        r = internal_user.app.get_member_list(self.client_name, app['name'])
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r6 = anonymous_user.app.get_one(self.client_name, app['name'])
        self.assert_status_200(r6)
        r7 = anonymous_user.app.get_list(self.client_name)
        self.assert_list_length(r7, 1)
        r8 = anonymous_user.app.get_member(self.client_name, app['name'], 'admin')
        self.assert_status_200(r8)
        r = anonymous_user.app.get_member_list(self.client_name, app['name'])
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

    def test_anonymous_can_not_modify_app(self):
        app = self.generate_app('Public')
        r1 = self.client.app.create(app)
        self.assert_status_201(r1)

        r2 = self.client.app.get_one(self.client_name, app['name'])
        self.assertDictEqual(r1.json(), r2.json())

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = internal_user.app.get_one(self.client_name, app['name'])
        self.assert_status_200(r3)
        r4 = internal_user.app.get_list(self.client_name)
        self.assert_list_length(r4, 1)
        r5 = internal_user.app.modify(self.client_name, app['name'], {'visibility': 'Private'})
        self.assert_status_403(r5)
        r6 = internal_user.app.modify(self.client_name, app['name'] + 'xyz', {'visibility': 'Private'})
        self.assert_status_404(r6)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r7 = anonymous_user.app.modify(self.client_name, app['name'], {'visibility': 'Private'})
        self.assert_status_403(r7)

    def test_admin_has_all_permissions(self):
        pass

    def test_collaborator_permissions(self):
        pass

    def test_member_permissions(self):
        pass

    def test_anonymous_permissions(self):
        pass
