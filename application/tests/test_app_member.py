from util.tests.client import ApiClient, UnitTestClient
from util.tests.case import BaseTestCase


class ApplicationMemberTest(BaseTestCase):

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

    def test_add_member(self):
        app = self.generate_app()
        r1 = self.client.app.create(app)
        self.assert_status_201(r1)
        name = app['name']

        r2 = self.client.app.get_one(self.client_name, name)
        self.assertDictEqual(r1.json(), r2.json())

        r = self.client.app.get_member(self.client_name, name, 'xyz')
        self.assert_status_404(r)

        jack: ApiClient = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = jack.app.get_one(self.client_name, name)
        self.assert_status_404(r3)

        member = {'username': 'jack', 'role': 'xyz'}
        r = self.client.app.add_member(self.client_name, name, member)
        self.assert_status_400(r)
        member = {'username': 'jackxxx', 'role': 'Developer'}
        r = self.client.app.add_member(self.client_name, name, member)
        self.assert_status_400(r)
        member = {'username': 'jack', 'role': 'Developer'}
        r4 = self.client.app.add_member(self.client_name, name, member)
        self.assert_status_201(r4)
        r5 = self.client.app.get_member(self.client_name, name, member['username'])
        self.assert_status_200(r5)
        self.assertEqual(r5.json()['username'], member['username'])
        self.assertEqual(r5.json()['role'], member['role'])
        r = self.client.app.add_member(self.client_name, name, member)
        self.assert_status_400(r)
        r6 = jack.app.get_one(self.client_name, name)
        self.assert_status_200(r6)
        self.assertEqual(r6.json()['role'], member['role'])

    def test_modify_member_role(self):
        app = self.generate_app()
        r1 = self.client.app.create(app)
        self.assert_status_201(r1)
        name = app['name']

        r2 = self.client.app.get_one(self.client_name, name)
        self.assertDictEqual(r1.json(), r2.json())

        r = self.client.app.change_member_role(self.client_name, name, 'admin', 'xyz')
        self.assert_status_400(r)

        r = self.client.app.change_member_role(self.client_name, name, 'admin', 'Developer')
        self.assert_status_403(r)

        jack: ApiClient = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = jack.app.get_one(self.client_name, name)
        self.assert_status_404(r3)

        member = {'username': 'jack', 'role': 'Manager'}
        r4 = self.client.app.add_member(self.client_name, name, member)
        self.assert_status_201(r4)
        r5 = jack.app.get_one(self.client_name, name)
        self.assertEqual(r5.json()['role'], member['role'])
        r = self.client.app.change_member_role(self.client_name, name, 'admin', 'Developer')
        self.assert_status_200(r)
        r6 = self.client.app.change_or_set_icon(self.client_name, name)
        self.assert_status_404(r6)
        r6 = self.client.app.change_or_set_icon('jack', name)
        self.assert_status_403(r6)
        # todo: Collaborator can upload package
        r = jack.app.change_member_role('jack', name, 'admin', 'Manager')
        self.assert_status_200(r)

        r7 = self.client.app.change_member_role('jack', name, member['username'], 'Viewer')
        self.assert_status_200(r7)
        # todo: Member can not upload package

    def test_remove_member(self):
        app = self.generate_app()
        r1 = self.client.app.create(app)
        self.assert_status_201(r1)
        name = app['name']

        r2 = self.client.app.get_one(self.client_name, name)
        self.assertDictEqual(r1.json(), r2.json())
        r = self.client.app.remove_member(self.client_name, name, 'admin')
        self.assert_status_403(r)

        jack: ApiClient = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = jack.app.get_one(self.client_name, name)
        self.assert_status_404(r3)

        member = {'username': 'jack', 'role': 'Manager'}
        r4 = self.client.app.add_member(self.client_name, name, member)
        self.assert_status_201(r4)
        r5 = self.client.app.get_member(self.client_name, name, member['username'])
        self.assert_status_200(r5)

        r6 = jack.app.get_one(self.client_name, name)
        self.assert_status_200(r6)

        r = jack.app.remove_member(self.client_name, name, 'admin')
        self.assert_status_204(r)

        r8 = self.client.app.get_one(self.client_name, name)
        self.assert_status_404(r8)

    def test_multi_member_multi_app(self):
        admin = self.client
        anonymous_user = ApiClient(UnitTestClient('/api/'))

        app1 = self.generate_app('Private')
        r = admin.app.create(app1)
        self.assert_status_201(r)

        app2 = self.generate_app('Internal')
        r = admin.app.create(app2)
        self.assert_status_201(r)

        app3 = self.generate_app('Public')
        r = admin.app.create(app3)
        self.assert_status_201(r)

        jack: ApiClient = ApiClient(UnitTestClient('/api/', 'jack'))
        paul: ApiClient = ApiClient(UnitTestClient('/api/', 'paul'))

        app4 = self.generate_app('Private')
        r = jack.app.create(app4)
        self.assert_status_201(r)

        app5 = self.generate_app('Internal')
        r = jack.app.create(app5)
        self.assert_status_201(r)

        app6 = self.generate_app('Public')
        r = jack.app.create(app6)
        self.assert_status_201(r)


        r = admin.app.get_list('admin')
        self.assert_list_length(r, 3)

        r = admin.app.get_list('jack')
        self.assert_list_length(r, 2)

        r = jack.app.get_list('admin')
        self.assert_list_length(r, 2)

        r = jack.app.get_list('jack')
        self.assert_list_length(r, 3)

        r = paul.app.get_list('admin')
        self.assert_list_length(r, 2)

        r = paul.app.get_list('jack')
        self.assert_list_length(r, 2)

        r = anonymous_user.app.get_list('admin')
        self.assert_list_length(r, 1)

        r = anonymous_user.app.get_list('jack')
        self.assert_list_length(r, 1)

        paul2: ApiClient = ApiClient(UnitTestClient('/api/', 'paul2'))
        paul3: ApiClient = ApiClient(UnitTestClient('/api/', 'paul3'))

        admin.app.add_member('admin', app1['name'], {'username': 'jack', 'role': 'Developer'})

        # todo
        admin.app.add_member('admin', app2['name'], {'username': 'paul2', 'role': 'Admin'})
        admin.app.add_member('admin', app2['name'], {'username': 'paul3', 'role': 'Member'})

        r = admin.app.get_list('admin')
        self.assert_list_length(r, 3)

        r = admin.app.get_list('jack')
        self.assert_list_length(r, 2)

        r = jack.app.get_list('admin')
        self.assert_list_length(r, 3)

        r = jack.app.get_list('jack')
        self.assert_list_length(r, 3)

        r = paul.app.get_list('admin')
        self.assert_list_length(r, 2)

        r = paul.app.get_list('jack')
        self.assert_list_length(r, 2)

        r = anonymous_user.app.get_list('admin')
        self.assert_list_length(r, 1)

        r = anonymous_user.app.get_list('jack')
        self.assert_list_length(r, 1)
