#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from django.test import Client

class BaseClient:
    def __init__(self, base_url):
        pass

    def set_token(self, token):
        pass

    def set_username(self, username):
        pass

    def get(self, path, query=None):
        pass

    def post(self, path, body):
        pass

    def put(self, path, body):
        pass

    def delete(self, path):
        pass

    def upload_post(self, path, data):
        pass

class RequestsClient(BaseClient):
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = ''
        self.username = ''

    def set_token(self, token):
        self.token = token

    def set_username(self, username):
        self.username = username

    def build_url(self, path):
        return self.base_url + path

    def headers(self):
        if self.token:
            return {
                'Authorization': 'Bearer ' + self.token
            }
        return {}

    def get(self, path, query=None):
        return requests.get(self.build_url(path), headers=self.headers())

    def post(self, path, body):
        return requests.post(self.build_url(path), json=body, headers=self.headers())

    def put(self, path, body):
        return requests.put(self.build_url(path), json=body, headers=self.headers())

    def delete(self, path):
        return requests.delete(self.build_url(path), headers=self.headers())

    def upload_post(self, path, data):
        return requests.post(self.build_url(path), files=data, headers=self.headers())


class DjangoTestClient(BaseClient):
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = ''
        self.username = ''
        self.client = Client()

    def set_token(self, token):
        if token is not None:
            self.token = 'Bearer ' + token
        else:
            self.token = ''

    def set_username(self, username):
        self.username = username

    def build_url(self, path):
        return self.base_url + path

    def get(self, path, query=None):
        return self.client.get(self.build_url(path), data=query, HTTP_AUTHORIZATION=self.token)

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

class UnitTestClient(DjangoTestClient):
    pass
