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

    def test_more_than_one_page(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        anonymous: Api = Api(UnitTestClient('/api'))
        user_api = api.get_user_api()
        number = 36
        org_list = []
        for i in range(number):
            org = self.generate_org(i, 'Public')
            org_list.append(org)
            r = user_api.create_org(org)
            self.assert_status_201(r)

        r = user_api.get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 10)
        resp_org_list = self.get_resp_list(r)
        r = anonymous.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 10)
        resp_org_list2 = self.get_resp_list(r)
        for i in range(10):
            self.assert_partial_dict_equal(resp_org_list[i], org_list[i], ['name'])
            self.assert_partial_dict_equal(resp_org_list2[i], org_list[i], ['name'])
            
        r = user_api.get_org_list(top=10, skip=10)
        self.assert_status_200(r)
        self.assert_list_length(r, 10)
        resp_org_list = self.get_resp_list(r)
        r = anonymous.get_user_api().get_org_list(top=10, skip=10)
        self.assert_status_200(r)
        self.assert_list_length(r, 10)
        resp_org_list2 = self.get_resp_list(r)
        for i in range(10):
            self.assert_partial_dict_equal(resp_org_list[i], org_list[i+10], ['name'])
            self.assert_partial_dict_equal(resp_org_list2[i], org_list[i+10], ['name'])

        r = user_api.get_org_list(top=10, skip=20)
        self.assert_status_200(r)
        self.assert_list_length(r, 10)
        resp_org_list = self.get_resp_list(r)
        r = anonymous.get_user_api().get_org_list(top=10, skip=20)
        self.assert_status_200(r)
        self.assert_list_length(r, 10)
        resp_org_list2 = self.get_resp_list(r)
        for i in range(10):
            self.assert_partial_dict_equal(resp_org_list[i], org_list[i+20], ['name'])
            self.assert_partial_dict_equal(resp_org_list2[i], org_list[i+20], ['name'])

        r = user_api.get_org_list(top=10, skip=30)
        self.assert_status_200(r)
        self.assert_list_length(r, 6)
        resp_org_list = self.get_resp_list(r)
        r = anonymous.get_user_api().get_org_list(top=10, skip=30)
        self.assert_status_200(r)
        self.assert_list_length(r, 6)
        resp_org_list2 = self.get_resp_list(r)
        for i in range(6):
            self.assert_partial_dict_equal(resp_org_list[i], org_list[i+30], ['name'])
            self.assert_partial_dict_equal(resp_org_list2[i], org_list[i+30], ['name'])

        r = user_api.get_org_list(top=10, skip=35)
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = anonymous.get_user_api().get_org_list(top=10, skip=35)
        self.assert_status_200(r)
        self.assert_list_length(r, 1)

        r = user_api.get_org_list(top=10, skip=36)
        self.assert_status_200(r)
        self.assert_list_length(r, 0)
        r = anonymous.get_user_api().get_org_list(top=10, skip=36)
        self.assert_status_200(r)
        self.assert_list_length(r, 0)

        r = user_api.get_org_list(top=10, skip=40)
        self.assert_status_200(r)
        self.assert_list_length(r, 0)
        r = anonymous.get_user_api().get_org_list(top=10, skip=40)
        self.assert_status_200(r)
        self.assert_list_length(r, 0)

    def test_multi_org_multi_member(self):
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
        org21 = self.generate_org(21, 'Public')
        mark.get_user_api().create_org(org21)

        larry.get_org_api(org1['name']).add_member(bill.client.username, 'Member')
        larry.get_org_api(org2['name']).add_member(bill.client.username, 'Member')

        bill.get_org_api(org11['name']).add_member(larry.client.username, 'Member')
        bill.get_org_api(org12['name']).add_member(larry.client.username, 'Member')

        bill.get_org_api(org11['name']).add_member(mark.client.username, 'Member')
        bill.get_org_api(org12['name']).add_member(mark.client.username, 'Member')

        r = larry.get_user_api().get_org_list()
        self.assert_list_length(r, 8)
        resp_list = self.get_resp_list(r)
        expect_org_info = {
            org1['name']: 'Admin',
            org2['name']: 'Admin',
            org3['name']: 'Admin',
            org4['name']: 'Admin',
            org11['name']: 'Member',
            org12['name']: 'Member',
            org14['name']: None,
            org21['name']: None
        }
        resp_org_info = dict([(org['name'], org.get('role', None)) for org in resp_list])
        self.assertDictEqual(resp_org_info, expect_org_info)

        r = bill.get_user_api().get_org_list()
        self.assert_list_length(r, 8)
        resp_list = self.get_resp_list(r)
        expect_org_info = {
            org11['name']: 'Admin',
            org12['name']: 'Admin',
            org13['name']: 'Admin',
            org14['name']: 'Admin',
            org1['name']: 'Member',
            org2['name']: 'Member',
            org4['name']: None,
            org21['name']: None
        }
        resp_org_info = dict([(org['name'], org.get('role', None)) for org in resp_list])
        self.assertDictEqual(resp_org_info, expect_org_info)

        r = mark.get_user_api().get_org_list()
        self.assert_list_length(r, 6)
        resp_list = self.get_resp_list(r)
        expect_org_info = {
            org1['name']: None,
            org4['name']: None,
            org11['name']: 'Member',
            org12['name']: 'Member',
            org21['name']: 'Admin',
            org14['name']: None
        }
        resp_org_info = dict([(org['name'], org.get('role', None)) for org in resp_list])
        self.assertDictEqual(resp_org_info, expect_org_info)

        anonymous: Api = Api(UnitTestClient('/api'))
        r = anonymous.get_user_api().get_org_list()
        self.assert_list_length(r, 3)
        resp_list = self.get_resp_list(r)
        expect_org_info = {
            org1['name']: None,
            org11['name']: None,
            org21['name']: None
        }
        resp_org_info = dict([(org['name'], org.get('role', None)) for org in resp_list])
        self.assertDictEqual(resp_org_info, expect_org_info)

    def test_order_by(self):
        pass

    def test_filter(self):
        pass

    def test_get_public_org_permission(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.generate_org(1, 'Public')
        org_name = org['name']
        api.get_user_api().create_org(org)
        
        bill: Api = Api(UnitTestClient('/api'), 'BillGates', True)
        api.get_org_api(org_name).add_member('BillGates', 'Admin')
        r = bill.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = bill.get_org_api(org_name).get_org()
        self.assert_status_200(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Collaborator')
        r = bill.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = bill.get_org_api(org_name).get_org()
        self.assert_status_200(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Member')
        r = bill.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = bill.get_org_api(org_name).get_org()
        self.assert_status_200(r)

        mark: Api = Api(UnitTestClient('/api'), 'MarkZuckerberg', True)
        r = mark.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = mark.get_org_api(org_name).get_org()
        self.assert_status_200(r)

        anonymous: Api = Api(UnitTestClient('/api'))
        r = anonymous.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = anonymous.get_org_api(org_name).get_org()
        self.assert_status_200(r)

    def test_get_internal_org_permission(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.generate_org(1, 'Internal')
        org_name = org['name']
        api.get_user_api().create_org(org)
        
        bill: Api = Api(UnitTestClient('/api'), 'BillGates', True)
        api.get_org_api(org_name).add_member('BillGates', 'Admin')
        r = bill.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = bill.get_org_api(org_name).get_org()
        self.assert_status_200(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Collaborator')
        r = bill.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = bill.get_org_api(org_name).get_org()
        self.assert_status_200(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Member')
        r = bill.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = bill.get_org_api(org_name).get_org()
        self.assert_status_200(r)

        mark: Api = Api(UnitTestClient('/api'), 'MarkZuckerberg', True)
        r = mark.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = mark.get_org_api(org_name).get_org()
        self.assert_status_200(r)

        anonymous: Api = Api(UnitTestClient('/api'))
        r = anonymous.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 0)
        r = anonymous.get_org_api(org_name).get_org()
        self.assert_status_404(r)

    def test_get_private_org_permission(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.generate_org(1, 'Private')
        org_name = org['name']
        api.get_user_api().create_org(org)
        
        bill: Api = Api(UnitTestClient('/api'), 'BillGates', True)
        api.get_org_api(org_name).add_member('BillGates', 'Admin')
        r = bill.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = bill.get_org_api(org_name).get_org()
        self.assert_status_200(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Collaborator')
        r = bill.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = bill.get_org_api(org_name).get_org()
        self.assert_status_200(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Member')
        r = bill.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 1)
        r = bill.get_org_api(org_name).get_org()
        self.assert_status_200(r)

        mark: Api = Api(UnitTestClient('/api'), 'MarkZuckerberg', True)
        r = mark.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 0)
        r = mark.get_org_api(org_name).get_org()
        self.assert_status_404(r)

        anonymous: Api = Api(UnitTestClient('/api'))
        r = anonymous.get_user_api().get_org_list()
        self.assert_status_200(r)
        self.assert_list_length(r, 0)
        r = anonymous.get_org_api(org_name).get_org()
        self.assert_status_404(r)
