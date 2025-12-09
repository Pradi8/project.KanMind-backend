from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'repeated_password']

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )

        Token.objects.create(user=user)

        return user