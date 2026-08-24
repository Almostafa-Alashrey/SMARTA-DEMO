import os
import io
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")

# Load the YOLO model
model = YOLO(MODEL_PATH)

# Valid and allowed classes for the demo (Strictly the 4 trained produce items)
VALID_CLASSES = ['potato', 'onion', 'tomato', 'garlic', 'potatoes', 'onions', 'tomatoes', 'garlics']

def analyze_image(image_bytes: bytes) -> dict:
    try:
        # Decode image bytes using OpenCV and PIL
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = model.predict(image, verbose=False)
        result = results[0]
        
        item_name = "unknown"
        confidence = 0.0

        # Check if the model is running classification
        if hasattr(result, 'probs') and result.probs is not None:
            top_class_index = int(result.probs.top1)
            confidence = float(result.probs.top1conf)
            raw_item_name = result.names.get(top_class_index, "unknown").lower()
            
            # Print raw detection details in the terminal for debugging
            print(f"--> Model detected raw: {raw_item_name} with confidence {confidence}")

            # Reject detection if confidence is below 70% or if the item is outside the 4 allowed categories
            if raw_item_name not in VALID_CLASSES or confidence < 0.70:
                return {"detected": False, "message": "Produce not recognized among the 4 trained categories."}
            
            item_name = raw_item_name
            
            # Draw a custom visual bounding box overlay and label on the image
            h, w, _ = img_cv.shape
            cv2.rectangle(img_cv, (50, 50), (w - 50, h - 50), (0, 255, 0), 4)
            label_text = f"{item_name.capitalize()} ({confidence*100:.1f}%)"
            cv2.putText(img_cv, label_text, (60, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            annotated_frame = img_cv

        # Check if the model is running object detection (bounding boxes)
        elif hasattr(result, 'boxes') and result.boxes is not None and len(result.boxes) > 0:
            box = result.boxes[0]
            top_class_index = int(box.cls[0])
            confidence = float(box.conf[0])
            raw_item_name = result.names.get(top_class_index, "unknown").lower()
            
            if raw_item_name not in VALID_CLASSES or confidence < 0.70:
                return {"detected": False, "message": "Produce not recognized."}
                
            item_name = raw_item_name
            annotated_frame = result.plot()
        else:
            return {"detected": False, "message": "No recognizable produce detected."}

        return {
            "detected": True,
            "primary_item": item_name,
            "confidence": round(confidence, 2),
            "annotated_frame": annotated_frame
        }
        
    except Exception as e:
        print(f"Vision Error: {e}")
        return {"detected": False}