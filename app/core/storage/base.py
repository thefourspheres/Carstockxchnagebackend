class StorageProvider:
    async def upload(self, file, path: str) -> str:
        raise NotImplementedError
