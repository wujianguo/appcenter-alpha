from util.tests.client import ApiClient
from util.tests.unit_test_client import UnitTestClient
from util.tests.case import BaseTestCase


class OrganizationMemberTest(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.client: ApiClient = ApiClient(UnitTestClient('/api/', 'admin'))
        self.org_index = 0

    def generate_org(self, visibility='Private'):
        self.org_index += 1
        org = {
            'name': 'org_name_' + str(self.org_index),
            'display_name': 'org_display_name_' + str(self.org_index),
            'visibility': visibility
        }
        return org

    def test_add_member(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)
        name = org['name']

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())

        r = self.client.org.get_member(name, 'xyz')
        self.assert_status_404(r)

        jack: ApiClient = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = jack.org.get_one(org['name'])
        self.assert_status_404(r3)

        member = {'username': 'jack', 'role': 'xyz'}
        r = self.client.org.add_member(name, member)
        self.assert_status_400(r)
        member = {'username': 'jackxxx', 'role': 'Collaborator'}
        r = self.client.org.add_member(name, member)
        self.assert_status_400(r)
        member = {'username': 'jack', 'role': 'Collaborator'}
        r4 = self.client.org.add_member(name, member)
        self.assert_status_201(r4)
        r5 = self.client.org.get_member(name, member['username'])
        self.assert_status_200(r5)
        self.assertEqual(r5.json()['username'], member['username'])
        self.assertEqual(r5.json()['role'], member['role'])
        r = self.client.org.add_member(name, member)
        self.assert_status_409(r)
        r6 = jack.org.get_one(org['name'])
        self.assert_status_200(r6)
        self.assertEqual(r6.json()['role'], member['role'])

    def test_multi_member(self):
        org = self.generate_org(visibility='Public')
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)
        name = org['name']

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())

        r = self.client.org.get_member(name, 'xyz')
        self.assert_status_404(r)

        jack: ApiClient = ApiClient(UnitTestClient('/api/', 'jack'))
        member = {'username': 'jack', 'role': 'Collaborator'}
        r4 = self.client.org.add_member(name, member)
        self.assert_status_201(r4)

        r = jack.org.get_app_list(org['name'])
        self.assert_status_200(r)

    def test_modify_member_role(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)
        name = org['name']

        r2 = self.client.org.get_one(name)
        self.assertDictEqual(r1.json(), r2.json())

        r = self.client.org.change_member_role(name, 'admin', 'xyz')
        self.assert_status_400(r)

        r = self.client.org.change_member_role(name, 'admin', 'Collaborator')
        self.assert_status_403(r)

        jack: ApiClient = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = jack.org.get_one(org['name'])
        self.assert_status_404(r3)

        member = {'username': 'jack', 'role': 'Admin'}
        r4 = self.client.org.add_member(name, member)
        self.assert_status_201(r4)
        r5 = jack.org.get_one(name)
        self.assertEqual(r5.json()['role'], member['role'])
        r = self.client.org.change_member_role(name, 'admin', 'Collaborator')
        self.assert_status_200(r)
        r6 = self.client.org.change_or_set_icon(name)
        self.assert_status_403(r6)
        # todo: Collaborator can upload package
        r = jack.org.change_member_role(name, 'admin', 'Admin')
        self.assert_status_200(r)

        r7 = self.client.org.change_member_role(name, member['username'], 'Member')
        self.assert_status_200(r7)
        # todo: Member can not upload package

    def test_remove_member(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)
        name = org['name']

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())
        r = self.client.org.remove_member(org['name'], 'admin')
        self.assert_status_403(r)

        jack: ApiClient = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = jack.org.get_one(org['name'])
        self.assert_status_404(r3)

        member = {'username': 'jack', 'role': 'Admin'}
        r4 = self.client.org.add_member(name, member)
        self.assert_status_201(r4)
        r5 = self.client.org.get_member(name, member['username'])
        self.assert_status_200(r5)

        r6 = jack.org.get_one(org['name'])
        self.assert_status_200(r6)

        r = jack.org.remove_member(org['name'], 'admin')
        self.assert_status_204(r)

        r8 = self.client.org.get_one(org['name'])
        self.assert_status_404(r8)

    def test_multi_member_multi_org(self):
        admin = self.client
        anonymous_user = ApiClient(UnitTestClient('/api/'))


        org1 = self.generate_org('Private')
        r = admin.org.create(org1)
        self.assert_status_201(r)

        org2 = self.generate_org('Internal')
        r = admin.org.create(org2)
        self.assert_status_201(r)

        org3 = self.generate_org('Public')
        r = admin.org.create(org3)
        self.assert_status_201(r)

        jack: ApiClient = ApiClient(UnitTestClient('/api/', 'jack'))
        paul: ApiClient = ApiClient(UnitTestClient('/api/', 'paul'))

        org4 = self.generate_org('Private')
        r = jack.org.create(org4)
        self.assert_status_201(r)

        org5 = self.generate_org('Internal')
        r = jack.org.create(org5)
        self.assert_status_201(r)

        org6 = self.generate_org('Public')
        r = jack.org.create(org6)
        self.assert_status_201(r)


        r = admin.org.get_list()
        self.assert_list_length(r, 5)

        r = jack.org.get_list()
        self.assert_list_length(r, 5)

        r = paul.org.get_list()
        self.assert_list_length(r, 4)

        r = anonymous_user.org.get_list()
        self.assert_list_length(r, 2)

        paul2: ApiClient = ApiClient(UnitTestClient('/api/', 'paul2'))
        paul3: ApiClient = ApiClient(UnitTestClient('/api/', 'paul3'))

        admin.org.add_member(org1['name'], {'username': 'jack', 'role': 'Collaborator'})

        # todo
        # admin.org.add_member(org2['name'], {'username': 'paul2', 'role': 'Admin'})
        # admin.org.add_member(org2['name'], {'username': 'paul3', 'role': 'Member'})

        r = jack.org.get_list()
        self.assert_list_length(r, 6)

        r = admin.org.get_list()
        self.assert_list_length(r, 5)

        r = paul.org.get_list()
        self.assert_list_length(r, 4)
