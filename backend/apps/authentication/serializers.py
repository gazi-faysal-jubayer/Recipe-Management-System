"""
Serializers for authentication app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from supabase import create_client, Client
from django.conf import settings
import os

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=6, write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        # Initialize Supabase client
        supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        
        # Create user in Supabase Auth
        try:
            response = supabase.auth.sign_up({
                'email': validated_data['email'],
                'password': validated_data['password'],
                'options': {
                    'data': {
                        'full_name': validated_data.get('full_name', '')
                    }
                }
            })
            
            if response.user:
                # Create or update Django user
                user, created = User.objects.update_or_create(
                    email=validated_data['email'],
                    defaults={
                        'username': validated_data['email'],
                        'first_name': validated_data.get('full_name', '').split(' ')[0] if validated_data.get('full_name') else '',
                        'last_name': ' '.join(validated_data.get('full_name', '').split(' ')[1:]) if validated_data.get('full_name') else '',
                    }
                )
                return user
            else:
                raise serializers.ValidationError("Failed to create user")
                
        except Exception as e:
            raise serializers.ValidationError(f"Registration failed: {str(e)}")


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        # Initialize Supabase client
        supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        
        # Authenticate with Supabase
        try:
            response = supabase.auth.sign_in_with_password({
                'email': data['email'],
                'password': data['password']
            })
            
            if response.user:
                data['user'] = response.user
                data['session'] = response.session
                return data
            else:
                raise serializers.ValidationError("Invalid credentials")
                
        except Exception as e:
            raise serializers.ValidationError(f"Login failed: {str(e)}")


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'date_joined')
        read_only_fields = ('id', 'email', 'date_joined')
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)
