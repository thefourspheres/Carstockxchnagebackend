# app/core/storage_simple.py
import os
from fastapi import UploadFile

class SimpleStorage:
    """Simple local storage for development"""
    
    async def upload(self, file: UploadFile, base_path: str) -> str:
        """Simple upload to local filesystem"""
        # Create the uploads directory
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate file path
        filename = f"{os.urandom(8).hex()}.webp"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Return relative path
        return f"/uploads/{filename}"
    
    async def delete(self, path: str) -> bool:
        """Delete file"""
        try:
            # Remove leading slash
            if path.startswith("/"):
                path = path[1:]
            
            if os.path.exists(path):
                os.remove(path)
                return True
            return False
        except Exception:
            return False

def get_storage():
    return SimpleStorage()