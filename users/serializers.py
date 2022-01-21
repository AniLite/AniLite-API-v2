from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):

    pfp = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'profile_picture', 'pfp']
        extra_kwargs = {
            'password': {'write_only': True},
            'profile_picture': {'write_only': True}
        }

    def get_pfp(self, obj):
        if obj.profile_picture is not None:
            pfp = obj.profile_picture.url
            return pfp
        else:
            return None

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
