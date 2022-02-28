from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from organization.models import OrganizationUser, Organization
from organization.serializers import *
from application.models import Application
from application.serializers import ApplicationIconSerializer
from util.visibility import VisibilityType
from util.choice import ChoiceField
from util.reserved import reserved_names

def viewer_query(user, org_name):
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
    org_user = OrganizationUser.objects.filter(viewer_query(user, org_name))
    if not org_user.exists():
        raise Http404
    return org_user.first()

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

class OrganizationList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        # order, filter, search
        # {
        #     "value": [],
        #     "count": 30
        # }
        top = int(request.GET.get('top', 10))
        skip = int(request.GET.get('skip', 0))
        count = True if request.GET.get('count', 'false').lower() == 'true' else False
        if request.user.is_authenticated:
            # todo
            allow_visibility = [VisibilityType.Public, VisibilityType.Internal]
            orgs = Organization.objects.filter(visibility__in=allow_visibility)
            user_orgs = OrganizationUser.objects.filter(user=request.user).prefetch_related('org')
            def not_in_user_orgs(org):
                return len(list(filter(lambda x: x.org.name==org.name, user_orgs))) == 0
            orgs = filter(not_in_user_orgs, orgs)
            data = OrganizationSerializer(orgs, many=True, context={'request': request}).data
            user_orgs_data = UserOrganizationSerializer(user_orgs, many=True, context={'request': request}).data
            data.extend(user_orgs_data)
            return Response(data[skip: skip + top])
        else:
            orgs = Organization.objects.filter(visibility=VisibilityType.Public).order_by('name')[skip: top + skip]
            serializer = OrganizationSerializer(orgs, many=True, context={'request': request})
            return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        serializer = OrganizationSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        name = serializer.validated_data['name']
        if name in reserved_names:
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
        if Organization.objects.filter(name=name).exists():
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

        instance = serializer.save()
        org_user = OrganizationUser.objects.create(org=instance, user=request.user, role=OrganizationUser.OrganizationUserRole.Admin)
        data = serializer.data
        data['role'] = ChoiceField(choices=OrganizationUser.OrganizationUserRole.choices).to_representation(org_user.role)
        response = Response(data, status=status.HTTP_201_CREATED)
        location = reverse('org-detail', args=(name,))
        response['Location'] = request.build_absolute_uri(location)
        return response

class OrganizationDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, org_name):
        if request.user.is_authenticated:
            try:
                user_org = OrganizationUser.objects.get(org__name=org_name, user=request.user)
                serializer = UserOrganizationSerializer(user_org, context={'request': request})
                return Response(serializer.data)
            except OrganizationUser.DoesNotExist:
                pass
        try:
            if request.user.is_authenticated:
                allow_visibility = [VisibilityType.Public, VisibilityType.Internal]
            else:
                allow_visibility = [VisibilityType.Public]
            org = Organization.objects.get(name=org_name, visibility__in=allow_visibility)
            serializer = OrganizationSerializer(org, context={'request': request})
            return Response(serializer.data)
        except Organization.DoesNotExist:
            raise Http404

    def put(self, request, org_name):
        user_org = check_org_admin_permission(org_name, request.user)
        serializer = OrganizationSerializer(user_org.org, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.validated_data.get('name', None) and org_name != serializer.validated_data['name']:
            if Organization.objects.filter(name=serializer.validated_data['name']).exists():
                return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

        serializer.save()
        data = serializer.data
        data['role'] = ChoiceField(choices=OrganizationUser.OrganizationUserRole.choices).to_representation(user_org.role)
        return Response(data)

    def delete(self, request, org_name):
        user_org = check_org_admin_permission(org_name, request.user)
        if Application.objects.filter(org=user_org.org).exists():
            raise PermissionDenied
        user_org.org.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrganizationIcon(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, org_name):
        user_org = check_org_view_permission(org_name, request.user)
        if not user_org.org.icon_file:
            raise Http404
        response = Response()
        response['X-Accel-Redirect'] = user_org.org.icon_file.url
        return response

    def post(self, request, org_name):
        user_org = check_org_admin_permission(org_name, request.user)
        serializer = OrganizationIconSerializer(user_org.org, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        data = {
            'icon_file': request.build_absolute_uri(instance.icon_file.url)
        }
        # todo response no content
        response = Response(data)
        location = reverse('org-icon', args=(org_name,))
        response['Location'] = request.build_absolute_uri(location)
        return response

    def delete(self, request, org_name):
        user_org = check_org_admin_permission(org_name, request.user)
        storage = user_org.org.icon_file.storage
        icon_file = user_org.org.icon_file
        user_org.org.icon_file = None
        user_org.org.save()
        storage.delete(icon_file.name)
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrganizationUserList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, org_name):
        check_org_view_permission(org_name, request.user)
        users = OrganizationUser.objects.filter(org__name=org_name)
        serializer = OrganizationUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, org_name):
        user_org = check_org_admin_permission(org_name, request.user)
        serializer = OrganizationUserAddSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data['username']
        role = serializer.validated_data['role']
        try:
            OrganizationUser.objects.get(org__name=org_name, user__username=username)
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
        except OrganizationUser.DoesNotExist:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            instance = OrganizationUser.objects.create(org=user_org.org, role=role, user=user)
            serializer = OrganizationUserSerializer(instance)
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            location = reverse('org-user', args=(org_name, username))
            response['Location'] = request.build_absolute_uri(location)
            return response

class OrganizationUserDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, org_name, username):
        try:
            return OrganizationUser.objects.get(org__name=org_name, user__username=username)
        except OrganizationUser.DoesNotExist:
            raise Http404

    def get(self, request, org_name, username):
        # todo
        check_org_view_permission(org_name, request.user)
        org_user = self.get_object(org_name, username)
        serializer = OrganizationUserSerializer(org_user)
        return Response(serializer.data)

    def put(self, request, org_name, username):
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        check_org_admin_permission(org_name, request.user)
        org_user = self.get_object(org_name, username)
        serializer = OrganizationUserSerializer(org_user, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if request.user.username == username:
            if serializer.validated_data.get('role', admin_role) != admin_role:
                exists = OrganizationUser.objects.filter(org__name=org_name, role=admin_role).exclude(user=request.user).exists()
                if not exists:
                    raise PermissionDenied
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, org_name, username):
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        check_org_admin_permission(org_name, request.user)
        org_user = self.get_object(org_name, username)

        if request.user.username == username:
            exists = OrganizationUser.objects.filter(org__name=org_name, role=admin_role).exclude(user=request.user).exists()
            if not exists:
                raise PermissionDenied

        org_user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrgApplicationList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, org_name):
        check_org_view_permission(org_name, request.user)
        apps = Application.objects.filter(org__name=org_name)
        serializer = OrgApplicationSerializer(apps, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, org_name):
        user_org = check_org_admin_permission(org_name, request.user)
        serializer = OrgApplicationSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if Application.objects.filter(name=serializer.validated_data['name'], org=user_org.org).exists():
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
        serializer.save(org=user_org.org)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrgApplicationDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, org_name, app_name, for_update=False):
        try:
            return Application.objects.get(org__name=org_name, name=app_name)
        except Application.DoesNotExist:
            raise Http404

    def get(self, request, org_name, app_name):
        check_org_view_permission(org_name, request.user)
        app = self.get_object(org_name, app_name)
        serializer = OrgApplicationSerializer(app, context={'request': request})
        return Response(serializer.data)

    def put(self, request, org_name, app_name):
        user_org = check_org_admin_permission(org_name, request.user)
        app = self.get_object(user_org.org.name, app_name)
        serializer = OrgApplicationSerializer(app, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if serializer.validated_data.get('name', None) and app_name != serializer.validated_data['name']:
            if Application.objects.filter(org=user_org.org, name=serializer.validated_data['name']).exists():
                return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

        # todo: transfer app to another org or user
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, org_name, app_name):
        user_org = check_org_admin_permission(org_name, request.user)
        app = self.get_object(user_org.org.name, app_name)
        # todo: check users, delete related object
        app.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrgApplicationIcon(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, org, app_name, for_update=False):
        try:
            return Application.objects.get(org=org, name=app_name)
        except Application.DoesNotExist:
            raise Http404

    def post(self, request, org_name, app_name):
        user_org = check_org_admin_permission(org_name, request.user)
        app = self.get_object(user_org.org, app_name, True)
        serializer = ApplicationIconSerializer(app, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        data = {
            'icon_file': request.build_absolute_uri(instance.icon_file.url)
        }
        return Response(data)

    def delete(self, request, org_name, app_name):
        user_org = check_org_admin_permission(org_name, request.user)
        app = self.get_object(user_org.org, app_name, True)
        storage = app.icon_file.storage
        icon_file = app.icon_file
        app.icon_file = None
        app.save()
        storage.delete(icon_file.name)
        return Response(status=status.HTTP_204_NO_CONTENT)
