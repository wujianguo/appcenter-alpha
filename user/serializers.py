# from collections import OrderedDict
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers

# class NonNullModelSerializer(serializers.ModelSerializer):
#     def to_representation(self, instance):
#         result = super(NonNullModelSerializer, self).to_representation(instance)
#         return OrderedDict([(key, result[key]) for key in result if result[key] is not None])

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField()

    class Meta:
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        username = attrs.get('username', None)
        email = attrs.get('email', None)
        password = attrs.get('password')
        user = None
        if username is not None and email is None:
            user = authenticate(username=username, password=password)
        elif email is not None and username is None:
            user = authenticate(email=email, password=password)
        elif email is not None and username is not None:
            user = authenticate(username=username, email=email, password=password)
        else:
            raise serializers.ValidationError('username or email is required.')
        if user is None:
            raise serializers.ValidationError('A user with this username/email and password is not found.')
        return {
            'user': user
        }
