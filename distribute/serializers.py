from collections import OrderedDict
from distribute.models import Package, Release, ReleaseStore, Upgrade, StoreApp
from rest_framework import serializers
from util.choice import ChoiceField

class NonNullModelSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        result = super(NonNullModelSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])

class PackageSerializer(NonNullModelSerializer):
    package_file = serializers.SerializerMethodField()
    def get_package_file(self, obj):
        try:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.package_file.url)
        except:
            return ''

    class Meta:
        model = Package
        fields = ['name', 'package_file', 'icon_file', 'fingerprint', 'version', 'short_version', 'internal_build', 'size', 'bundle_identifier', 'commit_id', 'min_os', 'channle', 'description', 'update_time', 'create_time']
        read_only_fields = ['name', 'package_file', 'icon_file', 'fingerprint', 'version', 'short_version', 'internal_build', 'size', 'bundle_identifier', 'min_os', 'channle']

class PackageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ['description', 'commit_id']

class UploadPackageSerializer(serializers.Serializer):
    file = serializers.FileField()
    class Meta:
        fields = ['file']

class ReleaseSerializer(NonNullModelSerializer):
    name = serializers.ReadOnlyField(source='package.name')
    fingerprint = serializers.ReadOnlyField(source='package.fingerprint')
    version = serializers.ReadOnlyField(source='package.version')
    short_version = serializers.ReadOnlyField(source='package.short_version')
    internal_build = serializers.ReadOnlyField(source='package.internal_build')
    size = serializers.ReadOnlyField(source='package.size')
    bundle_identifier = serializers.ReadOnlyField(source='package.bundle_identifier')
    commit_id = serializers.ReadOnlyField(source='package.commit_id')
    min_os = serializers.ReadOnlyField(source='package.min_os')
    channle = serializers.ReadOnlyField(source='package.channle')

    package_file = serializers.SerializerMethodField()
    icon_file = serializers.SerializerMethodField()

    def get_package_file(self, obj):
        try:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.package.package_file.url)
        except:
            return ''

    def get_icon_file(self, obj):
        try:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.package.icon_file.url)
        except:
            return ''

    class Meta:
        model = Release
        fields = ['release_id', 'release_notes', 'enabled', 'name', 'package_file', 'icon_file', 'fingerprint', 'version', 'short_version', 'internal_build', 'size', 'bundle_identifier', 'commit_id', 'min_os', 'channle', 'update_time', 'create_time']
        read_only_fields = ['release_id', 'name', 'package_file', 'icon_file', 'fingerprint', 'version', 'short_version', 'internal_build', 'size', 'bundle_identifier', 'commit_id', 'min_os', 'channle']

class ReleaseCreateSerializer(serializers.Serializer):
    internal_build = serializers.IntegerField()
    enabled = serializers.BooleanField()
    release_notes = serializers.CharField()
    class Meta:
        fields = ['release_notes', 'enabled', 'internal_build']

class ReleaseUpdateSerializer(NonNullModelSerializer):
    class Meta:
        model = Release
        fields = ['release_notes', 'enabled']

class UpgradeSerializer(NonNullModelSerializer):
    name = serializers.ReadOnlyField(source='release.package.name')
    package_file = serializers.ReadOnlyField(source='release.package.package_file')
    icon_file = serializers.ReadOnlyField(source='release.package.icon_file')
    fingerprint = serializers.ReadOnlyField(source='release.package.fingerprint')
    version = serializers.ReadOnlyField(source='release.package.version')
    short_version = serializers.ReadOnlyField(source='release.package.short_version')
    internal_build = serializers.ReadOnlyField(source='release.package.internal_build')
    size = serializers.ReadOnlyField(source='release.package.size')
    bundle_identifier = serializers.ReadOnlyField(source='release.package.bundle_identifier')
    commit_id = serializers.ReadOnlyField(source='release.package.commit_id')
    min_os = serializers.ReadOnlyField(source='release.package.min_os')
    bundle_identifier = serializers.ReadOnlyField(source='release.package.bundle_identifier')
    channle = serializers.ReadOnlyField(source='release.package.channle')
    class Meta:
        model = Upgrade
        fields = ['upgrade_id', 'release_notes', 'target_version', 'enabled', 'mandatory', 'name', 'package_file', 'icon_file', 'fingerprint', 'version', 'short_version', 'internal_build', 'size', 'bundle_identifier', 'commit_id', 'min_os', 'bundle_identifier', 'channle', 'update_time', 'create_time']
        read_only_fields = ['upgrade_id', 'name', 'package_file', 'icon_file', 'fingerprint', 'version', 'short_version', 'internal_build', 'size', 'bundle_identifier', 'commit_id', 'min_os', 'bundle_identifier', 'channle']

class StoreAppSerializer(NonNullModelSerializer):
    class Meta:
        model = StoreApp
        fields = ['store_name', 'store_display_name', 'store_icon', 'auth_data', 'current_version']

class StoreAppVivoAuthSerializer(serializers.Serializer):
    access_key = serializers.CharField()
    access_secret = serializers.CharField()
    vivo_store_app_id = serializers.CharField()
    store_link = serializers.URLField()
    class Meta:
        fields = ['access_key', 'access_secret', 'vivo_store_app_id', 'store_link']

class ReleaseStoreSerializer(NonNullModelSerializer):
    class Meta:
        model = ReleaseStore
        fields = ['name', 'package_file', 'icon_file', 'fingerprint', 'version', 'short_version', 'internal_build', 'size', 'bundle_identifier', 'commit_id', 'min_os', 'channle', 'release_store_id', 'release_notes', 'store', 'state', 'operator', 'update_time', 'create_time']

class ReleaseStoreCreateSerializer(serializers.Serializer):
    internal_build = serializers.IntegerField()
    release_notes = serializers.CharField()
    store = ChoiceField(choices=StoreApp.StoreType.choices)
    state = ChoiceField(choices=ReleaseStore.State.choices)

    class Meta:
        fields = ['internal_build', 'release_notes', 'store', 'state']

class ReleaseStoreUpdateSerializer(serializers.Serializer):
    internal_build = serializers.IntegerField()
    release_notes = serializers.CharField()
    state = ChoiceField(choices=ReleaseStore.State.choices)
    class Meta:
        fields = ['parent', 'release_notes', 'state']
