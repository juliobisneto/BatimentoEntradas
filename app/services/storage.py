"""
Supabase Storage Service
Handles file upload/download from Supabase Storage
"""
from typing import Optional, List
import os
from app.database import settings

# Only import supabase if credentials are configured
supabase_client = None
if settings.supabase_url and settings.supabase_key:
    try:
        from supabase import create_client, Client
        supabase_client: Client = create_client(settings.supabase_url, settings.supabase_key)
    except ImportError:
        print("⚠️  Supabase package not installed. Install with: pip install supabase")
    except Exception as e:
        print(f"⚠️  Failed to initialize Supabase client: {e}")

# Storage bucket name
BUCKET_NAME = "csv-files"

def is_storage_enabled() -> bool:
    """Check if Supabase storage is configured and available"""
    return supabase_client is not None

def upload_csv_file(file_name: str, file_content: bytes) -> dict:
    """
    Upload a CSV file to Supabase Storage
    
    Args:
        file_name: Name of the file
        file_content: File content as bytes
        
    Returns:
        dict with upload response
        
    Raises:
        Exception if storage is not configured or upload fails
    """
    if not is_storage_enabled():
        raise Exception("Supabase storage is not configured. Set SUPABASE_URL and SUPABASE_KEY environment variables.")
    
    file_path = f"uploads/{file_name}"
    
    try:
        response = supabase_client.storage.from_(BUCKET_NAME).upload(
            file_path,
            file_content,
            file_options={"content-type": "text/csv"}
        )
        return {
            "success": True,
            "path": file_path,
            "message": f"File {file_name} uploaded successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to upload file {file_name}"
        }

def download_csv_file(file_name: str) -> Optional[bytes]:
    """
    Download a CSV file from Supabase Storage
    
    Args:
        file_name: Name of the file to download
        
    Returns:
        File content as bytes or None if not found
    """
    if not is_storage_enabled():
        raise Exception("Supabase storage is not configured")
    
    file_path = f"uploads/{file_name}"
    
    try:
        response = supabase_client.storage.from_(BUCKET_NAME).download(file_path)
        return response
    except Exception as e:
        print(f"Error downloading file {file_name}: {e}")
        return None

def list_csv_files(folder: str = "uploads") -> List[dict]:
    """
    List all CSV files in a folder
    
    Args:
        folder: Folder path in storage
        
    Returns:
        List of file information dicts
    """
    if not is_storage_enabled():
        raise Exception("Supabase storage is not configured")
    
    try:
        files = supabase_client.storage.from_(BUCKET_NAME).list(folder)
        return files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def delete_csv_file(file_name: str) -> dict:
    """
    Delete a CSV file from Supabase Storage
    
    Args:
        file_name: Name of the file to delete
        
    Returns:
        dict with deletion status
    """
    if not is_storage_enabled():
        raise Exception("Supabase storage is not configured")
    
    file_path = f"uploads/{file_name}"
    
    try:
        response = supabase_client.storage.from_(BUCKET_NAME).remove([file_path])
        return {
            "success": True,
            "message": f"File {file_name} deleted successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to delete file {file_name}"
        }

def get_public_url(file_name: str) -> Optional[str]:
    """
    Get public URL for a file (if bucket is public)
    
    Args:
        file_name: Name of the file
        
    Returns:
        Public URL string or None
    """
    if not is_storage_enabled():
        return None
    
    file_path = f"uploads/{file_name}"
    
    try:
        response = supabase_client.storage.from_(BUCKET_NAME).get_public_url(file_path)
        return response
    except Exception as e:
        print(f"Error getting public URL: {e}")
        return None



