import os
import numpy as np
from ultralytics import YOLO
from PIL import Image
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOM_MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")
BASE_MODEL_PATH = os.path.join(BASE_DIR, "..", "yolov8n.pt")

# Load both models into memory once on startup
custom_model = YOLO(CUSTOM_MODEL_PATH) if os.path.exists(CUSTOM_MODEL_PATH) else None
base_model = YOLO(BASE_MODEL_PATH) if os.path.exists(BASE_MODEL_PATH) else YOLO("yolov8n.pt")

def analyze_image(image_bytes: bytes) -> dict:
    """
    Analyzes image bytes using both models hand-in-hand (Ensemble Method).
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # 1. Get predictions from both models simultaneously
        custom_results = custom_model.predict(image, verbose=False)[0] if custom_model else None
        base_results = base_model.predict(image, verbose=False)[0]
        
        custom_conf = 0.0
        custom_item = "unknown"
        
        # Extract custom model top prediction
        if custom_results and hasattr(custom_results, 'probs') and custom_results.probs is not None:
            c_idx = int(custom_results.probs.top1)
            custom_conf = float(custom_results.probs.top1conf)
            custom_item = custom_results.names.get(c_idx, "unknown")

        # 2. Hand-in-Hand Logic (Consensus & Boosting)
        # If your custom model is confident, it takes the lead
        if custom_conf >= 0.55:
            return {
                "detected": True,
                "primary_item": custom_item,
                "confidence": round(custom_conf, 2),
                "analysis_mode": "custom_lead"
            }
            
        # If custom model is unsure (e.g., 30% - 50% confidence), 
        # check if the base model can corroborate or if we default to base model
        if hasattr(base_results, 'probs') and base_results.probs is not None:
            b_idx = int(base_results.probs.top1)
            base_conf = float(base_results.probs.top1conf)
            base_item = base_results.names.get(b_idx, "unknown")
            
            # If custom model detected a valid produce item but with low confidence, 
            # and base model agrees or has a strong alternative, we merge insights.
            if custom_conf >= 0.20:
                return {
                    "detected": True,
                    "primary_item": custom_item, # Prioritize custom warehouse label
                    "confidence": round((custom_conf + base_conf) / 2, 2), # Fused confidence
                    "analysis_mode": "ensemble_fusion"
                }
            else:
                # Custom model had no idea what it was; rely fully on base model
                return {
                    "detected": True,
                    "primary_item": base_item,
                    "confidence": round(base_conf, 2),
                    "analysis_mode": "base_fallback"
                }
                
        elif custom_conf >= 0.20:
            return {
                "detected": True,
                "primary_item": custom_item,
                "confidence": round(custom_conf, 2),
                "analysis_mode": "custom_solo"
            }
            
        return {"detected": False}
        
    except Exception as e:
        print(f"Hand-in-Hand Vision Error: {e}")
        return {"detected": False}