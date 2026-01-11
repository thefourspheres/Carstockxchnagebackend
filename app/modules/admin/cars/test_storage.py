# test_storage.py
import asyncio
import os
from fastapi import UploadFile
import io

async def test_storage():
    from app.core.storage.factory import get_storage
    
    # Get storage instance
    storage = get_storage()
    print(f"Storage type: {type(storage).__name__}")
    
    # Create a dummy webp file for testing
    dummy_content = b"dummy webp content"  # In reality, this would be actual webp data
    
    # Create UploadFile
    dummy_file = UploadFile(
        filename="test_image.webp",
        file=io.BytesIO(dummy_content),
        content_type="image/webp"
    )
    
    try:
        # Test upload
        url = await storage.upload(dummy_file, "test/organization/cars/123")
        print(f"✅ Upload successful: {url}")
        print(f"   File should be at: uploads/test/organization/cars/123/")
        
        # Test delete
        success = await storage.delete(url)
        print(f"✅ Delete successful: {success}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_storage())