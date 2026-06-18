from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirmed_password = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'confirmed_password']

    def validate(self, attrs):
        """Check that passwords match"""
        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('confirmed_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user
    
class UserSerializer(serializers.ModelSerializer):
    """Serializer for returning user data (without password)"""
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'created_at']
        read_only_fields = ['id', 'created_at']

class LoginSerializer(serializers.Serializer):
    """Serializer for login requests - accepts username or email"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)