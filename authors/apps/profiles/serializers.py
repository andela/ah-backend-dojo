from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    bio = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Profile
        fields = ('firstname', 'lastname','username', 'bio', 'image','email')
        read_only_fields = ('username',)

