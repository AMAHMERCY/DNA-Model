from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from accounts.imd_lookup import lookup_imd   # <-- REQUIRED IMPORT


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "name",
            "password",
            "date_of_birth",
            "phone",
            "post_code",
            "sex",
            "chronic_condition",
            "chronic_other",
        ]

    def create(self, validated_data):
        # Extract password safely
        password = validated_data.pop("password")

        # Get postcode from request
        postcode = validated_data.get("post_code")

        # IMD lookup (returns tuple)
        imd_score, imd_band = lookup_imd(postcode)

        # Add IMD fields into saved user object
        validated_data["imd_score"] = imd_score
        validated_data["imd_band"] = imd_band

        # Create user
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # authenticate using custom user model
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("This account is disabled")

        data["user"] = user
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "name",
            "hospital_id",
            "slug",
            "role",
            "date_joined",
            "date_of_birth",
            "phone",
            "post_code",
            "sex",
            "chronic_condition",
            "chronic_other",
        ]

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name"]    