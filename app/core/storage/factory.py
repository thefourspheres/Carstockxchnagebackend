# app/core/storage/factory.py
"""
Factory for creating storage service instances.
"""

import os
import uuid
import shutil
from typing import Optional
from fastapi import UploadFile, HTTPException
import aiofiles
from app.core.config import settings


class StorageService:
    """Base interface for storage services."""
    
    async def upload(self, file: UploadFile, base_path: str) -> str:
        """
        Upload a file to storage.
        
        Args:
            file: The file to upload
            base_path: Base path for storing the file
            
        Returns:
            URL or path to the uploaded file
        """
        raise NotImplementedError
    
    async def delete(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if deleted, False otherwise
        """
        raise NotImplementedError
    
    async def get_url(self, file_path: str) -> str:
        """
        Get the public URL for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Public URL
        """
        raise NotImplementedError


class LocalStorage(StorageService):
    """Local filesystem storage implementation."""
    
    def __init__(self):
        self.base_dir = settings.LOCAL_STORAGE_PATH
        os.makedirs(self.base_dir, exist_ok=True)
        print(f"LocalStorage initialized at: {os.path.abspath(self.base_dir)}")
    
    async def upload(self, file: UploadFile, base_path: str) -> str:
        """
        Upload file to local filesystem.
        
        Args:
            file: UploadFile object
            base_path: Base directory path within storage
            
        Returns:
            URL/path to access the file
        """
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")
            
            # Ensure file extension is .webp
            if not file.filename.lower().endswith('.webp'):
                raise HTTPException(
                    status_code=400, 
                    detail="Only WEBP images are allowed"
                )
            
            # Create the directory structure
            full_dir_path = os.path.join(self.base_dir, base_path)
            os.makedirs(full_dir_path, exist_ok=True)
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4().hex}.webp"
            file_path = os.path.join(full_dir_path, unique_filename)
            
            # Save the file
            async with aiofiles.open(file_path, 'wb') as buffer:
                content = await file.read()
                await buffer.write(content)
            
            # Return relative path for URL construction
            relative_path = os.path.join(base_path, unique_filename)
            return f"/uploads/{relative_path.replace(os.sep, '/')}"
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to upload file: {str(e)}"
            )
    
    async def delete(self, file_path: str) -> bool:
        """
        Delete file from local storage.
        
        Args:
            file_path: Path to the file (URL format: /uploads/...)
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            # Convert URL path to filesystem path
            if file_path.startswith("/uploads/"):
                # Remove the /uploads/ prefix
                relative_path = file_path[8:]  # len("/uploads/") = 9
                fs_path = os.path.join(self.base_dir, relative_path)
            else:
                fs_path = os.path.join(self.base_dir, file_path)
            
            # Check if file exists
            if not os.path.exists(fs_path):
                print(f"File not found: {fs_path}")
                return False
            
            # Delete the file
            os.remove(fs_path)
            print(f"File deleted: {fs_path}")
            
            # Try to remove empty parent directories
            self._cleanup_empty_dirs(os.path.dirname(fs_path))
            
            return True
            
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    def _cleanup_empty_dirs(self, directory: str):
        """Recursively remove empty directories."""
        try:
            # Walk up from the directory to base_dir
            while directory and directory.startswith(self.base_dir):
                if os.path.exists(directory) and os.path.isdir(directory):
                    # Check if directory is empty
                    if not os.listdir(directory):
                        os.rmdir(directory)
                        print(f"Removed empty directory: {directory}")
                    else:
                        break
                directory = os.path.dirname(directory)
        except Exception as e:
            print(f"Error cleaning up directories: {e}")
    
    async def get_url(self, file_path: str) -> str:
        """
        Get URL for the file.
        
        Args:
            file_path: Filesystem path
            
        Returns:
            Public URL
        """
        # For local storage, we serve files through /uploads endpoint
        if file_path.startswith("/uploads/"):
            return file_path
        
        # If it's a relative path, prepend /uploads
        if file_path.startswith("uploads/"):
            return f"/{file_path}"
        
        # Otherwise, assume it's already a relative path from base_dir
        return f"/uploads/{file_path}"


class S3Storage(StorageService):
    """S3 storage implementation (placeholder)."""
    
    def __init__(self):
        # This would require boto3 and AWS credentials
        raise NotImplementedError("S3 storage not implemented yet")
    
    async def upload(self, file: UploadFile, base_path: str) -> str:
        raise NotImplementedError("S3 storage not implemented yet")
    
    async def delete(self, file_path: str) -> bool:
        raise NotImplementedError("S3 storage not implemented yet")
    
    async def get_url(self, file_path: str) -> str:
        raise NotImplementedError("S3 storage not implemented yet")


def get_storage() -> StorageService:
    """
    Factory function to get storage service.
    
    Returns:
        StorageService instance based on configuration
    """
    storage_type = settings.STORAGE_TYPE.lower()
    
    if storage_type == "s3":
        return S3Storage()
    elif storage_type == "local":
        return LocalStorage()
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")