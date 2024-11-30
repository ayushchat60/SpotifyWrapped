from django.contrib.auth.models import User
from rest_framework import serializers

from .models import WrappedHistory


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Fields:
    - `username`: The username of the user.
    - `email`: The email address of the user.
    - `password`: The user's password (write-only).

    Methods:
    - `create`: Custom method to create a new user instance using Django's `create_user` method.
    """
    password = serializers.CharField(write_only=True)  # Ensure password is write-only

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        """
        Create a new user instance with the validated data.

        Args:
            validated_data (dict): The validated data for the user.

        Returns:
            User: The created user instance.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class WrappedHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the `WrappedHistory` model.

    Fields:
    - `id`: The unique ID of the Wrapped history.
    - `title`: The title of the Wrapped history.
    - `artists`: The artists associated with this Wrapped history.
    - `created_at`: The timestamp of when this Wrapped history was created.
    """
    class Meta:
        model = WrappedHistory
        fields = ['id', 'title', 'artists', 'created_at']