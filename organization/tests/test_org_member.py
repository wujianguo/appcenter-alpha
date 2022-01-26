from django.test import TestCase
from util.tests.client import ApiClient, UnitTestClient


class OrganizationMemberTest(TestCase):

    def setUp(self):
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
        self.assertEqual(r1.status_code, 201)
        name = org['name']

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())

        r = self.client.org.get_member(name, 'xyz')
        self.assertEqual(r.status_code, 404)

        jack: ApiClient = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = jack.org.get_one(org['name'])
        self.assertEqual(r3.status_code, 404)

        member = {'username': 'jack', 'role': 'xyz'}
        r = self.client.org.add_member(name, member)
        self.assertEqual(r.status_code, 400)
        member = {'username': 'jack', 'role': 'Collaborator'}
        r4 = self.client.org.add_member(name, member)
        self.assertEqual(r4.status_code, 201)
        r5 = self.client.org.get_member(name, member['username'])
        self.assertEqual(r5.status_code, 200)
        self.assertEqual(r5.json()['username'], member['username'])
        self.assertEqual(r5.json()['role'], member['role'])
        r = self.client.org.add_member(name, member)
        self.assertEqual(r.status_code, 400)
        r6 = jack.org.get_one(org['name'])
        self.assertEqual(r6.status_code, 200)
        self.assertEqual(r6.json()['role'], member['role'])

    def test_modify_member_role(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assertEqual(r1.status_code, 201)
        name = org['name']

        r2 = self.client.org.get_one(name)
        self.assertDictEqual(r1.json(), r2.json())

        r = self.client.org.change_member_role(name, 'admin', 'Collaborator')
        self.assertEqual(r.status_code, 403)

        jack: ApiClient = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = jack.org.get_one(org['name'])
        self.assertEqual(r3.status_code, 404)

        member = {'username': 'jack', 'role': 'Admin'}
        r4 = self.client.org.add_member(name, member)
        self.assertEqual(r4.status_code, 201)
        r5 = jack.org.get_one(name)
        self.assertEqual(r5.json()['role'], member['role'])
        r = self.client.org.change_member_role(name, 'admin', 'Collaborator')
        self.assertEqual(r.status_code, 200)
        r6 = self.client.org.change_or_set_icon(name)
        self.assertEqual(r6.status_code, 403)
        # todo: Collaborator can upload package
        r = jack.org.change_member_role(name, 'admin', 'Admin')
        self.assertEqual(r.status_code, 200)

        r7 = self.client.org.change_member_role(name, member['username'], 'Member')
        self.assertEqual(r7.status_code, 200)
        # todo: Member can not upload package

    def test_remove_member(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assertEqual(r1.status_code, 201)
        name = org['name']

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())
        r = self.client.org.remove_member(org['name'], 'admin')
        self.assertEqual(r.status_code, 403)

        jack: ApiClient = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = jack.org.get_one(org['name'])
        self.assertEqual(r3.status_code, 404)

        member = {'username': 'jack', 'role': 'Admin'}
        r4 = self.client.org.add_member(name, member)
        self.assertEqual(r4.status_code, 201)
        r5 = self.client.org.get_member(name, member['username'])
        self.assertEqual(r5.status_code, 200)

        r6 = jack.org.get_one(org['name'])
        self.assertEqual(r6.status_code, 200)

        r = jack.org.remove_member(org['name'], 'admin')
        self.assertEqual(r.status_code, 204)

        r8 = self.client.org.get_one(org['name'])
        self.assertEqual(r8.status_code, 404)
