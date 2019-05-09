from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """This serializer requests and creates a new article"""
    class Meta:
        fields = [
            'receiver',
            'body',
            'link',
            'created_at',
        ]
        model = Notification

        