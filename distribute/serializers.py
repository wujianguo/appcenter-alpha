from collections import OrderedDict
from dataclasses import field
from distribute.models import Package, Release, Upgrade
from rest_framework import serializers

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
        fields = ['name', 'package_file', 'icon_file', 'fingerprint', 'version', 'short_version', 'internal_build', 'size', 'bundle_identifier', 'commit_id', 'min_os', 'bundle_identifier', 'channle', 'description', 'update_time', 'create_time']
        read_only_fields = ['name', 'package_file', 'icon_file', 'fingerprint', 'version', 'short_version', 'internal_build', 'size', 'bundle_identifier', 'min_os', 'bundle_identifier', 'channle']

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
    package_file = serializers.ReadOnlyField(source='package.package_file')
    icon_file = serializers.ReadOnlyField(source='package.icon_file')
    fingerprint = serializers.ReadOnlyField(source='package.fingerprint')
    version = serializers.ReadOnlyField(source='package.version')
    short_version = serializers.ReadOnlyField(source='package.short_version')
    internal_build = serializers.ReadOnlyField(source='package.internal_build')
    size = serializers.ReadOnlyField(source='package.size')
    bundle_identifier = serializers.ReadOnlyField(source='package.bundle_identifier')
    commit_id = serializers.ReadOnlyField(source='package.commit_id')
    min_os = serializers.ReadOnlyField(source='package.min_os')
    channle = serializers.ReadOnlyField(source='package.channle')
    class Meta:
        model = Release
        fields = ['release_id', 'release_notes', 'enabled', 'name', 'package_file', 'icon_file', 'fingerprint', 'version', 'short_version', 'internal_build', 'size', 'bundle_identifier', 'commit_id', 'min_os', 'bundle_identifier', 'channle', 'update_time', 'create_time']
        read_only_fields = ['upgrade_id', 'name', 'package_file', 'icon_file', 'fingerprint', 'version', 'short_version', 'internal_build', 'size', 'bundle_identifier', 'commit_id', 'min_os', 'bundle_identifier', 'channle']

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
