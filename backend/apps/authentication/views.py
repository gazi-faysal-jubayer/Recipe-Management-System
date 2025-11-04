"""
Authentication views for Recipe Management System
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from supabase import create_client, Client
from django.conf import settings
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, 
    RefreshTokenSerializer
)
from apps.common.utils import success_response, error_response

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return success_response(
            data={
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            },
            message='Registration successful',
            status_code=status.HTTP_201_CREATED
        )
    
    return error_response(
        message='Registration failed',
        errors=serializer.errors,
        status_code=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login user and return tokens
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        validated_data = serializer.validated_data
        
        # Get or create Django user
        user, created = User.objects.get_or_create(
            email=validated_data['email'],
            defaults={
                'username': validated_data['email'],
            }
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return success_response(
            data={
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                'supabase_session': {
                    'access_token': validated_data['session'].access_token,
                    'refresh_token': validated_data['session'].refresh_token,
                }
            },
            message='Login successful'
        )
    
    return error_response(
        message='Login failed',
        errors=serializer.errors,
        status_code=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user (blacklist refresh token)
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return success_response(message='Logout successful')
    
    except Exception as e:
        return error_response(
            message='Logout failed',
            errors={'detail': str(e)}
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh access token using refresh token
    """
    serializer = RefreshTokenSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            refresh = RefreshToken(serializer.validated_data['refresh_token'])
            
            return success_response(
                data={
                    'access': str(refresh.access_token),
                },
                message='Token refreshed successfully'
            )
        
        except Exception as e:
            return error_response(
                message='Invalid refresh token',
                status_code=status.HTTP_401_UNAUTHORIZED
            )
    
    return error_response(
        message='Invalid request',
        errors=serializer.errors
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Get current user profile
    """
    serializer = UserSerializer(request.user)
    
    return success_response(
        data=serializer.data,
        message='Profile retrieved successfully'
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update user profile
    """
    user = request.user
    
    # Update user fields
    if 'full_name' in request.data:
        full_name_parts = request.data['full_name'].split(' ')
        user.first_name = full_name_parts[0] if full_name_parts else ''
        user.last_name = ' '.join(full_name_parts[1:]) if len(full_name_parts) > 1 else ''
    
    user.save()
    
    serializer = UserSerializer(user)
    
    return success_response(
        data=serializer.data,
        message='Profile updated successfully'
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Change user password
    """
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return error_response(
            message='Both old and new passwords are required',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify with Supabase
    supabase: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )
    
    try:
        # First verify old password by attempting to login
        supabase.auth.sign_in_with_password({
            'email': request.user.email,
            'password': old_password
        })
        
        # If successful, update password
        supabase.auth.update_user({
            'password': new_password
        })
        
        return success_response(message='Password changed successfully')
    
    except Exception as e:
        return error_response(
            message='Failed to change password',
            errors={'detail': str(e)},
            status_code=status.HTTP_400_BAD_REQUEST
        )
