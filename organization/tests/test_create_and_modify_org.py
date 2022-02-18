import tempfile
from util.tests.client import ApiClient
from util.tests.unit_test_client import UnitTestClient
from util.tests.case import BaseTestCase

class OrganizationCreateTest(BaseTestCase):

    def setUp(self):
        super().setUp()
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

    def test_create_success(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)
        ret = {
            'name': r1.json()['name'],
            'display_name': r1.json()['display_name'],
            'visibility': r1.json()['visibility']
        }
        self.assertDictEqual(ret, org)

        r2 = self.client.org.get_one(org['name'])
        self.assertDictEqual(r1.json(), r2.json())

        r3 = self.client.org.get_list()
        self.assertDictEqual(r3.json()[0], r1.json())

    def test_invalid_name(self):
        # 1. only letters, numbers, underscores or hyphens
        # 2. 0 < len(name) <= 32
        org = self.generate_org()
        org['name'] += '*'
        r1 = self.client.org.create(org)
        self.assert_status_400(r1)

        max_length = 32
        org['name'] = 'a' * max_length
        r2 = self.client.org.create(org)
        self.assert_status_201(r2)

        org['name'] = 'a' * max_length + 'a'
        r3 = self.client.org.create(org)
        self.assert_status_400(r3)

        org['name'] = ''
        r4 = self.client.org.create(org)
        self.assert_status_400(r4)

        del org['name']
        r5 = self.client.org.create(org)
        self.assert_status_400(r5)

    def test_duplicate_name(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        org2 = self.generate_org()
        org2['name'] = org['name']
        r2 = self.client.org.create(org2)
        self.assert_status_409(r2)

    def test_required(self):
        org = self.generate_org()
        del org['name']
        r1 = self.client.org.create(org)
        self.assert_status_400(r1)
        
        org2 = self.generate_org()
        del org2['display_name']
        r2 = self.client.org.create(org2)
        self.assert_status_400(r2)

        org3 = self.generate_org()
        del org3['visibility']
        r3 = self.client.org.create(org3)
        self.assert_status_400(r3)

    def test_invalid_display_name(self):
        # 0 < len(display_name) <= 32
        org = self.generate_org()
        max_length = 128
        org['display_name'] = 'a' * max_length
        r2 = self.client.org.create(org)
        self.assert_status_201(r2)

        org['display_name'] = 'a' * max_length + 'a'
        r3 = self.client.org.create(org)
        self.assert_status_400(r3)

        org['display_name'] = ''
        r4 = self.client.org.create(org)
        self.assert_status_400(r4)

    def test_visibility(self):
        org = self.generate_org()
        org['visibility'] = 'a'
        r2 = self.client.org.create(org)
        self.assert_status_400(r2)

        allow_visibility = ['Private', 'Internal', 'Public']
        for visibility in allow_visibility:
            org = self.generate_org()
            org['visibility'] = visibility
            r = self.client.org.create(org)
            self.assert_status_201(r)

    def test_modify_org_name(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)

        new_name = 'new_name'
        data = {'name': new_name}
        r2 = self.client.org.modify(org['name'], data)
        self.assert_status_200(r2)

        r3 = self.client.org.get_one(org['name'])
        self.assert_status_404(r3)

        r4 = self.client.org.get_one(new_name)
        self.assert_status_200(r4)
        old_value = r1.json()
        old_value['name'] = new_name
        del old_value['update_time']
        new_value = r4.json()
        del new_value['update_time']
        self.assertDictEqual(new_value, old_value)

    def test_modify_invalid_name(self):
        # 1. only letters, numbers, underscores or hyphens
        # 2. 0 < len(name) <= 32
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)
        name = org['name']

        max_length = 32
        new_name = 'a' * max_length + 'a'
        r3 = self.client.org.modify(name, {'name': new_name})
        self.assert_status_400(r3)

        new_name = ''
        r4 = self.client.org.modify(name, {'name': new_name})
        self.assert_status_400(r4)

        new_name = 'a' * max_length
        r2 = self.client.org.modify(name, {'name': new_name})
        self.assert_status_200(r2)

    def test_modify_duplicate_name(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)
        name = org['name']
        r2 = self.client.org.modify(name, {'name': name})
        self.assert_status_200(r2)

        org2 = self.generate_org()
        r3 = self.client.org.create(org2)
        self.assert_status_201(r3)
        new_name = org2['name']
        r4 = self.client.org.modify(name, {'name': new_name})
        self.assert_status_409(r4)

    def test_modify_org_display_name(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)
        name = org['name']

        max_length = 128
        display_name = 'a' * max_length
        r2 = self.client.org.modify(name, {'display_name': display_name})
        self.assert_status_200(r2)

        display_name = 'a' * max_length + 'a'
        r3 = self.client.org.modify(name, {'display_name': display_name})
        self.assert_status_400(r3)

        display_name = ''
        r4 = self.client.org.modify(name, {'display_name': display_name})
        self.assert_status_400(r4)

    def test_modify_org_visibility(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)
        name = org['name']

        visibility = 'a'
        r2 = self.client.org.modify(name, {'visibility': visibility})
        self.assert_status_400(r2)

        allow_visibility = ['Private', 'Internal', 'Public']
        for visibility in allow_visibility:
            visibility = visibility
            r = self.client.org.modify(name, {'visibility': visibility})
            self.assert_status_200(r)

    def test_upload_icon(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)
        name = org['name']

        r2 = self.client.org.change_or_set_icon('xyz')
        self.assert_status_404(r2)
        r2 = self.client.org.change_or_set_icon(name)
        self.assert_status_200(r2)
        self.assertNotEqual(r2.json()['icon_file'], '')

        r3 = self.client.org.change_or_set_icon(name)
        self.assert_status_200(r3)
        self.assertNotEqual(r3.json()['icon_file'], r2.json()['icon_file'])
        self.assertNotEqual(r3.json()['icon_file'], '')

        file = tempfile.NamedTemporaryFile(suffix='.jpg')
        file.write(b'hello')
        file_path = file.name
        r4 = self.client.org.change_or_set_icon(name, file_path)
        self.assert_status_400(r4)


    def test_delete_icon(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)
        name = org['name']

        r2 = self.client.org.change_or_set_icon(name)
        self.assert_status_200(r2)
        self.assertNotEqual(r2.json()['icon_file'], '')

        r3 = self.client.org.delete_icon(name)
        self.assert_status_204(r3)

        r4 = self.client.org.get_one(name)
        self.assertEqual(r4.json()['icon_file'], '')

    def test_delete_org(self):
        org = self.generate_org()
        r1 = self.client.org.create(org)
        self.assert_status_201(r1)
        name = org['name']

        r2 = self.client.org.delete(name)
        self.assert_status_204(r2)

        r3 = self.client.org.get_one(name)
        self.assert_status_404(r3)

    # def test_transfer_org(self):
    #     pass

    # def test_leave_org(self):
    #     pass
