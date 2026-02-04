"""
Image handler for photo uploads and compression.
Handles profile photos and visit photos with proper compression and storage.
"""

import os
from datetime import datetime
from typing import Optional, List
from PIL import Image
import io


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
    upload_dir: str = "uploaded_photos"
) -> Optional[str]:
    """
    Save an uploaded photo with compression.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        resident_id: Resident's unique ID
        photo_type: Type of photo ('profile' or 'visit')
        upload_dir: Directory to save photos
        
    Returns:
        Relative path to saved photo or None if failed
    """
    try:
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # Read uploaded file
        image_bytes = uploaded_file.read()
        
        # Compress image
        compressed_bytes = compress_image(image_bytes)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{resident_id}_{timestamp}_{photo_type}.jpg"
        filepath = os.path.join(upload_dir, filename)
        
        # Save compressed image
        with open(filepath, 'wb') as f:
            f.write(compressed_bytes)
        
        return filepath
    except Exception as e:
        print(f"Error saving photo: {e}")
        return None


def save_multiple_photos(
    uploaded_files: List,
    resident_id: str,
    photo_type: str = "visit",
    upload_dir: str = "uploaded_photos"
) -> List[str]:
    """
    Save multiple uploaded photos with compression.
    
    Args:
        uploaded_files: List of Streamlit uploaded file objects
        resident_id: Resident's unique ID
        photo_type: Type of photos
        upload_dir: Directory to save photos
        
    Returns:
        List of relative paths to saved photos
    """
    saved_paths = []
    
    for idx, uploaded_file in enumerate(uploaded_files):
        # Add index to photo type to differentiate multiple photos
        indexed_type = f"{photo_type}_{idx+1}"
        filepath = save_uploaded_photo(uploaded_file, resident_id, indexed_type, upload_dir)
        if filepath:
            saved_paths.append(filepath)
    
    return saved_paths


def photo_exists(photo_path: str) -> bool:
    """
    Check if a photo file exists.
    
    Args:
        photo_path: Path to photo file
        
    Returns:
        True if exists, False otherwise
    """
    return os.path.exists(photo_path)


def get_photo_size_mb(photo_path: str) -> float:
    """
    Get photo file size in MB.
    
    Args:
        photo_path: Path to photo file
        
    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(photo_path)
        return size_bytes / (1024 * 1024)
    except:
        return 0.0
