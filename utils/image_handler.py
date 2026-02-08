"""
Image handler for photo uploads and compression.
Handles profile photos and visit photos with Supabase Storage.
"""

import os
from datetime import datetime
from typing import Optional, List
from PIL import Image
import io
from supabase import create_client, Client
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_supabase_client() -> Client:
    """Get Supabase client for storage operations."""
    try:
        supabase_url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
        supabase_key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
    except (AttributeError, KeyError):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase credentials not found.")
    
    return create_client(supabase_url, supabase_key)


def compress_image(image_bytes: bytes, max_width: int = 1200, quality: int = 85) -> bytes:
    """
    Compress an image to reduce file size.
    
    Args:
        image_bytes: Original image bytes
        max_width: Maximum width in pixels
        quality: JPEG quality (1-100)
        
    Returns:
        Compressed image bytes
    """
    # Open image from bytes
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert RGBA to RGB if necessary
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background
    
    # Resize if too wide
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)
    
    # Save to bytes with compression
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    return output.read()


def save_uploaded_photo(
    uploaded_file,
    resident_id: str,
    photo_type: str = "profile",
    bucket_name: str = None
) -> Optional[str]:
    """
    Save an uploaded photo to Supabase Storage with compression.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        resident_id: Resident's unique ID
        photo_type: Type of photo ('profile' or 'visit')
        bucket_name: Supabase storage bucket name (defaults to 'resident-photos')
        
    Returns:
        Public URL of uploaded photo or None if failed
    """
    try:
        if bucket_name is None:
            try:
                bucket_name = st.secrets.get("SUPABASE_BUCKET_NAME", os.getenv("SUPABASE_BUCKET_NAME", "resident-photos"))
            except (AttributeError, KeyError):
                bucket_name = os.getenv("SUPABASE_BUCKET_NAME", "resident-photos")
        
        # Read uploaded file
        image_bytes = uploaded_file.read()
        
        # Compress image
        compressed_bytes = compress_image(image_bytes)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{resident_id}/{timestamp}_{photo_type}.jpg"
        
        # Upload to Supabase Storage
        supabase = get_supabase_client()
        supabase.storage.from_(bucket_name).upload(
            filename,
            compressed_bytes,
            file_options={"content-type": "image/jpeg"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
        
        return public_url
    except Exception as e:
        print(f"Error saving photo: {e}")
        return None


def save_multiple_photos(
    uploaded_files: List,
    resident_id: str,
    photo_type: str = "visit",
    bucket_name: str = None
) -> List[str]:
    """
    Save multiple uploaded photos to Supabase Storage with compression.
    
    Args:
        uploaded_files: List of Streamlit uploaded file objects
        resident_id: Resident's unique ID
        photo_type: Type of photos
        bucket_name: Supabase storage bucket name
        
    Returns:
        List of public URLs to saved photos
    """
    saved_urls = []
    
    for idx, uploaded_file in enumerate(uploaded_files):
        # Add index to photo type to differentiate multiple photos
        indexed_type = f"{photo_type}_{idx+1}"
        url = save_uploaded_photo(uploaded_file, resident_id, indexed_type, bucket_name)
        if url:
            saved_urls.append(url)
    
    return saved_urls


def photo_exists(photo_url: str) -> bool:
    """
    Check if a photo URL is accessible.
    
    Args:
        photo_url: URL to photo
        
    Returns:
        True if accessible, False otherwise
    """
    try:
        import requests
        response = requests.head(photo_url, timeout=5)
        return response.status_code == 200
    except (requests.RequestException, Exception):
        return False


def get_photo_size_mb(photo_url: str) -> float:
    """
    Get photo file size in MB from URL.
    
    Args:
        photo_url: URL to photo
        
    Returns:
        File size in MB
    """
    try:
        import requests
        response = requests.head(photo_url, timeout=5)
        size_bytes = int(response.headers.get('content-length', 0))
        return size_bytes / (1024 * 1024)
    except (requests.RequestException, ValueError, Exception):
        return 0.0
