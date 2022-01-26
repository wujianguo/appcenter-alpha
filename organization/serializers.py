from rest_framework import serializers
from organization.models import Organization, OrganizationUser
from application.models import Application
from util.choice import ChoiceField
from util.visibility import VisibilityType

class OrganizationSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(max_length=128, help_text='A short text describing the organization')
    name = serializers.SlugField(max_length=32)
    visibility = ChoiceField(VisibilityType.choices)
    icon_file = serializers.SerializerMethodField()

    def get_icon_file(self, obj):
        try:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.icon_file.url)
        except:
            return ''

    class Meta:
        model = Organization
        fields = ['name', 'display_name', 'icon_file', 'visibility', 'update_time', 'create_time']

class OrganizationIconSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['icon_file']

class UserOrganizationSerializer(serializers.ModelSerializer):
    
    name = serializers.StringRelatedField(source='org.name')
    display_name = serializers.StringRelatedField(source='org.display_name')
    visibility = ChoiceField(VisibilityType.choices, source='org.visibility')
    role = ChoiceField(choices=OrganizationUser.OrganizationUserRole.choices, required=False)
    icon_file = serializers.SerializerMethodField()
    update_time = serializers.ReadOnlyField(source='org.update_time')
    create_time = serializers.ReadOnlyField(source='org.create_time')

    def get_icon_file(self, obj):
        try:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.org.icon_file.url)
        except:
            return ''

    class Meta:
        model = OrganizationUser
        fields = ['role', 'name', 'display_name', 'icon_file', 'visibility', 'update_time', 'create_time']

class OrganizationUserSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    role = ChoiceField(choices=OrganizationUser.OrganizationUserRole.choices, required=False)

    class Meta:
        model = OrganizationUser
        fields = ['role', 'username', 'update_time', 'create_time']

class OrganizationUserAddSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = ChoiceField(choices=OrganizationUser.OrganizationUserRole.choices)

    class Meta:
        model = OrganizationUser
        fields = ['role', 'username']

class OrgApplicationSerializer(serializers.ModelSerializer):    
    display_name = serializers.CharField(help_text='A short text describing the application')
    name = serializers.SlugField()
    description = serializers.CharField(required=False, max_length=1024, help_text='A short text describing the application')
    release_type = ChoiceField(choices=Application.ReleaseType.choices)
    os = ChoiceField(choices=Application.OperatingSystem.choices, help_text='The OS the app will be running on')
    platform = ChoiceField(choices=Application.Platform.choices, help_text='The platform of the app')
    icon_file = serializers.SerializerMethodField()

    def get_icon_file(self, obj):
        try:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.icon_file.url)
        except:
            return ''

    class Meta:
        model = Application
        fields = ['name', 'display_name', 'icon_file', 'description', 'os', 'platform', 'release_type', 'update_time', 'create_time']
