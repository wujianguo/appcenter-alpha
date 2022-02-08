from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.http import Http404
from django.db.models import Q
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from distribute.serializers import *
from distribute.app_parser import parser
from organization.models import OrganizationUser, Organization
from application.models import Application, ApplicationUser
from util.visibility import VisibilityType

def create_package(request, app):
    serializer = UploadPackageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    file = serializer.validated_data['file']
    ext = file.name.split('.')[-1]
    pkg = parser.parse(file.file, ext, app.os, app.platform)
    if pkg is None:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if pkg.app_icon is not None:
        icon_file = ContentFile(pkg.app_icon)
        icon_file.name = 'icon.png'
    else:
        icon_file = None
    internal_build = Package.objects.filter(app=app).count() + 1
    instance = Package.objects.create(
        app=app,
        name=pkg.display_name,
        package_file=file,
        icon_file=icon_file,
        version=pkg.version,
        short_version=pkg.short_version,
        bundle_identifier=pkg.bundle_identifier,
        internal_build=internal_build,
        min_os=pkg.minimum_os_version,
        extra=pkg.extra,
        size=file.size)
    if not app.icon_file and icon_file is not None:
        app.icon_file = icon_file
        app.save()
    serializer = PackageSerializer(instance, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)

def org_viewer_query(user, org_name):
    if user.is_authenticated:
        allow_visibility = [VisibilityType.Public, VisibilityType.Internal]
        q1 = Q(org__name=org_name)
        q2 = Q(org__visibility__in=allow_visibility)
        q3 = Q(user=user)
        return (q2 | q3) & q1
    else:
        q1 = Q(org__name=org_name)
        q2 = Q(org__visibility=VisibilityType.Public)
        return q1 & q2

def check_org_view_permission(org_name, user):
    try:
        return OrganizationUser.objects.get(org_viewer_query(user, org_name))
    except OrganizationUser.DoesNotExist:
        raise Http404

def check_org_upload_app_permission(org_name, user):
    try:
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        collaborator_role = OrganizationUser.OrganizationUserRole.Collaborator
        user_org = OrganizationUser.objects.get(org__name=org_name, user=user)
        if user_org.role != admin_role and user_org.role != collaborator_role:
            raise PermissionDenied
        return user_org
    except OrganizationUser.DoesNotExist:
        try:
            allow_visibility = [VisibilityType.Public, VisibilityType.Internal]
            Organization.objects.get(name=org_name, visibility__in=allow_visibility)
            raise PermissionDenied
        except Organization.DoesNotExist:
            raise Http404

def check_org_admin_permission(org_name, user):
    try:
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        user_org = OrganizationUser.objects.get(org__name=org_name, user=user)
        if user_org.role != admin_role:
            raise PermissionDenied
        return user_org
    except OrganizationUser.DoesNotExist:
        try:
            allow_visibility = [VisibilityType.Public, VisibilityType.Internal]
            Organization.objects.get(name=org_name, visibility__in=allow_visibility)
            raise PermissionDenied
        except Organization.DoesNotExist:
            raise Http404

class OrgAppPackageList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, org_name, app_name):
        user_org = check_org_view_permission(org_name, request.user)
        packages = Package.objects.filter(app__org=user_org.org, app__name=app_name)
        serializer = PackageSerializer(packages, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, org_name, app_name):
        user_org = check_org_upload_app_permission(org_name, request.user)
        try:
            app = Application.objects.get(org=user_org.org, name=app_name)
        except Application.DoesNotExist:
            raise Http404
        return create_package(request, app)

class OrgAppPackageDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, org, app_name, internal_build):
        try:
            return Package.objects.get(app__org=org, app__name=app_name, internal_build=internal_build)
        except Package.DoesNotExist:
            raise Http404

    def get(self, request, org_name, app_name, internal_build):
        user_org = check_org_view_permission(org_name, request.user)
        package = self.get_object(user_org.org, app_name, internal_build)
        serializer = PackageSerializer(package, context={'request': request})
        return Response(serializer.data)

    def put(self, request, org_name, app_name, internal_build):
        user_org = check_org_upload_app_permission(org_name, request.user)
        package = self.get_object(user_org.org, app_name, internal_build)
        serializer = PackageUpdateSerializer(package, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, org_name, app_name, internal_build):
        user_org = check_org_upload_app_permission(org_name, request.user)
        package = self.get_object(user_org.org, app_name, internal_build)
        # todo: released app should not be deleted
        package.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrgAppReleaseList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, org_name, app_name):
        user_org = check_org_view_permission(org_name, request.user)
        releases = Release.objects.filter(app__org=user_org.org, app__name=app_name)
        serializer = ReleaseSerializer(releases, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, org_name, app_name):
        user_org = check_org_admin_permission(org_name, request.user)
        serializer = ReleaseSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            app = Application.objects.get(org=user_org.org, name=app_name)
        except Application.DoesNotExist:
            raise Http404
        serializer.save(app=app)
        return Response(serializer.data)

class OrgAppReleaseDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, org, app_name, release_id):
        try:
            return Release.objects.get(app__org=org, app__name=app_name, release_id=release_id)
        except Release.DoesNotExist:
            raise Http404

    def get(self, request, org_name, app_name, release_id):
        user_org = check_org_view_permission(org_name, request.user)
        release = self.get_object(user_org.org, app_name, release_id)
        serializer = ReleaseSerializer(release, context={'request': request})
        return Response(serializer.data)

    def put(self, request, org_name, app_name, release_id):
        user_org = check_org_upload_app_permission(org_name, request.user)
        release = self.get_object(user_org.org, app_name, release_id)
        serializer = ReleaseSerializer(release, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, org_name, app_name, release_id):
        user_org = check_org_upload_app_permission(org_name, request.user)
        release = self.get_object(user_org.org, app_name, release_id)
        # todo: released app should not be deleted
        release.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Application

def user_app_viewer_query(ownername, app_name, user):
    if user.is_authenticated:
        allow_visibility = [VisibilityType.Public, VisibilityType.Internal]
        q1 = Q(app__name=app_name, app__owner__username=ownername)
        q2 = Q(app__visibility__in=allow_visibility)
        q3 = Q(user=user)
        return (q2 | q3) & q1
    else:
        q1 = Q(app__name=app_name, app__owner__username=ownername)
        q2 = Q(app__visibility=VisibilityType.Public)
        return q1 & q2

def check_app_view_permission(ownername, app_name, user):
    try:
        return ApplicationUser.objects.get(user_app_viewer_query(ownername, app_name, user))
    except ApplicationUser.DoesNotExist:
        raise Http404

def check_app_upload_permission(ownername, app_name, user):
    try:
        manager_role = ApplicationUser.ApplicationUserRole.Manager
        developer_role = ApplicationUser.ApplicationUserRole.Developer
        user_app = ApplicationUser.objects.get(app__name=app_name, app__owner__username=ownername, user=user)
        if user_app.role != manager_role and user_app.role != developer_role:
            raise PermissionDenied
        return user_app
    except ApplicationUser.DoesNotExist:
        try:
            allow_visibility = [VisibilityType.Public, VisibilityType.Internal]
            Application.objects.get(name=app_name, owner__username=ownername, visibility__in=allow_visibility)
            raise PermissionDenied
        except Application.DoesNotExist:
            raise Http404

def check_app_manager_permission(ownername, app_name, user):
    try:
        manager_role = ApplicationUser.ApplicationUserRole.Manager
        user_app = ApplicationUser.objects.get(app__name=app_name, app__owner__username=ownername, user=user)
        if user_app.role != manager_role:
            raise PermissionDenied
        return user_app
    except ApplicationUser.DoesNotExist:
        try:
            allow_visibility = [VisibilityType.Public, VisibilityType.Internal]
            Application.objects.get(name=app_name, owner__username=ownername, visibility__in=allow_visibility)
            raise PermissionDenied
        except Application.DoesNotExist:
            raise Http404

class UserAppPackageList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, ownername, app_name):
        user_app = check_app_view_permission(ownername, app_name, request.user)
        packages = Package.objects.filter(app=user_app.app)
        serializer = PackageSerializer(packages, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, ownername, app_name):
        user_app = check_app_upload_permission(ownername, app_name, request.user)
        return create_package(request, user_app.app)

class UserAppPackageDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, app, internal_build):
        try:
            return Package.objects.get(app=app, internal_build=internal_build)
        except Package.DoesNotExist:
            raise Http404

    def get(self, request, ownername, app_name, internal_build):
        user_app = check_app_view_permission(ownername, app_name, request.user)
        package = self.get_object(user_app.app, internal_build)
        serializer = PackageSerializer(package, context={'request': request})
        return Response(serializer.data)

    def put(self, request, ownername, app_name, internal_build):
        user_app = check_app_upload_permission(ownername, app_name, request.user)
        package = self.get_object(user_app.app, internal_build)
        serializer = PackageUpdateSerializer(package, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, ownername, app_name, internal_build):
        user_app = check_app_upload_permission(ownername, app_name, request.user)
        package = self.get_object(user_app.app, internal_build)
        # todo: released app should not be deleted
        package.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserAppReleaseList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, ownername, app_name):
        user_app = check_app_view_permission(ownername, app_name, request.user)
        releases = Release.objects.filter(app=user_app.app)
        serializer = ReleaseSerializer(releases, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, ownername, app_name):
        user_app = check_app_manager_permission(ownername, app_name, request.user)
        serializer = ReleaseSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(app=user_app.app)
        return Response(serializer.data)

class UserAppReleaseDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, app, release_id):
        try:
            return Release.objects.get(app=app, release_id=release_id)
        except Release.DoesNotExist:
            raise Http404

    def get(self, request, ownername, app_name, release_id):
        user_app = check_app_view_permission(ownername, app_name, request.user)
        release = self.get_object(user_app.app, release_id)
        serializer = ReleaseSerializer(release, context={'request': request})
        return Response(serializer.data)

    def put(self, request, ownername, app_name, release_id):
        user_app = check_app_manager_permission(ownername, app_name, request.user)
        release = self.get_object(user_app.app, release_id)
        serializer = ReleaseSerializer(release, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, ownername, app_name, release_id):
        user_app = check_app_manager_permission(ownername, app_name, request.user)
        release = self.get_object(user_app.app, release_id)
        # todo: released app should not be deleted
        release.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
