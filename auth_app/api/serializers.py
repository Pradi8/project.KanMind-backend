from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.db import transaction
from django.contrib.auth import authenticate

def validate_registration_data(data):
    if data['password'] != data['repeated_password']:
        raise serializers.ValidationError({'password': 'Passwords do not match'})
    if User.objects.filter(email=data['email']).exists():
        raise serializers.ValidationError({'email': 'Email already exists'})
    if User.objects.filter(username=data['username']).exists():
        raise serializers.ValidationError({'username': 'Username already exists'})
    return data


def create_user(validated_data):
    validated_data.pop('repeated_password')
    with transaction.atomic():
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
    return user


# Register user function 
class RegisterationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password' :  {
                'write_only' : True
            }
        }

    def validate(self, data):
        return validate_registration_data(data)
    
    def create(self, validated_data):
        return create_user(validated_data)

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Ungültige E-mail")
        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError("Passwort ist falsch")
        data['user'] = user
        return data