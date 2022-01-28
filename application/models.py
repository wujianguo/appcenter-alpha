from django.db import models
from django.contrib.auth.models import User
from util.choice import CustomChoicesMeta
from util.visibility import VisibilityType

def application_directory_path(instance, filename):
    name = 'icon.' + filename.split('.')[-1]
    if instance.org is not None:
      return 'orgs/{0}/apps/{1}/{2}/icons/{3}'.format(instance.org.name, instance.name, instance.platform, name)
    else:
      return 'users/{0}/apps/{1}/{2}/icons/{3}'.format(instance.owner.username, instance.name, instance.platform, name)

def universal_app_directory_path(instance, filename):
    name = 'icon.' + filename.split('.')[-1]
    if instance.org is not None:
      return 'orgs/{0}/apps/{1}/universal/icons/{2}'.format(instance.org.name, instance.name, name)
    else:
      return 'users/{0}/apps/{1}/universal/icons/{2}'.format(instance.owner.username, instance.name, name)

class Application(models.Model):
    class ReleaseType(models.IntegerChoices):
        Alpha = 1
        Beta = 2
        Enterprise = 3
        Production = 4
        Store = 5

    class OperatingSystem(models.IntegerChoices, metaclass=CustomChoicesMeta):
        Android = 1
        iOS = 2
        macOS = 3
        Tizen = 4
        tvOS = 5
        Windows = 6
        Linux = 7

    class Platform(models.IntegerChoices, metaclass=CustomChoicesMeta):
        JavaKotlin = 1
        ObjectiveCSwift = 2
        UWP = 3
        Cordova = 4
        ReactNative = 5
        Xamarin = 6
        Unity = 7
        Electron = 8
        WPF = 9
        WinForms = 10

    org = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    visibility = models.IntegerField(choices=VisibilityType.choices, null=True)
    display_name = models.CharField(max_length=128, help_text='The descriptive name of the app')
    name = models.SlugField(max_length=32)
    icon_file = models.ImageField(upload_to=application_directory_path)
    description = models.CharField(max_length=1024, help_text='A short text describing the app')
    release_type = models.IntegerField(choices=ReleaseType.choices)
    os = models.IntegerField(choices=OperatingSystem.choices, help_text='The OS the app will be running on')
    platform = models.IntegerField(choices=Platform.choices, help_text='The platform of the app')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class ApplicationUser(models.Model):
    class ApplicationUserRole(models.IntegerChoices):
        Manager = 1
        Developer = 2
        Viewer = 3
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.IntegerField(ApplicationUserRole.choices)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class UniversalApp(models.Model):
    iOS = models.OneToOneField(Application, related_name='iOS', on_delete=models.CASCADE)
    android = models.OneToOneField(Application, related_name='Android', on_delete=models.CASCADE)
    macOS = models.OneToOneField(Application, related_name='macOS', on_delete=models.CASCADE)
    windows = models.OneToOneField(Application, related_name='Windows', on_delete=models.CASCADE)
    linux = models.OneToOneField(Application, related_name='Linux', on_delete=models.CASCADE)
    tizen = models.OneToOneField(Application, related_name='Tizen', on_delete=models.CASCADE)
    tvOS = models.OneToOneField(Application, related_name='tvOS', on_delete=models.CASCADE)
    display_name = models.CharField(max_length=128, help_text='The descriptive name of the app')
    name = models.SlugField(max_length=32, unique=True)
    icon_file = models.ImageField(upload_to=universal_app_directory_path)
    description = models.CharField(max_length=1024, help_text='A short text describing the app')
    org = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
