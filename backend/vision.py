import io
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from PIL import Image
from ultralytics import YOLO

# Load pre-trained lightweight YOLOv8 model
model = YOLO("yolov8n.pt")

# USDA ARS Handbook 66 - Storage Baselines (Optimal Temp in °C, Max Days at Optimal Conditions)
# تم تقليل القائمة لتتناسب فقط مع الفواكه والخضروات التي يدعمها موديل COCO الافتراضي لضمان استقرار الـ Demo
USDA_BASELINE: Dict[str, Tuple[float, int]] = {
    # Fruits
    "apple": (0.0, 90),
    "banana": (13.0, 7),
    "orange": (4.0, 30),
    
    # Vegetables
    "carrot": (0.0, 28),
    "broccoli": (0.0, 14)
}

def predict_shelf_life(item_name: str, current_temp: float, current_hum: float) -> Dict[str, Any]:
    """
    Calculates estimated days to expire using Q10 temperature coefficient degradation kinetics.
    """
    item_key = item_name.lower()
    if item_key not in USDA_BASELINE:
        # Default fallback for unlisted produce
        opt_temp, base_days = (4.0, 10)
    else:
        opt_temp, base_days = USDA_BASELINE[item_key]

    # Q10 Model: Spoilage rate doubles every 10°C above optimal temperature
    temp_diff = max(0.0, current_temp - opt_temp)
    degradation_factor = math.pow(2.0, temp_diff / 10.0)
    
    # Humidity penalty factor (low humidity causes shriveling/spoilage acceleration)
    hum_factor = 1.0
    if current_hum < 85.0:
        hum_factor = 1.25

    adjusted_days = max(1, round(base_days / (degradation_factor * hum_factor)))
    expiration_date = (datetime.now() + timedelta(days=adjusted_days)).strftime("%Y-%m-%d")

    return {
        "item": item_name.capitalize(),
        "optimal_temp_c": opt_temp,
        "estimated_days_remaining": adjusted_days,
        "estimated_expiration_date": expiration_date,
        "degradation_risk": "High" if adjusted_days <= 3 else "Moderate" if adjusted_days <= 7 else "Low"
    }

def analyze_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Runs YOLOv8 object detection on produce image stream.
    """
    img = Image.open(io.BytesIO(image_bytes))
    
    # تحديد الكلاسات المسموحة فقط لتجاهل الأشخاص والموبايلات وغيرها
    # 46: banana, 47: apple, 49: orange, 50: broccoli, 51: carrot
    results = model(img, classes=[46, 47, 49, 50, 51])

    detected_items = []
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id].lower()
            confidence = float(box.conf[0])
            
            # Keep detections above confidence threshold
            if confidence > 0.25:
                detected_items.append({
                    "label": label,
                    "confidence": round(confidence * 100, 1),
                    "is_known_produce": label in USDA_BASELINE
                })

    if not detected_items:
        return {"detected": False, "primary_item": None, "all_detected": []}

    # Prioritize items matching our produce taxonomy, otherwise pick highest confidence
    known_produce = [d for d in detected_items if d["is_known_produce"]]
    if known_produce:
        primary = max(known_produce, key=lambda x: x["confidence"])
    else:
        primary = max(detected_items, key=lambda x: x["confidence"])

    return {
        "detected": True,
        "primary_item": primary["label"],
        "confidence": primary["confidence"],
        "all_detected": detected_items
    }