"""Utils package initialization."""
from .auth import (
    load_config,
    init_authenticator,
    check_authentication,
    get_current_user,
    get_current_user_name,
    logout
)
from .id_generator import generate_unique_id, validate_unique_id_format
from .image_handler import (
    compress_image,
    save_uploaded_photo,
    save_multiple_photos,
    photo_exists,
    get_photo_size_mb
)
from .validators import (
    validate_phone,
    validate_age,
    validate_blood_pressure,
    validate_temperature,
    validate_pulse,
    validate_weight,
    validate_height,
    validate_spo2,
    calculate_bmi,
    get_bmi_category,
    validate_required_field
)

__all__ = [
    'load_config',
    'init_authenticator',
    'check_authentication',
    'get_current_user',
    'get_current_user_name',
    'logout',
    'generate_unique_id',
    'validate_unique_id_format',
    'compress_image',
    'save_uploaded_photo',
    'save_multiple_photos',
    'photo_exists',
    'get_photo_size_mb',
    'validate_phone',
    'validate_age',
    'validate_blood_pressure',
    'validate_temperature',
    'validate_pulse',
    'validate_weight',
    'validate_height',
    'validate_spo2',
    'calculate_bmi',
    'get_bmi_category',
    'validate_required_field'
]
