import tempfile
from client.api import Api
from client.client import UnitTestClient
from util.tests.case import BaseTestCase

class OrganizationCreateTest(BaseTestCase):

    def create_org(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.google_org()
        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)
        org_name = org['name']
        return api.get_org_api(org_name)

    def test_create_success(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.google_org()
        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)
        self.assert_partial_dict_equal(org, r.json(), ['name', 'display_name', 'visibility', 'description'])
        org_name = org['name']

        r2 = api.get_org_api(org_name).get_org()
        self.assertDictEqual(r.json(), r2.json())

        r3 = api.get_user_api().get_org_list()
        self.assertDictEqual(self.get_resp_list(r3)[0], r.json())

    def test_invalid_name(self):
        # 1. only letters, numbers, underscores or hyphens
        # 2. 0 < len(name) <= 32
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.google_org()
        org['name'] += '*'
        user_api = api.get_user_api()
        r = user_api.create_org(org)
        self.assert_status_400(r)

        max_length = 32
        org['name'] = 'a' * max_length
        r = user_api.create_org(org)
        self.assert_status_201(r)

        org['name'] = 'a' * max_length + 'a'
        r = user_api.create_org(org)
        self.assert_status_400(r)

        org['name'] = ''
        r = user_api.create_org(org)
        self.assert_status_400(r)

        del org['name']
        r = user_api.create_org(org)
        self.assert_status_400(r)

    def test_duplicate_name(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.google_org()
        api.get_user_api().create_org(org)

        org2 = self.microsoft_org()
        org2['name'] = org['name']
        r =  api.get_user_api().create_org(org2)
        self.assert_status_409(r)

    def test_required(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.google_org()
        del org['name']
        r = api.get_user_api().create_org(org)
        self.assert_status_400(r)
        
        org = self.google_org()
        del org['display_name']
        r = api.get_user_api().create_org(org)
        self.assert_status_400(r)

        org = self.google_org()
        del org['visibility']
        r = api.get_user_api().create_org(org)
        self.assert_status_400(r)

    def test_invalid_display_name(self):
        # 0 < len(display_name) <= 32
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.google_org()

        max_length = 128
        org['display_name'] = 'a' * max_length
        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)

        org['display_name'] = 'a' * max_length + 'a'
        r = api.get_user_api().create_org(org)
        self.assert_status_400(r)

        org['display_name'] = ''
        r = api.get_user_api().create_org(org)
        self.assert_status_400(r)

    def test_visibility(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.google_org()

        org['visibility'] = 'a'
        r = api.get_user_api().create_org(org)
        self.assert_status_400(r)

        allow_visibility = ['Private', 'Internal', 'Public']
        for visibility in allow_visibility:
            org = self.google_org()
            org['name'] += visibility
            org['visibility'] = visibility
            r = api.get_user_api().create_org(org)
            self.assert_status_201(r)

    def test_modify_org_name(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.google_org()

        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)
        old_value = r.json()

        org_name = org['name']

        new_name = 'new_name'
        data = {'name': new_name}
        org_api = api.get_org_api(org_name)
        r = org_api.update_org(data)
        self.assert_status_200(r)

        r = org_api.get_org()
        self.assert_status_404(r)

        r = api.get_org_api(new_name).get_org()
        self.assert_status_200(r)

        old_value['name'] = new_name
        del old_value['update_time']
        new_value = r.json()
        del new_value['update_time']
        self.assertDictEqual(new_value, old_value)

    def test_modify_invalid_name(self):
        # 1. only letters, numbers, underscores or hyphens
        # 2. 0 < len(name) <= 32
        org_api = self.create_org()

        max_length = 32
        new_name = 'a' * max_length + 'a'
        r = org_api.update_org({'name': new_name})
        self.assert_status_400(r)

        new_name = ''
        r = org_api.update_org({'name': new_name})
        self.assert_status_400(r)

        new_name = 'a' * max_length
        r = org_api.update_org({'name': new_name})
        self.assert_status_200(r)

    def test_modify_duplicate_name(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.google_org()

        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)

        org_name = org['name']
        org_api = api.get_org_api(org_name)

        name = org['name']
        r = org_api.update_org({'name': name})
        self.assert_status_200(r)

        org2 = self.microsoft_org()
        r = api.get_user_api().create_org(org2)
        self.assert_status_201(r)
        new_name = org2['name']
        r = org_api.update_org({'name': new_name})
        self.assert_status_409(r)

    def test_modify_org_display_name(self):
        org_api = self.create_org()

        max_length = 128
        display_name = 'a' * max_length
        r = org_api.update_org({'display_name': display_name})
        self.assert_status_200(r)

        display_name = 'a' * max_length + 'a'
        r = org_api.update_org({'display_name': display_name})
        self.assert_status_400(r)

        display_name = ''
        r = org_api.update_org({'display_name': display_name})
        self.assert_status_400(r)

    def test_modify_org_visibility(self):
        org_api = self.create_org()

        visibility = 'a'
        r = org_api.update_org({'visibility': visibility})
        self.assert_status_400(r)

        allow_visibility = ['Private', 'Internal', 'Public']
        for visibility in allow_visibility:
            visibility = visibility
            r = org_api.update_org({'visibility': visibility})
            self.assert_status_200(r)

    def test_upload_icon(self):
        org_api = self.create_org()

        r1 = org_api.get_icon()
        self.assert_status_404(r1)

        r = org_api.change_or_set_icon()
        self.assert_status_200(r)
        self.assertNotEqual(r.json()['icon_file'], '')

        r1 = org_api.get_icon()
        self.assert_status_200(r)

        r2 = org_api.change_or_set_icon()
        self.assert_status_200(r2)
        self.assertNotEqual(r2.json()['icon_file'], r.json()['icon_file'])
        self.assertNotEqual(r2.json()['icon_file'], '')

        file = tempfile.NamedTemporaryFile(suffix='.jpg')
        file.write(b'hello')
        file_path = file.name
        r = org_api.change_or_set_icon(file_path)
        self.assert_status_400(r)

    def test_delete_icon(self):
        org_api = self.create_org()

        r = org_api.change_or_set_icon()
        self.assert_status_200(r)

        r = org_api.remove_icon()
        self.assert_status_204(r)

        r = org_api.get_org()
        self.assertEqual(r.json()['icon_file'], '')

    def test_delete_org(self):
        org_api = self.create_org()

        r = org_api.remove_org()
        self.assert_status_204(r)

        r = org_api.get_org()
        self.assert_status_404(r)

    def test_create_org_permission(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.generate_org(1)
        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)

        anonymous: Api = Api(UnitTestClient('/api'))
        org = self.generate_org(2)
        r = anonymous.get_user_api().create_org(org)
        self.assert_status_401(r)

    def test_update_public_org_permission(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.generate_org(1, 'Public')
        org_name = org['name']
        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)

        bill: Api = Api(UnitTestClient('/api'), 'BillGates', True)
        api.get_org_api(org_name).add_member('BillGates', 'Admin')
        update_org = {'description': 'My description.'}
        r = bill.get_org_api(org_name).update_org(update_org)
        self.assert_status_200(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Collaborator')
        r = bill.get_org_api(org_name).update_org(update_org)
        self.assert_status_403(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Member')
        r = bill.get_org_api(org_name).update_org(update_org)
        self.assert_status_403(r)

        mark: Api = Api(UnitTestClient('/api'), 'MarkZuckerberg', True)
        r = mark.get_org_api(org_name).update_org(update_org)
        self.assert_status_403(r)

        anonymous: Api = Api(UnitTestClient('/api'))
        r = anonymous.get_org_api(org_name).update_org(update_org)
        self.assert_status_401(r)

    def test_update_internal_org_permission(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.generate_org(1, 'Internal')
        org_name = org['name']
        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)

        bill: Api = Api(UnitTestClient('/api'), 'BillGates', True)
        api.get_org_api(org_name).add_member('BillGates', 'Admin')
        update_org = {'description': 'My description.'}
        r = bill.get_org_api(org_name).update_org(update_org)
        self.assert_status_200(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Collaborator')
        r = bill.get_org_api(org_name).update_org(update_org)
        self.assert_status_403(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Member')
        r = bill.get_org_api(org_name).update_org(update_org)
        self.assert_status_403(r)

        mark: Api = Api(UnitTestClient('/api'), 'MarkZuckerberg', True)
        r = mark.get_org_api(org_name).update_org(update_org)
        self.assert_status_403(r)

        anonymous: Api = Api(UnitTestClient('/api'))
        r = anonymous.get_org_api(org_name).update_org(update_org)
        self.assert_status_401(r)

    def test_update_private_org_permission(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.generate_org(1, 'Private')
        org_name = org['name']
        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)

        bill: Api = Api(UnitTestClient('/api'), 'BillGates', True)
        api.get_org_api(org_name).add_member('BillGates', 'Admin')
        update_org = {'description': 'My description.'}
        r = bill.get_org_api(org_name).update_org(update_org)
        self.assert_status_200(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Collaborator')
        r = bill.get_org_api(org_name).update_org(update_org)
        self.assert_status_403(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Member')
        r = bill.get_org_api(org_name).update_org(update_org)
        self.assert_status_403(r)

        mark: Api = Api(UnitTestClient('/api'), 'MarkZuckerberg', True)
        r = mark.get_org_api(org_name).update_org(update_org)
        self.assert_status_404(r)

        anonymous: Api = Api(UnitTestClient('/api'))
        r = anonymous.get_org_api(org_name).update_org(update_org)
        self.assert_status_401(r)

    def test_remove_public_org_permission(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.generate_org(1, 'Public')
        org_name = org['name']
        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)

        bill: Api = Api(UnitTestClient('/api'), 'BillGates', True)
        api.get_org_api(org_name).add_member('BillGates', 'Collaborator')
        r = bill.get_org_api(org_name).remove_org()
        self.assert_status_403(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Member')
        r = bill.get_org_api(org_name).remove_org()
        self.assert_status_403(r)

        mark: Api = Api(UnitTestClient('/api'), 'MarkZuckerberg', True)
        r = mark.get_org_api(org_name).remove_org()
        self.assert_status_403(r)

        anonymous: Api = Api(UnitTestClient('/api'))
        r = anonymous.get_org_api(org_name).remove_org()
        self.assert_status_401(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Admin')
        r = bill.get_org_api(org_name).remove_org()
        self.assert_status_204(r)

    def test_remove_internal_org_permission(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.generate_org(1, 'Internal')
        org_name = org['name']
        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)

        bill: Api = Api(UnitTestClient('/api'), 'BillGates', True)
        api.get_org_api(org_name).add_member('BillGates', 'Collaborator')
        r = bill.get_org_api(org_name).remove_org()
        self.assert_status_403(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Member')
        r = bill.get_org_api(org_name).remove_org()
        self.assert_status_403(r)

        mark: Api = Api(UnitTestClient('/api'), 'MarkZuckerberg', True)
        r = mark.get_org_api(org_name).remove_org()
        self.assert_status_403(r)

        anonymous: Api = Api(UnitTestClient('/api'))
        r = anonymous.get_org_api(org_name).remove_org()
        self.assert_status_401(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Admin')
        r = bill.get_org_api(org_name).remove_org()
        self.assert_status_204(r)

    def test_remove_private_org_permission(self):
        api: Api = Api(UnitTestClient('/api'), 'LarryPage', True)
        org = self.generate_org(1, 'Private')
        org_name = org['name']
        r = api.get_user_api().create_org(org)
        self.assert_status_201(r)

        bill: Api = Api(UnitTestClient('/api'), 'BillGates', True)
        api.get_org_api(org_name).add_member('BillGates', 'Collaborator')
        r = bill.get_org_api(org_name).remove_org()
        self.assert_status_403(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Member')
        r = bill.get_org_api(org_name).remove_org()
        self.assert_status_403(r)

        mark: Api = Api(UnitTestClient('/api'), 'MarkZuckerberg', True)
        r = mark.get_org_api(org_name).remove_org()
        self.assert_status_404(r)

        anonymous: Api = Api(UnitTestClient('/api'))
        r = anonymous.get_org_api(org_name).remove_org()
        self.assert_status_401(r)

        api.get_org_api(org_name).change_member_role('BillGates', 'Admin')
        r = bill.get_org_api(org_name).remove_org()
        self.assert_status_204(r)
