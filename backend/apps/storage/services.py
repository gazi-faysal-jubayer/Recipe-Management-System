"""
Storage service for Supabase integration
"""
from typing import BinaryIO, Optional, Tuple
from supabase import create_client, Client
from django.conf import settings
import uuid
import os

# Initialize Supabase client
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY
)


class StorageService:
    """Service for handling file storage with Supabase"""
    
    RECIPE_IMAGES_BUCKET = 'recipe-images'
    USER_UPLOADS_BUCKET = 'user-uploads'
    
    def __init__(self):
        self.client = supabase
        self._ensure_buckets_exist()
    
    def _ensure_buckets_exist(self):
        """Ensure storage buckets exist"""
        try:
            # List existing buckets
            buckets = self.client.storage.list_buckets()
            bucket_names = [b['name'] for b in buckets]
            
            # Create recipe images bucket if not exists
            if self.RECIPE_IMAGES_BUCKET not in bucket_names:
                self.client.storage.create_bucket(
                    self.RECIPE_IMAGES_BUCKET,
                    {'public': True}
                )
            
            # Create user uploads bucket if not exists
            if self.USER_UPLOADS_BUCKET not in bucket_names:
                self.client.storage.create_bucket(
                    self.USER_UPLOADS_BUCKET,
                    {'public': False}
                )
        except Exception as e:
            print(f"Error ensuring buckets: {str(e)}")
    
    def upload_recipe_image(
        self, 
        file: BinaryIO, 
        file_name: str,
        user_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Upload recipe image to Supabase storage
        
        Args:
            file: File object to upload
            file_name: Original file name
            user_id: User ID for organization
            
        Returns:
            Tuple of (success, public_url)
        """
        try:
            # Generate unique file name
            file_extension = os.path.splitext(file_name)[1]
            unique_name = f"{user_id}/{uuid.uuid4()}{file_extension}"
            
            # Upload to Supabase storage
            response = self.client.storage.from_(self.RECIPE_IMAGES_BUCKET).upload(
                unique_name,
                file.read(),
                {'content-type': self._get_content_type(file_extension)}
            )
            
            # Get public URL
            url = self.client.storage.from_(self.RECIPE_IMAGES_BUCKET).get_public_url(unique_name)
            
            return True, url
            
        except Exception as e:
            print(f"Error uploading recipe image: {str(e)}")
            return False, None
    
    def upload_user_file(
        self,
        file: BinaryIO,
        file_name: str,
        user_id: str,
        folder: str = 'misc'
    ) -> Tuple[bool, Optional[str]]:
        """
        Upload user file to private storage
        
        Args:
            file: File object to upload
            file_name: Original file name
            user_id: User ID for organization
            folder: Subfolder within user's directory
            
        Returns:
            Tuple of (success, file_path)
        """
        try:
            # Generate file path
            file_extension = os.path.splitext(file_name)[1]
            unique_name = f"{user_id}/{folder}/{uuid.uuid4()}{file_extension}"
            
            # Upload to Supabase storage
            response = self.client.storage.from_(self.USER_UPLOADS_BUCKET).upload(
                unique_name,
                file.read(),
                {'content-type': self._get_content_type(file_extension)}
            )
            
            return True, unique_name
            
        except Exception as e:
            print(f"Error uploading user file: {str(e)}")
            return False, None
    
    def delete_file(self, bucket: str, file_path: str) -> bool:
        """
        Delete a file from storage
        
        Args:
            bucket: Bucket name
            file_path: Path to file in bucket
            
        Returns:
            Success status
        """
        try:
            self.client.storage.from_(bucket).remove([file_path])
            return True
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False
    
    def get_signed_url(
        self,
        bucket: str,
        file_path: str,
        expires_in: int = 3600
    ) -> Optional[str]:
        """
        Get a signed URL for private file access
        
        Args:
            bucket: Bucket name
            file_path: Path to file in bucket
            expires_in: URL expiry time in seconds
            
        Returns:
            Signed URL or None
        """
        try:
            response = self.client.storage.from_(bucket).create_signed_url(
                file_path,
                expires_in
            )
            return response['signedURL']
        except Exception as e:
            print(f"Error creating signed URL: {str(e)}")
            return None
    
    def list_user_files(
        self,
        user_id: str,
        bucket: str = USER_UPLOADS_BUCKET,
        folder: Optional[str] = None
    ) -> list:
        """
        List files for a user
        
        Args:
            user_id: User ID
            bucket: Bucket to search in
            folder: Optional subfolder
            
        Returns:
            List of file objects
        """
        try:
            path = f"{user_id}/{folder}" if folder else str(user_id)
            response = self.client.storage.from_(bucket).list(path)
            return response
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []
    
    def _get_content_type(self, file_extension: str) -> str:
        """Get content type from file extension"""
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.pdf': 'application/pdf'
        }
        
        return content_types.get(
            file_extension.lower(),
            'application/octet-stream'
        )
