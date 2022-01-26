import tempfile, PIL, requests
from django.test import Client
from django.contrib.auth.models import User

class UnitTestClient:
    def __init__(self, base_url, username=None):
        self.base_url = base_url
        self.client = Client()
        if username is not None:
            user = User.objects.get_or_create(username=username)[0]
            self.client.force_login(user=user)

    def build_url(self, path):
        return self.base_url + path

    def get(self, path):
        return self.client.get(self.build_url(path))

    def post(self, path, body):
        content_type = 'application/json'
        return self.client.post(self.build_url(path), body, content_type=content_type)

    def put(self, path, body):
        content_type = 'application/json'
        return self.client.put(self.build_url(path), body, content_type=content_type)

    def delete(self, path):
        return self.client.delete(self.build_url(path))

    def upload_post(self, path, data):
        return self.client.post(self.build_url(path), data=data, format="multipart")

class RequestsClient:
    def __init__(self, base_url, username=None):
        self.base_url = base_url
        if username is not None:
            self.username = username

    def build_url(self, path):
        return self.base_url + path

    def get(self, path):
        return requests.get(self.build_url(path))

    def post(self, path, body):
        return requests.post(self.build_url(path), json=body)

    def put(self, path, body):
        return requests.put(self.build_url(path), json=body)

    def delete(self, path):
        return requests.delete(self.build_url(path))

    def upload_post(self, path, data):
        return requests.post(self.build_url(path), data=data, format="multipart")

class ApiClient:

    class OrganizationClient:

        def __init__(self, client):
            self.client = client
        
        def create(self, org):
            return self.client.post('orgs', org)

        def get_one(self, name):
            return self.client.get('orgs/' + name)

        def get_list(self):
            return self.client.get('orgs')

        def modify(self, name, org):
            return self.client.put('orgs/' + name, org)

        def delete(self, name):
            return self.client.delete('orgs/' + name)

        def change_or_set_icon(self, name, icon_file_path=None):
            
            if icon_file_path is None:
                image = PIL.Image.new('RGB', size=(1, 1))
                file = tempfile.NamedTemporaryFile(suffix='.jpg')
                image.save(file)
                file_path = file.name
            else:
                file_path = icon_file_path

            with open(file_path, 'rb') as fp:
                data = {'icon_file': fp}
                return self.client.upload_post('orgs/' + name + '/icon', data=data)

        def delete_icon(self, name):
            return self.client.delete('orgs/' + name + '/icon')

        def add_member(self, name, collaborator):
            return self.client.post('orgs/' + name + '/people/collaborators', collaborator)

        def get_member(self, name, username):
            return self.client.get('orgs/' + name + '/people/collaborators/' + username)

        def get_member_list(self, name):
            return self.client.get('orgs/' + name + '/people/collaborators')

        def change_member_role(self, name, collaborator, role):
            data = {
                'role': role
            }
            return self.client.put('orgs/' + name + '/people/collaborators/' + collaborator, data)

        def remove_member(self, name, collaborator):
            return self.client.delete('orgs/' + name + '/people/collaborators/' + collaborator)
    
    def __init__(self, client):
        self._org = ApiClient.OrganizationClient(client)

    @property
    def org(self):
        return self._org