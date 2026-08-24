import os
from ultralytics import YOLO
from PIL import Image
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")

# Load model
model = YOLO(MODEL_PATH)

def analyze_image(image_bytes: bytes) -> dict:
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = model.predict(image, verbose=False)
        result = results[0]
        
        # Check for classification probabilities
        if hasattr(result, 'probs') and result.probs is not None:
            top_class_index = int(result.probs.top1)
            confidence = float(result.probs.top1conf)
            item_name = result.names.get(top_class_index, "unknown")
            
            return {
                "detected": True,
                "primary_item": item_name,
                "confidence": round(confidence, 2)
            }
        return {"detected": False}
    except Exception as e:
        print(f"Vision Error: {e}")
        return {"detected": False}