# app/core/storage/__init__.py
"""
Storage module for handling file uploads and storage.
"""

from .factory import get_storage, StorageService

__version__ = "1.0.0"
__all__ = ["get_storage", "StorageService"]