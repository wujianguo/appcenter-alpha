import tempfile, PIL

class ApiClient:

    class ApplicationClient:

        def __init__(self, client):
            self.client = client

        def create(self, app, ownername=None):
            if ownername is None:
                username = self.client.username
            else:
                username = ownername
            return self.client.post('users/' + username + '/apps', app)

        def get_one(self, ownername, name):
            return self.client.get('users/' + ownername + '/apps/' + name)

        def get_list(self, ownername):
            return self.client.get('users/' + ownername + '/apps')

        def modify(self, ownername, name, app):
            return self.client.put('users/' + ownername + '/apps/' + name, app)

        def delete_app(self, ownername, name):
            return self.client.delete('users/' + ownername + '/apps/' + name)

        def change_or_set_icon(self, ownername, name, icon_file_path=None):
            if icon_file_path is None:
                image = PIL.Image.new('RGB', size=(1, 1))
                file = tempfile.NamedTemporaryFile(suffix='.jpg')
                image.save(file)
                file_path = file.name
            else:
                file_path = icon_file_path

            with open(file_path, 'rb') as fp:
                data = {'icon_file': fp}
                return self.client.upload_post('users/' + ownername + '/apps/' + name + '/icon', data=data)

        def delete_icon(self, ownername, name):
            return self.client.delete('users/' + ownername + '/apps/' + name + '/icon')

        def add_member(self, ownername, name, collaborator):
            return self.client.post('users/' + ownername + '/apps/' + name + '/people/collaborators', collaborator)

        def get_member(self, ownername, name, username):
            return self.client.get('users/' + ownername + '/apps/' + name + '/people/collaborators/' + username)

        def get_member_list(self, ownername, name):
            return self.client.get('users/' + ownername + '/apps/' + name + '/people/collaborators')

        def change_member_role(self, ownername, name, collaborator, role):
            data = {
                'role': role
            }
            return self.client.put('users/' + ownername + '/apps/' + name + '/people/collaborators/' + collaborator, data)

        def remove_member(self, ownername, name, collaborator):
            return self.client.delete('users/' + ownername + '/apps/' + name + '/people/collaborators/' + collaborator)

        def upload_app(self, ownername, name, file_path):
            with open(file_path, 'rb') as fp:
                data = {'file': fp}
                return self.client.upload_post('users/' + ownername + '/apps/' + name + '/distribute/packages', data=data)

        def get_package(self, ownername, name, internal_build):
            return self.client.get('users/' + ownername + '/apps/' + name + '/distribute/packages/' + str(internal_build))

        def get_package_list(self, ownername, name):
            return self.client.get('users/' + ownername + '/apps/' + name + '/distribute/packages')

        def modify_package(self, ownername, name, internal_build, package):
            return self.client.put('users/' + ownername + '/apps/' + name + '/distribute/packages/' + str(internal_build), package)

        def remove_package(self, ownername, name, internal_build):
            return self.client.delete('users/' + ownername + '/apps/' + name + '/distribute/packages/' + str(internal_build))

        def create_release(self, ownername, name, env, release):
            return self.client.post('users/' + ownername + '/apps/' + name + '/distribute/releases/env/' + env, release)            

        def get_release(self, ownername, name, release_id):
            return self.client.get('users/' + ownername + '/apps/' + name + '/distribute/releases/' + str(release_id))

        def get_release_list(self, ownername, name, env):
            return self.client.get('users/' + ownername + '/apps/' + name + '/distribute/releases/env/' + env)

        def modify_release(self, ownername, name, release_id, release):
            return self.client.put('users/' + ownername + '/apps/' + name + '/distribute/releases/' + str(release_id), release)

        def remove_release(self, ownername, name, release_id):
            return self.client.delete('users/' + ownername + '/apps/' + name + '/distribute/releases/' + str(release_id))            


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
    
        def create_app(self, name, app):
            return self.client.post('orgs/' + name + '/apps', app)

        def get_app(self, name, app_name):
            return self.client.get('orgs/' + name + '/apps/' + app_name)
        
        def get_app_list(self, name):
            return self.client.get('orgs/' + name + '/apps')

        def modify_app(self, name, app_name, app):
            return self.client.put('orgs/' + name + '/apps/' + app_name, app)

        def delete_app(self, name, app_name):
            return self.client.delete('orgs/' + name + '/apps/' + app_name)

        def change_or_set_app_icon(self, name, app_name, icon_file_path=None):
            
            if icon_file_path is None:
                image = PIL.Image.new('RGB', size=(1, 1))
                file = tempfile.NamedTemporaryFile(suffix='.jpg')
                image.save(file)
                file_path = file.name
            else:
                file_path = icon_file_path

            with open(file_path, 'rb') as fp:
                data = {'icon_file': fp}
                return self.client.upload_post('orgs/' + name + '/apps/' + app_name + '/icon', data=data)

        def delete_app_icon(self, name, app_name):
            return self.client.delete('orgs/' + name + '/apps/' + app_name + '/icon')

        def upload_app(self, name, app_name, file_path):
            with open(file_path, 'rb') as fp:
                data = {'file': fp}
                return self.client.upload_post('orgs/' + name + '/apps/' + app_name + '/distribute/packages', data=data)

        def get_package(self, name, app_name, internal_build):
            return self.client.get('orgs/' + name + '/apps/' + app_name + '/distribute/packages/' + str(internal_build))

        def get_package_list(self, name, app_name):
            return self.client.get('orgs/' + name + '/apps/' + app_name + '/distribute/packages')

        def modify_package(self, name, app_name, internal_build, package):
            return self.client.put('orgs/' + name + '/apps/' + app_name + '/distribute/packages/' + str(internal_build), package)

        def remove_package(self, name, app_name, internal_build):
            return self.client.delete('orgs/' + name + '/apps/' + app_name + '/distribute/packages/' + str(internal_build))            

        def create_release(self, name, app_name, env, release):
            return self.client.post('orgs/' + name + '/apps/' + app_name + '/distribute/releases/env/' + env, release)            

        def get_release(self, name, app_name, release_id):
            return self.client.get('orgs/' + name + '/apps/' + app_name + '/distribute/releases/' + str(release_id))

        def get_release_list(self, name, app_name, env):
            return self.client.get('orgs/' + name + '/apps/' + app_name + '/distribute/releases/env/' + env)

        def modify_release(self, name, app_name, release_id, release):
            return self.client.put('orgs/' + name + '/apps/' + app_name + '/distribute/releases/' + str(release_id), release)

        def remove_release(self, name, app_name, release_id):
            return self.client.delete('orgs/' + name + '/apps/' + app_name + '/distribute/releases/' + str(release_id))            

    class UserClient:

        def __init__(self, client):
            self.client = client

        def register(self, user):
            return self.client.post('user/register', user)

        def login(self, user):
            return self.client.post('user/login', user)

        def logout(self):
            return self.client.post('user/logout')

        def me(self):
            return self.client.get('user/me')

    def __init__(self, client):
        self._client = client
        self._org = ApiClient.OrganizationClient(client)
        self._app = ApiClient.ApplicationClient(client)
        self._user = ApiClient.UserClient(client)

    @property
    def org(self):
        return self._org

    @property
    def app(self):
        return self._app

    @property
    def user(self):
        return self._user

    @property
    def client(self):
        return self._client