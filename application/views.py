from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from application.models import Application, ApplicationUser
from application.serializers import *
from util.visibility import VisibilityType
from util.choice import ChoiceField

def viewer_query(ownername, app_name, user):
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
        return ApplicationUser.objects.get(viewer_query(ownername, app_name, user))
    except ApplicationUser.DoesNotExist:
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

class ApplicationList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, ownername):
        if request.user.is_authenticated:
            q1 = Q(app__owner__username=ownername)
            q2 = Q(app__visibility=VisibilityType.Public) | Q(app__visibility=VisibilityType.Internal)
            q3 = Q(user=request.user, app__owner__username=ownername)
            apps = ApplicationUser.objects.filter(q3 | (q1 & q2))
            # todo： an app has multi member
            # print('====')
            # for app in apps:
            #     print('{0}: {1}'.format(app.user.username, app.app.name))
            serializer = UserApplicationSerializer(apps, many=True, context={'request': request})
        else:
            apps = Application.objects.filter(owner__username=ownername, visibility=VisibilityType.Public)
            serializer = ApplicationSerializer(apps, many=True, context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request, ownername):
        if ownername != request.user.username:
            raise PermissionDenied

        serializer = ApplicationSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if Application.objects.filter(name=serializer.validated_data.get('name'), owner=request.user).exists():
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
        instance = serializer.save(owner=request.user)
        app_user = ApplicationUser(app=instance, user=request.user, role=ApplicationUser.ApplicationUserRole.Manager)
        app_user.save()
        data = serializer.data
        data['role'] = ChoiceField(choices=ApplicationUser.ApplicationUserRole.choices).to_representation(app_user.role)
        return Response(data, status=status.HTTP_201_CREATED)

class ApplicationDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, ownername, app_name):
        if request.user.is_authenticated:
            try:
                user_app = ApplicationUser.objects.get(app__name=app_name, app__owner__username=ownername, user=request.user)
                serializer = UserApplicationSerializer(user_app, context={'request': request})
                return Response(serializer.data)
            except ApplicationUser.DoesNotExist:
                pass
        try:
            if request.user.is_authenticated:
                allow_visibility = [VisibilityType.Public, VisibilityType.Internal]
            else:
                allow_visibility = [VisibilityType.Public]
            app = Application.objects.get(name=app_name, owner__username=ownername, visibility__in=allow_visibility)
            serializer = ApplicationSerializer(app, context={'request': request})
            return Response(serializer.data)
        except Application.DoesNotExist:
            raise Http404

    def put(self, request, ownername, app_name):
        user_app = check_app_manager_permission(ownername, app_name, request.user)
        serializer = ApplicationSerializer(user_app.app, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = serializer.validated_data.get('name', None)
        if name and app_name != name:
            if Application.objects.filter(owner__username=ownername, name=name).exists():
                return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

        serializer.save()
        data = serializer.data
        data['role'] = ChoiceField(choices=ApplicationUser.ApplicationUserRole.choices).to_representation(user_app.role)
        return Response(data)

    def delete(self, request, ownername, app_name):
        user_app = check_app_manager_permission(ownername, app_name, request.user)
        # todo: check users, delete related object
        user_app.app.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ApplicationIcon(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, ownername, app_name):
        user_app = check_app_manager_permission(ownername, app_name, request.user)
        serializer = ApplicationIconSerializer(user_app.app, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        data = {
            'icon_file': request.build_absolute_uri(instance.icon_file.url)
        }
        return Response(data)

    def delete(self, request, ownername, app_name):
        user_app = check_app_manager_permission(ownername, app_name, request.user)
        storage = user_app.app.icon_file.storage
        icon_file = user_app.app.icon_file
        user_app.app.icon_file = None
        user_app.app.save()
        storage.delete(icon_file.name)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ApplicationUserList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, ownername, app_name):
        check_app_view_permission(ownername, app_name, request.user)
        users = ApplicationUser.objects.filter(app__name=app_name, app__owner__username=ownername)
        serializer = ApplicationUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, ownername, app_name):
        user_app = check_app_manager_permission(ownername, app_name, request.user)
        serializer = ApplicationUserAddSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data['username']
        role = serializer.validated_data['role']
        try:
            ApplicationUser.objects.get(app__name=app_name, user__username=username)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ApplicationUser.DoesNotExist:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            instance = ApplicationUser.objects.create(app=user_app.app, role=role, user=user)
            serializer = ApplicationUserSerializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class ApplicationUserDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, ownername, app_name, username):
        try:
            return ApplicationUser.objects.get(app__name=app_name, app__owner__username=ownername, user__username=username)
        except ApplicationUser.DoesNotExist:
            raise Http404

    def get(self, request, ownername, app_name, username):
        # todo
        check_app_view_permission(ownername, app_name, request.user)
        app_user = self.get_object(ownername, app_name, username)
        serializer = ApplicationUserSerializer(app_user)
        return Response(serializer.data)

    def put(self, request, ownername, app_name, username):
        manager_role = ApplicationUser.ApplicationUserRole.Manager
        check_app_manager_permission(ownername, app_name, request.user)
        app_user = self.get_object(ownername, app_name, username)
        serializer = ApplicationUserSerializer(app_user, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if app_user.app.owner == app_user.user:
            if serializer.validated_data.get('role', manager_role) != manager_role:
                raise PermissionDenied
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, ownername, app_name, username):
        check_app_manager_permission(ownername, app_name, request.user)
        app_user = self.get_object(ownername, app_name, username)
        if app_user.app.owner == app_user.user:
            raise PermissionDenied
        app_user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
