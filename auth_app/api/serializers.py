from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth import authenticate
from rest_framework import serializers

def validate_registration_data(data):
    """
    Validate registration input data.
    - Ensure that 'password' and 'repeated_password' match
    - Ensure the email is unique in the system
    """
    if data['password'] != data['repeated_password']:
        raise serializers.ValidationError({'password': 'Passwords do not match'})
    if User.objects.filter(email=data['email']).exists():
        raise serializers.ValidationError({'email': 'Email already exists'})
    return data


def split_full_name(full_name):
    """
    Split a full name into first_name and last_name.
    - If only one name is provided, last_name is set to an empty string.
    """
    parts = full_name.strip().split(" ", 1)
    first_name = parts[0]
    if len(parts) > 1:
            last_name = parts[1]
    else:
        last_name = ""
    return first_name, last_name


def generate_username(first_name, last_name):
    """
    Generate a unique username based on first and last name.
    - Format: first.last
    - If username exists, append a number until unique.
    """
    base_username = f"{first_name.lower()}.{last_name.lower()}"
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username


def create_user(validated_data):
    """
    Create a new User instance in the database.
    - Extracts 'fullname' and splits into first/last names
    - Generates a unique username
    - Saves user with hashed password using transaction.atomic()
    """
    fullname = validated_data.pop('fullname')
    validated_data.pop('repeated_password')
    first_name, last_name = split_full_name(fullname)
    username = generate_username(first_name, last_name)
    with transaction.atomic():
        user = User(
            email=validated_data['email'],
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(validated_data['password'])
        user.save()
    return user

class RegisterationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    - Accepts 'fullname', 'email', 'password', 'repeated_password'
    - Validates input data and creates a new user
    """
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'fullname', 'email', 'password', 'repeated_password']
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
    """
    Serializer for user login.
    - Accepts 'email' and 'password'
    - Validates credentials and authenticates the user
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    def validate(self, data):
        """
        Validate user login credentials.
        - Raise ValidationError if email does not exist
        - Raise ValidationError if password is incorrect
        - Add the authenticated user object to data['user']
        """
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