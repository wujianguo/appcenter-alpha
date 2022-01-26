from django.db import models
from django.contrib.auth.models import User
from util.visibility import VisibilityType

def organization_directory_path(instance, filename):
    name = 'icon.' + filename.split('.')[-1]
    return 'orgs/{0}/icons/{1}'.format(instance.name, name)

class Organization(models.Model):
    display_name = models.CharField(max_length=128, help_text='The descriptive name of the organization')
    name = models.SlugField(max_length=32, unique=True)
    description = models.CharField(max_length=1024, help_text='A short text describing the organization')
    visibility = models.IntegerField(choices=VisibilityType.choices)
    icon_file = models.ImageField(upload_to=organization_directory_path)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class OrganizationUser(models.Model):
    class OrganizationUserRole(models.IntegerChoices):
        Admin = 1
        Collaborator = 2
        Member = 3
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.IntegerField(OrganizationUserRole.choices)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
