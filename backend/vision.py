import os
import io
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO

# Define base directory and model path for general YOLO detection
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(os.path.dirname(BASE_DIR), "yolov8n.pt")
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(BASE_DIR, "..", "yolov8n.pt")

# Load the general YOLO model
model = YOLO(MODEL_PATH)

# Strict whitelist of allowed produce items (Standard produce + Custom trained ones)
# This filters out hands, bowls, phones, and any non-produce objects.
ALLOWED_PRODUCE = [
    'banana', 'apple', 'orange', 'carrot', 'broccoli', 
    'tomato', 'onion', 'potato', 'garlic', 'potatoes', 
    'onions', 'tomatoes', 'garlics', 'fruit', 'vegetable'
]

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

        # Check for bounding boxes using general object detection
        if hasattr(result, 'boxes') and result.boxes is not None and len(result.boxes) > 0:
            # Find the best bounding box that matches our allowed produce list
            best_box = None
            highest_conf = 0.0
            
            for box in result.boxes:
                cls_idx = int(box.cls[0])
                conf = float(box.conf[0])
                name = result.names.get(cls_idx, "unknown").lower()
                
                # Check if the detected item is in our allowed whitelist and has good confidence
                if name in ALLOWED_PRODUCE and conf > highest_conf:
                    highest_conf = conf
                    best_box = box
                    item_name = name
                    confidence = conf

            # If no allowed produce was found or confidence is too low
            if best_box is None or confidence < 0.40:
                return {"detected": False, "message": "No valid produce detected or object filtered out."}
                
            # Generate the annotated frame with bounding boxes and labels for the valid item
            annotated_frame = result.plot()
        else:
            return {"detected": False, "message": "No recognizable object detected."}

        return {
            "detected": True,
            "primary_item": item_name,
            "confidence": round(confidence, 2),
            "annotated_frame": annotated_frame
        }
        
    except Exception as e:
        print(f"Vision Error: {e}")
        return {"detected": False}



# import os
# import numpy as np
# from ultralytics import YOLO
# from PIL import Image
# import io

# BASE_DIR = os.path.dirname(os.path.abspath(file))
# CUSTOM_MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")
# BASE_MODEL_PATH = os.path.join(BASE_DIR, "..", "yolov8n.pt")

# # Load both models into memory once on startup
# custom_model = YOLO(CUSTOM_MODEL_PATH) if os.path.exists(CUSTOM_MODEL_PATH) else None
# base_model = YOLO(BASE_MODEL_PATH) if os.path.exists(BASE_MODEL_PATH) else YOLO("yolov8n.pt")

# def analyze_image(image_bytes: bytes) -> dict:
#     """
#     Analyzes image bytes using both models hand-in-hand (Ensemble Method).
#     """
#     try:
#         image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
#         # 1. Get predictions from both models simultaneously
#         custom_results = custom_model.predict(image, verbose=False)[0] if custom_model else None
#         base_results = base_model.predict(image, verbose=False)[0]
        
#         custom_conf = 0.0
#         custom_item = "unknown"
        
#         # Extract custom model top prediction
#         if custom_results and hasattr(custom_results, 'probs') and custom_results.probs is not None:
#             c_idx = int(custom_results.probs.top1)
#             custom_conf = float(custom_results.probs.top1conf)
#             custom_item = custom_results.names.get(c_idx, "unknown")

#         # 2. Hand-in-Hand Logic (Consensus & Boosting)
#         # If your custom model is confident, it takes the lead
#         if custom_conf >= 0.55:
#             return {
#                 "detected": True,
#                 "primary_item": custom_item,
#                 "confidence": round(custom_conf, 2),
#                 "analysis_mode": "custom_lead"
#             }
            
#         # If custom model is unsure (e.g., 30% - 50% confidence), 
#         # check if the base model can corroborate or if we default to base model
#         if hasattr(base_results, 'probs') and base_results.probs is not None:
#             b_idx = int(base_results.probs.top1)
#             base_conf = float(base_results.probs.top1conf)
#             base_item = base_results.names.get(b_idx, "unknown")
            
#             # If custom model detected a valid produce item but with low confidence, 
#             # and base model agrees or has a strong alternative, we merge insights.
#             if custom_conf >= 0.20:
#                 return {
#                     "detected": True,
#                     "primary_item": custom_item, # Prioritize custom warehouse label
#                     "confidence": round((custom_conf + base_conf) / 2, 2), # Fused confidence
#                     "analysis_mode": "ensemble_fusion"
#                 }
#             else:
#                 # Custom model had no idea what it was; rely fully on base model
#                 return {
#                     "detected": True,
#                     "primary_item": base_item,
#                     "confidence": round(base_conf, 2),
#                     "analysis_mode": "base_fallback"
#                 }
                
#         elif custom_conf >= 0.20:
#             return {
#                 "detected": True,
#                 "primary_item": custom_item,
#                 "confidence": round(custom_conf, 2),
#                 "analysis_mode": "custom_solo"
#             }
            
#         return {"detected": False}
        
#     except Exception as e:
#         print(f"Hand-in-Hand Vision Error: {e}")
#         return {"detected": False}