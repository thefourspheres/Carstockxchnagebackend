import os
from uuid import uuid4

from app.core.storage.base import StorageProvider

class LocalStorage(StorageProvider):

    async def upload(self, file, path: str) -> str:
        os.makedirs(path, exist_ok=True)

        filename = f"{uuid4()}.webp"
        full_path = os.path.join(path, filename)

        with open(full_path, "wb") as f:
            f.write(await file.read())

        return full_path
