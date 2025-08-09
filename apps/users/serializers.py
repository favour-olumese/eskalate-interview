import re
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('name', 'email', 'password', 'password2', 'role')

    def validate_name(self, value):
        if not re.match(r"^[a-zA-Z]+( [a-zA-Z]+)?$", value):
            raise serializers.ValidationError("Name must contain only alphabets and a single space.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            name=validated_data['name'],
            email=validated_data['email'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])
        # User is inactive until email is verified
        user.is_active = False
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        if not user.is_verified:
             raise serializers.ValidationError("Email not verified. Please check your inbox for a verification link.", code='authorization')
        if not user.is_active:
             raise serializers.ValidationError("User account is inactive.", code='authorization')

        token = super().get_token(user)
        # Add custom claims
        token['user_id'] = str(user.id)
        token['role'] = user.role
        token['name'] = user.name
        return token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'role', 'is_verified')