import io
from typing import Dict, Any
from PIL import Image
from ultralytics import YOLO

# ==========================================
# 1. LOAD ALL CUSTOM MODELS
# ==========================================
# We load them into a dictionary once at startup so the server doesn't 
# waste time reloading the files every time a new image is scanned.
CUSTOM_MODELS = {
    "garlic": YOLO("models/best_garlics.pt"),
    "potato": YOLO("models/best_potatoes.pt"),
    "tomato": YOLO("models/best_tomatoes.pt"),
    "general": YOLO("models/best.pt")
}

def analyze_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Runs YOLOv8 object detection on the uploaded image using all custom models.
    Returns the detection with the highest confidence score.
    """
    img = Image.open(io.BytesIO(image_bytes))
    
    all_detections = []

    # ==========================================
    # 2. SCAN IMAGE WITH EVERY MODEL
    # ==========================================
    for model_name, model in CUSTOM_MODELS.items():
        # conf=0.25 ignores extremely weak guesses
        results = model.predict(img, conf=0.25, verbose=False)
        
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id].lower()
                confidence = float(box.conf[0])
                
                all_detections.append({
                    "label": label,
                    "confidence": round(confidence, 2)
                })

    # ==========================================
    # 3. RETURN THE BEST MATCH TO MAIN.PY
    # ==========================================
    if not all_detections:
        return {"detected": False, "primary_item": None, "confidence": 0.0}

    # Find the single detection with the absolute highest confidence score
    best_match = max(all_detections, key=lambda x: x["confidence"])

    return {
        "detected": True,
        "primary_item": best_match["label"],
        "confidence": best_match["confidence"]
    }