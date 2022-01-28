from rest_framework import serializers
from application.models import Application, ApplicationUser
from util.choice import ChoiceField
from util.visibility import VisibilityType


class ApplicationSerializer(serializers.ModelSerializer):
    
    display_name = serializers.CharField(max_length=128, help_text='A short text describing the application')
    name = serializers.SlugField(max_length=32)
    description = serializers.CharField(required=False, max_length=1024, help_text='A short text describing the application')
    visibility = ChoiceField(VisibilityType.choices)
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
        read_only_fields = ['icon_file']
        fields = ['name', 'display_name', 'description', 'icon_file', 'visibility', 'release_type', 'os', 'platform', 'update_time', 'create_time']

class ApplicationIconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['icon_file']

class UserApplicationSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='app.name')
    display_name = serializers.StringRelatedField(source='app.display_name')
    description = serializers.StringRelatedField(source='app.description')
    visibility = ChoiceField(VisibilityType.choices, source='app.visibility')
    release_type = ChoiceField(choices=Application.ReleaseType.choices, source='app.release_type')
    os = ChoiceField(choices=Application.OperatingSystem.choices, source='app.os', help_text='The OS the app will be running on')
    platform = ChoiceField(choices=Application.Platform.choices, source='app.platform', help_text='The platform of the app')
    icon_file = serializers.SerializerMethodField()
    role = ChoiceField(choices=ApplicationUser.ApplicationUserRole.choices, required=False)
    update_time = serializers.ReadOnlyField(source='app.update_time')
    create_time = serializers.ReadOnlyField(source='app.create_time')

    def get_icon_file(self, obj):
        try:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.app.icon_file.url)
        except:
            return ''

    class Meta:
        model = ApplicationUser
        fields = ['role', 'name', 'display_name', 'description', 'icon_file', 'visibility', 'release_type', 'os', 'platform', 'update_time', 'create_time']

class ApplicationUserSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    role = ChoiceField(choices=ApplicationUser.ApplicationUserRole.choices, required=False)

    class Meta:
        model = ApplicationUser
        fields = ['role', 'username', 'update_time', 'create_time']

class ApplicationUserAddSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = ChoiceField(choices=ApplicationUser.ApplicationUserRole.choices)

    class Meta:
        fields = ['role', 'username']
