from django.test import Client
from django.contrib.auth.models import User

class DjangoTestClient:
    def __init__(self, base_url, username=None):
        self.base_url = base_url
        self.client = Client()
        self.username = username
        self.token = ''
        if username is not None:
            user = User.objects.get_or_create(username=username)[0]
            self.client.force_login(user=user)

    def set_token(self, token):
        if token is not None:
            self.token = 'Bearer ' + token
        else:
            self.token = ''

    def set_username(self, username):
        self.username = username

    def build_url(self, path):
        return self.base_url + path

    def get(self, path):
        return self.client.get(self.build_url(path), HTTP_AUTHORIZATION=self.token)

    def post(self, path, body):
        content_type = 'application/json'
        return self.client.post(self.build_url(path), body, content_type=content_type, HTTP_AUTHORIZATION=self.token)

    def put(self, path, body):
        content_type = 'application/json'
        return self.client.put(self.build_url(path), body, content_type=content_type, HTTP_AUTHORIZATION=self.token)

    def delete(self, path):
        return self.client.delete(self.build_url(path), HTTP_AUTHORIZATION=self.token)

    def upload_post(self, path, data):
        return self.client.post(self.build_url(path), data=data, format="multipart", HTTP_AUTHORIZATION=self.token)

