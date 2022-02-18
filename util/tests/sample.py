#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from client import ApiClient
from requests_client import RequestsClient

class Sample:

    def __init__(self, data_path):
        self.data_path = data_path
        self.base_url = '/debug/api/'

    def sync_to_server(self):
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        self.data = data
        for user in data['users']:
            client = ApiClient(RequestsClient(self.base_url))
            self.create_user(client, user)

        for org in data['orgs']:
            owner = self.find_and_create_org(org)
            self.org_add_other_user(owner, org)

    def create_user(self, client, user):
        user_req = {
            "username": user['username'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "password": user['username'] + '@password',
            "email": user['username'] + '@example.com'
        }
        r = client.user.register(user_req)
        if r.status_code != 201:
            print(user_req)
            print(r.json())
        client.client.set_token(r.json()['token'])

    def org_add_other_user(self, owner, org):
        for user in self.data['users']:
            for o in user['orgs']:
                if o['name'] == org['name'] and user['username'] != owner.client.username:
                    member = {
                        'username': user['username'],
                        'role': o['role']
                    }
                    r = owner.org.add_member(o['name'], member)
                    r = owner.org.get_app_list(o['name'])
                    if r.status_code != 200:
                        print(member)
                        raise

    def find_and_create_org(self, org):
        for user in self.data['users']:
            client = None
            for o in user['orgs']:
                if o['name'] == org['name'] and o['role'] == 'Admin':
                    client = ApiClient(RequestsClient(self.base_url))
                    user_req = {
                        'username': user['username'],
                        'password': user['username'] + '@password',
                    }
                    r = client.user.login(user_req)
                    client.client.set_token(r.json()['token'])
                    client.client.set_username(user['username'])
                    break
            if client is not None:
                break

        org_req = {
            'name': org['name'],
            'display_name': org['display_name'],
            'visibility': org['visibility'],
            'description': org['description']
        }

        r = client.org.create(org_req)
        if org.get('icon_file', None):
            client.org.change_or_set_icon(name=org['name'], icon_file_path="icons/" + org['icon_file'])
        self.create_org_app(client, org)
        return client

    def create_org_app(self, owner, org):
        for app in org.get('apps', []):
            for a in self.data['apps']:
                if app == a['name']:
                    app_req = {
                        'name': a['name'],
                        'display_name': a['display_name'],
                        "os": a["os"],
                        "platform": a["platform"],
                        "release_type": a["release_type"]
                    }
                    if a.get('description', None):
                        app_req['description'] = a['description']
                    r = owner.org.create_app(org['name'], app_req)
                    if r.status_code != 201:
                        print(app_req)
                        print(r.json())
                    if a.get('icon_file', None):
                        owner.org.change_or_set_app_icon(org['name'], a['name'], icon_file_path="icons/" + a['icon_file'])

def main():
    sample = Sample('sample.json')
    sample.sync_to_server()

if __name__ == '__main__':
    main()

