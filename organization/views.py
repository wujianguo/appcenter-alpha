from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from organization.models import OrganizationUser, Organization
from organization.serializers import *
from application.models import Application
from util.visibility import VisibilityType
from util.choice import ChoiceField

def check_org_permission(org_name, user, role=None):
    try:
        user_org = OrganizationUser.objects.get(org__name=org_name, user=user)
        if role is not None and user_org.role != role:
            raise PermissionDenied
        return user_org
    except OrganizationUser.DoesNotExist:
        raise Http404

class OrganizationList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        if request.user.is_authenticated:
            allow_visibility = [VisibilityType.Public, VisibilityType.Internal]
            q1 = Q(org__visibility__in=allow_visibility)
            q2 = Q(user=request.user)
            # # todo： an app has multi member
            orgs = OrganizationUser.objects.filter(q1 | q2).prefetch_related('org')
            serializer = UserOrganizationSerializer(orgs, many=True, context={'request': request})
        else:
            orgs = Organization.objects.filter(visibility=VisibilityType.Public)
            serializer = OrganizationSerializer(orgs, many=True, context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        serializer = OrganizationSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if Organization.objects.filter(name=serializer.validated_data['name']).exists():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()
        org_user = OrganizationUser(org=instance, user=request.user, role=OrganizationUser.OrganizationUserRole.Admin)
        org_user.save()
        data = serializer.data
        data['role'] = ChoiceField(choices=OrganizationUser.OrganizationUserRole.choices).to_representation(org_user.role)
        response = Response(data, status=status.HTTP_201_CREATED)
        response['Location'] = request.build_absolute_uri('orgs/' + data['name'])
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
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        user_org = check_org_permission(org_name, request.user, admin_role)
        serializer = OrganizationSerializer(user_org.org, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.validated_data.get('name', None) and org_name != serializer.validated_data['name']:
            if Organization.objects.filter(name=serializer.validated_data['name']).exists():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        data = serializer.data
        data['role'] = ChoiceField(choices=OrganizationUser.OrganizationUserRole.choices).to_representation(user_org.role)
        return Response(data)

    def delete(self, request, org_name):
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        user_org = check_org_permission(org_name, request.user, admin_role)
        # todo: check users, delete related object
        user_org.org.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrganizationIcon(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, org_name):
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        user_org = check_org_permission(org_name, request.user, admin_role)
        serializer = OrganizationIconSerializer(user_org.org, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        data = {
            'icon_file': request.build_absolute_uri(instance.icon_file.url)
        }
        return Response(data)

    def delete(self, request, org_name):
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        user_org = check_org_permission(org_name, request.user, admin_role)
        user_org.org.icon_file.storage.delete(user_org.org.icon_file.name)
        user_org.org.icon_file = None
        user_org.org.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrganizationUserList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, org_name):
        users = OrganizationUser.objects.filter(org__name=org_name, user=request.user).prefetch_related('user').order_by('-updated_at')
        serializer = OrganizationUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, org_name):
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        user_org = check_org_permission(org_name, request.user, admin_role)
        serializer = OrganizationUserAddSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data['username']
        role = serializer.validated_data['role']
        try:
            org_user = OrganizationUser.objects.get(org__name=org_name, user__username=username)
            if org_user.role != role:
                org_user.role = role
                org_user.save()
            serializer = OrganizationUserSerializer(org_user)
            return Response(serializer.data)
        except OrganizationUser.DoesNotExist:
            user = User.objects.get(username=username)
            instance = OrganizationUser.objects.create(org=user_org.org, role=role, user=user)
            serializer = OrganizationUserSerializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrganizationUserDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, org_name, username):
        try:
            return OrganizationUser.objects.get(org__name=org_name, user__username=username)
        except OrganizationUser.DoesNotExist:
            raise Http404

    def get(self, request, org_name, username):
        check_org_permission(org_name, request.user)
        org_user = self.get_object(org_name, username)
        serializer = OrganizationUserSerializer(org_user)
        return Response(serializer.data)

    def put(self, request, org_name, username):
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        check_org_permission(org_name, request.user, admin_role)
        org_user = self.get_object(org_name, username)
        serializer = OrganizationUserSerializer(org_user, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # print(serializer.validated_data)
        if request.user.username == username:
            if serializer.validated_data.get('role', admin_role) != admin_role:
                exists = OrganizationUser.objects.filter(org__name=org_name, role=admin_role).exclude(user=request.user).exists()
                if not exists:
                    raise PermissionDenied
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, org_name, username):
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        check_org_permission(org_name, request.user, admin_role)
        org_user = self.get_object(org_name, username)

        if request.user.username == username:
            exists = OrganizationUser.objects.filter(org__name=org_name, role=admin_role).exclude(user=request.user).exists()
            if not exists:
                raise PermissionDenied

        org_user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrgApplicationList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, org_name):
        check_org_permission(org_name, request.user)
        apps = Application.objects.filter(org__name=org_name).order_by('-updated_at')
        serializer = OrgApplicationSerializer(apps, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, org_name):
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        user_org = check_org_permission(org_name, request.user, admin_role)
        serializer = OrgApplicationSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(org=user_org.org)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrgApplicationDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, org, app_name):
        try:
            return Application.objects.get(org=org, name=app_name)
        except Application.DoesNotExist:
            raise Http404

    def get(self, request, org_name, app_name):
        user_org = check_org_permission(org_name, request.user)
        app = self.get_object(user_org.org, app_name)
        serializer = OrgApplicationSerializer(app, context={'request': request})
        return Response(serializer.data)

    def put(self, request, org_name, app_name):
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        user_org = check_org_permission(org_name, request.user, admin_role)
        app = self.get_object(user_org.org, app_name)
        serializer = OrgApplicationSerializer(app, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # todo: transfer app to another org or user
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, org_name, app_name):
        admin_role = OrganizationUser.OrganizationUserRole.Admin
        user_org = check_org_permission(org_name, request.user, admin_role)
        app = self.get_object(user_org.org, app_name)
        # todo: check users, delete related object
        app.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
