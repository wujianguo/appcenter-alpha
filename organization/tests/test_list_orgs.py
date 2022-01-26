from django.test import TestCase
from util.tests.client import ApiClient, UnitTestClient

class OrganizationListTest(TestCase):

    def setUp(self):
        self.client: ApiClient = ApiClient(UnitTestClient('/api/', 'admin'))
        self.org_index = 0

    def generate_org(self):
        self.org_index += 1
        org = {
            'name': 'org_name_' + str(self.org_index),
            'display_name': 'org_display_name_' + str(self.org_index),
            'visibility': 'Private'
        }
        return org

    def test_empty_orgs(self):
        r = self.client.org.get_list()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), [])

    def test_less_than_one_page(self):
        for i in range(6):
            org = self.generate_org()
            r = self.client.org.create(org)
            self.assertEqual(r.status_code, 201)
        r1 = self.client.org.get_list()
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(len(r1.json()), 6)

    def test_more_than_one_page(self):
        pass

    def test_last_page(self):
        pass

    def test_filter(self):
        pass

    def test_order_by(self):
        pass



    # def test_member_can_view_private(self):
    #     pass

    # def test_login_user_can_view_internal(self):
    #     pass

    # def test_anonymous_can_view_public(self):
    #     pass
