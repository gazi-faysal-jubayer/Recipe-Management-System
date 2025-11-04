"""
Views for storage app
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import StorageService
from apps.common.utils import success_response, error_response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_recipe_image(request):
    """Upload a recipe image"""
    if 'image' not in request.FILES:
        return error_response(
            message='No image file provided',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    
    # Validate file size (max 10MB)
    if image_file.size > 10 * 1024 * 1024:
        return error_response(
            message='Image size should not exceed 10MB',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']
    if image_file.content_type not in allowed_types:
        return error_response(
            message=f'Invalid image type. Allowed types: {", ".join(allowed_types)}',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        storage_service = StorageService()
        success, url = storage_service.upload_recipe_image(
            image_file,
            image_file.name,
            str(request.user.id)
        )
        
        if success:
            return success_response(
                data={'url': url},
                message='Image uploaded successfully',
                status_code=status.HTTP_201_CREATED
            )
        else:
            return error_response(
                message='Failed to upload image',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return error_response(
            message=f'Upload failed: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
