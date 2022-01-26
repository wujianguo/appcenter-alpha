from rest_framework import serializers
from application.models import Application

class ApplicationIconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['icon_file']
