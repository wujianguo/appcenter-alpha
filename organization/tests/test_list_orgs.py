from client.api import Api
from client.client import UnitTestClient
from util.tests.case import BaseTestCase


class OrganizationListTest(BaseTestCase):

    def create_org(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.google_org()

        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)

        org_name = org['name']
        return api.get_org_api(org_name)

    def test_empty_orgs(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        r = api.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 0)

    def test_less_than_one_page(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        user_api = api.get_user_api()
        number = 6
        for i in range(number):
            org = self.generate_org(i)
            r = user_api.create_org(org)
            self.assert_status_201(r)
        r = user_api.get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, number)

    def xtest_more_than_one_page(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        user_api = api.get_user_api()
        number = 36
        org_list = []
        for i in range(number):
            org = self.generate_org(i)
            org_list.append(org)
            r = user_api.create_org(org)
            self.assert_status_201(r)

        r = user_api.get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 10)
        resp_org_list = self.get_resp_list(r)
        for i in range(10):
            self.assertEqual(resp_org_list[i], org_list[i])
            
        r = user_api.get_org_list(top=10, skip=10)
        self.assert_status_200(r)
        self.assert_list_length(r, 10)
        resp_org_list = self.get_resp_list(r)
        for i in range(10):
            self.assertEqual(resp_org_list[i], org_list[i+10])

        r = user_api.get_org_list(top=20, skip=10)
        self.assert_status_200(r)
        self.assert_list_length(r, 10)
        resp_org_list = self.get_resp_list(r)
        for i in range(10):
            self.assertEqual(resp_org_list[i], org_list[i+20])

        r = user_api.get_org_list(top=30, skip=10)
        self.assert_status_200(r)
        self.assert_list_length(r, 6)
        resp_org_list = self.get_resp_list(r)
        for i in range(6):
            self.assertEqual(resp_org_list[i], org_list[i+30])

    def test_order_by(self):
        pass

    def xtest_multi_org_multi_member(self):
        larry: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org1 = self.generate_org(1, 'Public')
        larry.get_user_api().create_org(org1)
        org2 = self.generate_org(2, 'Private')
        larry.get_user_api().create_org(org2)
        org3 = self.generate_org(3, 'Private')
        larry.get_user_api().create_org(org3)
        org4 = self.generate_org(4, 'Internal')
        larry.get_user_api().create_org(org4)

        bill: Api = Api(UnitTestClient('/api'), 'BillGates', True)
        org11 = self.generate_org(11, 'Public')
        bill.get_user_api().create_org(org11)
        org12 = self.generate_org(12, 'Private')
        bill.get_user_api().create_org(org12)
        org13 = self.generate_org(13, 'Private')
        bill.get_user_api().create_org(org13)
        org14 = self.generate_org(14, 'Internal')
        bill.get_user_api().create_org(org14)

        mark: Api = Api(UnitTestClient('/api'), 'Mark', True)

        larry.get_org_api(org1['name']).add_member(bill.client.username, 'Member')
        larry.get_org_api(org2['name']).add_member(bill.client.username, 'Member')

        bill.get_org_api(org11['name']).add_member(larry.client.username, 'Member')
        bill.get_org_api(org12['name']).add_member(larry.client.username, 'Member')

        bill.get_org_api(org11['name']).add_member(mark.client.username, 'Member')
        bill.get_org_api(org12['name']).add_member(mark.client.username, 'Member')

        r = larry.get_user_api().get_org_list()
        self.assert_list_length(r, 6)
        
        r = bill.get_user_api().get_org_list()
        self.assert_list_length(r, 6)

        r = mark.get_user_api().get_org_list()
        self.assert_list_length(r, 5)

        anonymous: Api = Api(UnitTestClient('/api'))
        r = anonymous.get_user_api().get_org_list()
        self.assert_list_length(r, 2)

    # def test_member_can_view_private(self):
    #     pass

    # def test_login_user_can_view_internal(self):
    #     pass

    # def test_anonymous_can_view_public(self):
    #     pass
