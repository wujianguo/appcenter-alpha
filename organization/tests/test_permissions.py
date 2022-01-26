from django.test import TestCase, tag
from util.tests.client import ApiClient, UnitTestClient

class OrganizationPermissionTest(TestCase):

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

    def test_org_visibility(self):
        org1 = self.generate_org('Private')
        r1 = self.client.org.create(org1)
        self.assertEqual(r1.status_code, 201)

        org2 = self.generate_org('Internal')
        r2 = self.client.org.create(org2)
        self.assertEqual(r2.status_code, 201)

        org3 = self.generate_org('Public')
        r3 = self.client.org.create(org3)
        self.assertEqual(r3.status_code, 201)

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r4 = internal_user.org.get_list()
        self.assertEqual(len(r4.json()), 2)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r5 = anonymous_user.org.get_list()
        self.assertEqual(len(r5.json()), 1)

    def test_member_can_view_private_org(self):
        org = self.generate_org('Private')
        r1 = self.client.org.create(org)
        self.assertEqual(r1.status_code, 201)

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())
        r = self.client.org.get_list()
        self.assertEqual(len(r.json()), 1)
        r = self.client.org.get_member(org['name'], 'admin')
        self.assertEqual(r.status_code, 200)
        r = self.client.org.get_member_list(org['name'])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = internal_user.org.get_one(org['name'])
        self.assertEqual(r3.status_code, 404)
        r4 = internal_user.org.get_list()
        self.assertEqual(len(r4.json()), 0)
        r5 = internal_user.org.get_member(org['name'], 'admin')
        self.assertEqual(r5.status_code, 404)
        r = internal_user.org.get_member_list(org['name'])
        self.assertEqual(r.status_code, 404)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r6 = anonymous_user.org.get_one(org['name'])
        self.assertEqual(r6.status_code, 404)
        r7 = anonymous_user.org.get_list()
        self.assertEqual(len(r7.json()), 0)
        r8 = anonymous_user.org.get_member(org['name'], 'admin')
        self.assertEqual(r8.status_code, 404)
        r = anonymous_user.org.get_member_list(org['name'])
        self.assertEqual(r.status_code, 404)


    def test_internal_can_view_internal_org(self):
        org = self.generate_org('Internal')
        r1 = self.client.org.create(org)
        self.assertEqual(r1.status_code, 201)

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())
        r = self.client.org.get_list()
        self.assertEqual(len(r.json()), 1)
        r = self.client.org.get_member(org['name'], 'admin')
        self.assertEqual(r.status_code, 200)
        r = self.client.org.get_member_list(org['name'])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = internal_user.org.get_one(org['name'])
        self.assertEqual(r3.status_code, 200)
        r4 = internal_user.org.get_list()
        self.assertEqual(len(r4.json()), 1)
        r5 = internal_user.org.get_member(org['name'], 'admin')
        self.assertEqual(r5.status_code, 200)
        r = internal_user.org.get_member_list(org['name'])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r6 = anonymous_user.org.get_one(org['name'])
        self.assertEqual(r6.status_code, 404)
        r7 = anonymous_user.org.get_list()
        self.assertEqual(len(r7.json()), 0)
        r8 = anonymous_user.org.get_member(org['name'], 'admin')
        self.assertEqual(r8.status_code, 404)
        r = anonymous_user.org.get_member_list(org['name'])
        self.assertEqual(r.status_code, 404)

    def test_anonymous_can_view_public_org(self):
        org = self.generate_org('Public')
        r1 = self.client.org.create(org)
        self.assertEqual(r1.status_code, 201)

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())
        r = self.client.org.get_list()
        self.assertEqual(len(r.json()), 1)
        r = self.client.org.get_member(org['name'], 'admin')
        self.assertEqual(r.status_code, 200)
        r = self.client.org.get_member_list(org['name'])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = internal_user.org.get_one(org['name'])
        self.assertEqual(r3.status_code, 200)
        r4 = internal_user.org.get_list()
        self.assertEqual(len(r4.json()), 1)
        r5 = internal_user.org.get_member(org['name'], 'admin')
        self.assertEqual(r5.status_code, 200)
        r = internal_user.org.get_member_list(org['name'])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r6 = anonymous_user.org.get_one(org['name'])
        self.assertEqual(r6.status_code, 200)
        r7 = anonymous_user.org.get_list()
        self.assertEqual(len(r7.json()), 1)
        r8 = anonymous_user.org.get_member(org['name'], 'admin')
        self.assertEqual(r8.status_code, 200)
        r = anonymous_user.org.get_member_list(org['name'])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

    def test_anonymous_can_not_modify_org(self):
        org = self.generate_org('Public')
        r1 = self.client.org.create(org)
        self.assertEqual(r1.status_code, 201)

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = internal_user.org.get_one(org['name'])
        self.assertEqual(r3.status_code, 200)
        r4 = internal_user.org.get_list()
        self.assertEqual(len(r4.json()), 1)
        r5 = internal_user.org.modify(org['name'], {'visibility': 'Private'})
        self.assertEqual(r5.status_code, 403)
        r6 = internal_user.org.modify(org['name'] + 'xyz', {'visibility': 'Private'})
        self.assertEqual(r6.status_code, 404)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r7 = anonymous_user.org.modify(org['name'], {'visibility': 'Private'})
        self.assertEqual(r7.status_code, 403)


    def test_admin_has_all_permissions(self):
        pass
