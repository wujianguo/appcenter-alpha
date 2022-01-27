from util.tests.client import ApiClient, UnitTestClient
from util.tests.case import BaseTestCase


class OrganizationPermissionTest(BaseTestCase):

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
        self.assert_status_201(r1)

        org2 = self.generate_org('Internal')
        r2 = self.client.org.create(org2)
        self.assert_status_201(r2)

        org3 = self.generate_org('Public')
        r3 = self.client.org.create(org3)
        self.assert_status_201(r3)

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r4 = internal_user.org.get_list()
        self.assert_list_length(r4, 2)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r5 = anonymous_user.org.get_list()
        self.assert_list_length(r5, 1)

    def test_member_can_view_private_org(self):
        org = self.generate_org('Private')
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())
        r = self.client.org.get_list()
        self.assert_list_length(r, 1)
        r = self.client.org.get_member(org['name'], 'admin')
        self.assert_status_200(r)
        r = self.client.org.get_member_list(org['name'])
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = internal_user.org.get_one(org['name'])
        self.assert_status_404(r3)
        r4 = internal_user.org.get_list()
        self.assert_list_length(r4, 0)
        r5 = internal_user.org.get_member(org['name'], 'admin')
        self.assert_status_404(r5)
        r = internal_user.org.get_member_list(org['name'])
        self.assert_status_404(r)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r6 = anonymous_user.org.get_one(org['name'])
        self.assert_status_404(r6)
        r7 = anonymous_user.org.get_list()
        self.assert_list_length(r7, 0)
        r8 = anonymous_user.org.get_member(org['name'], 'admin')
        self.assert_status_404(r8)
        r = anonymous_user.org.get_member_list(org['name'])
        self.assert_status_404(r)

    def test_internal_can_view_internal_org(self):
        org = self.generate_org('Internal')
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())
        r = self.client.org.get_list()
        self.assert_list_length(r, 1)
        r = self.client.org.get_member(org['name'], 'admin')
        self.assert_status_200(r)
        r = self.client.org.get_member_list(org['name'])
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = internal_user.org.get_one(org['name'])
        self.assert_status_200(r3)
        r4 = internal_user.org.get_list()
        self.assert_list_length(r4, 1)
        r5 = internal_user.org.get_member(org['name'], 'admin')
        self.assert_status_200(r5)
        r = internal_user.org.get_member_list(org['name'])
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r6 = anonymous_user.org.get_one(org['name'])
        self.assert_status_404(r6)
        r7 = anonymous_user.org.get_list()
        self.assert_list_length(r7, 0)
        r8 = anonymous_user.org.get_member(org['name'], 'admin')
        self.assert_status_404(r8)
        r = anonymous_user.org.get_member_list(org['name'])
        self.assert_status_404(r)

    def test_anonymous_can_view_public_org(self):
        org = self.generate_org('Public')
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())
        r = self.client.org.get_list()
        self.assert_list_length(r, 1)
        r = self.client.org.get_member(org['name'], 'admin')
        self.assert_status_200(r)
        r = self.client.org.get_member_list(org['name'])
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = internal_user.org.get_one(org['name'])
        self.assert_status_200(r3)
        r4 = internal_user.org.get_list()
        self.assert_list_length(r4, 1)
        r5 = internal_user.org.get_member(org['name'], 'admin')
        self.assert_status_200(r5)
        r = internal_user.org.get_member_list(org['name'])
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r6 = anonymous_user.org.get_one(org['name'])
        self.assert_status_200(r6)
        r7 = anonymous_user.org.get_list()
        self.assert_list_length(r7, 1)
        r8 = anonymous_user.org.get_member(org['name'], 'admin')
        self.assert_status_200(r8)
        r = anonymous_user.org.get_member_list(org['name'])
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

    def test_anonymous_can_not_modify_org(self):
        org = self.generate_org('Public')
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())

        internal_user = ApiClient(UnitTestClient('/api/', 'jack'))
        r3 = internal_user.org.get_one(org['name'])
        self.assert_status_200(r3)
        r4 = internal_user.org.get_list()
        self.assert_list_length(r4, 1)
        r5 = internal_user.org.modify(org['name'], {'visibility': 'Private'})
        self.assert_status_403(r5)
        r6 = internal_user.org.modify(org['name'] + 'xyz', {'visibility': 'Private'})
        self.assert_status_404(r6)

        anonymous_user = ApiClient(UnitTestClient('/api/'))
        r7 = anonymous_user.org.modify(org['name'], {'visibility': 'Private'})
        self.assert_status_403(r7)

    def test_admin_has_all_permissions(self):
        pass

    def test_collaborator_permissions(self):
        pass

    def test_member_permissions(self):
        pass

    def test_anonymous_permissions(self):
        pass
