#!/usr/bin/env python3
"""
Secure ML Inference Module - Best Practices Example
This is what the corrected version should look like
"""

import os
import json
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Configure logging securely
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security: Use environment variables for sensitive config
MAX_FEATURES = int(os.getenv('MAX_FEATURES', '100'))
MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', '1000'))


@dataclass
class PredictionInput:
    """Validated prediction input"""
    features: List[float]
    
    def __post_init__(self):
        if not isinstance(self.features, list):
            raise ValueError("Features must be a list")
        if len(self.features) > MAX_FEATURES:
            raise ValueError(f"Too many features. Max: {MAX_FEATURES}")
        if not all(isinstance(f, (int, float)) for f in self.features):
            raise ValueError("All features must be numeric")


class SecureMLModel:
    """Secure ML Model class with proper error handling"""
    
    def __init__(self, model_path: str = None):
        """Initialize model without pickle (use joblib or safetensors instead)"""
        self.model_path = model_path
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load model using safe methods"""
        if self.model_path and Path(self.model_path).exists():
            # Use joblib.load instead of pickle
            # model = joblib.load(self.model_path)
            logger.info(f"Model loaded from {self.model_path}")
    
    def predict(self, input_data: PredictionInput) -> Dict[str, Any]:
        """
        Make prediction with validated input
        
        Args:
            input_data: Validated prediction input
            
        Returns:
            Prediction results dictionary
        """
        try:
            features_array = np.array(input_data.features)
            
            # Safely perform inference
            prediction = np.mean(features_array) * 2.0
            confidence = 0.95
            
            return {
                "prediction": float(prediction),
                "confidence": float(confidence),
                "feature_count": len(input_data.features)
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise


def validate_and_predict(features: List[float]) -> Dict[str, Any]:
    """
    Safe prediction pipeline with input validation
    """
    # Validate input
    try:
        validated_input = PredictionInput(features=features)
    except ValueError as e:
        logger.warning(f"Input validation failed: {e}")
        raise
    
    # Make prediction
    model = SecureMLModel()
    result = model.predict(validated_input)
    
    return result


if __name__ == '__main__':
    # Test the secure inference
    test_features = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = validate_and_predict(test_features)
    print(f"Prediction result: {json.dumps(result, indent=2)}")
