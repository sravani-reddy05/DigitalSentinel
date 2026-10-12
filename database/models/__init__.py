# DigitalSentinel models package

from database.models.brand_model import (
    create_brand,
    get_brand,
    update_brand
)

from database.models.detection_model import (
    create_detection,
    get_all_detections,
    get_detection_by_id,
    update_detection_status
)

from database.models.user_model import (
    create_user,
    get_user_by_email
)
