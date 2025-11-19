"""
Wellness Score Prediction Module
Loads trained model and preprocessor to make predictions
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Union, List

# Get the model directory path
MODEL_DIR = Path(__file__).parent.parent / "model"


class WellnessPredictor:
    """Wellness score prediction class with model management"""
    
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.features = None
        self.metrics = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model, preprocessor, and metadata"""
        try:
            # Load model
            model_path = MODEL_DIR / "wellness_model.joblib"
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found at {model_path}")
            self.model = joblib.load(model_path)
            
            # Load preprocessor
            preprocessor_path = MODEL_DIR / "preprocessor.joblib"
            if not preprocessor_path.exists():
                raise FileNotFoundError(f"Preprocessor not found at {preprocessor_path}")
            self.preprocessor = joblib.load(preprocessor_path)
            
            # Load feature names
            features_path = MODEL_DIR / "feature_names.json"
            if features_path.exists():
                with open(features_path, 'r') as f:
                    feature_data = json.load(f)
                    self.features = feature_data.get('features', [])
            else:
                # Default features if file doesn't exist
                self.features = ['sleepHours', 'calories', 'steps', 'waterIntake', 'screenTime', 'stressLevel']
            
            # Load metrics
            metrics_path = MODEL_DIR / "metrics.json"
            if metrics_path.exists():
                with open(metrics_path, 'r') as f:
                    self.metrics = json.load(f)
            
            print(f"✓ Model loaded successfully")
            print(f"  Features: {self.features}")
            if self.metrics:
                print(f"  Model: {self.metrics.get('model_name', 'Unknown')}")
                print(f"  RMSE: {self.metrics.get('metrics', {}).get('rmse', 'N/A')}")
            
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            raise
    
    def predict(self, input_data: Union[Dict, pd.DataFrame]) -> float:
        """
        Predict wellness score for given input data
        
        Args:
            input_data: Dictionary or DataFrame with health metrics
        
        Returns:
            Predicted wellness score (0-100)
        """
        try:
            # Convert dict to DataFrame if needed
            if isinstance(input_data, dict):
                df = pd.DataFrame([input_data])
            else:
                df = input_data.copy()
            
            # Ensure all required features are present
            for feature in self.features:
                if feature not in df.columns:
                    df[feature] = 0  # Default value for missing features
            
            # Select only the features used during training
            df = df[self.features]
            
            # Preprocess
            X_processed = self.preprocessor.transform(df)
            
            # Predict
            prediction = self.model.predict(X_processed)
            
            # Ensure score is within valid range
            score = float(np.clip(prediction[0], 0, 100))
            
            return score
            
        except Exception as e:
            print(f"✗ Prediction error: {e}")
            raise
    
    def predict_batch(self, input_data: pd.DataFrame) -> np.ndarray:
        """
        Predict wellness scores for multiple inputs
        
        Args:
            input_data: DataFrame with multiple rows of health metrics
        
        Returns:
            Array of predicted wellness scores
        """
        try:
            df = input_data.copy()
            
            # Ensure all required features are present
            for feature in self.features:
                if feature not in df.columns:
                    df[feature] = 0
            
            # Select only the features used during training
            df = df[self.features]
            
            # Preprocess and predict
            X_processed = self.preprocessor.transform(df)
            predictions = self.model.predict(X_processed)
            
            # Clip scores to valid range
            scores = np.clip(predictions, 0, 100)
            
            return scores
            
        except Exception as e:
            print(f"✗ Batch prediction error: {e}")
            raise
    
    def get_model_info(self) -> Dict:
        """Return model metadata and metrics"""
        return {
            'features': self.features,
            'metrics': self.metrics,
            'model_loaded': self.model is not None,
            'preprocessor_loaded': self.preprocessor is not None
        }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance if available"""
        if hasattr(self.model, 'feature_importances_'):
            importance_dict = {
                feature: float(importance)
                for feature, importance in zip(self.features, self.model.feature_importances_)
            }
            # Sort by importance
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        return {}


# Global predictor instance
_predictor = None


def get_predictor() -> WellnessPredictor:
    """Get or create the global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = WellnessPredictor()
    return _predictor


def predict_wellness_score(input_data: Union[Dict, pd.DataFrame]) -> float:
    """
    Convenient function to predict wellness score
    
    Args:
        input_data: Dictionary or DataFrame with health metrics
            Expected keys: sleepHours, calories, steps, waterIntake, screenTime, stressLevel
    
    Returns:
        Predicted wellness score (0-100)
    
    Example:
        >>> score = predict_wellness_score({
        ...     'sleepHours': 7.5,
        ...     'calories': 2000,
        ...     'steps': 8000,
        ...     'waterIntake': 2.5,
        ...     'screenTime': 3,
        ...     'stressLevel': 4
        ... })
        >>> print(f"Wellness Score: {score:.2f}")
    """
    predictor = get_predictor()
    return predictor.predict(input_data)


def reload_model():
    """Reload the model (useful after retraining)"""
    global _predictor
    _predictor = None
    return get_predictor()


if __name__ == "__main__":
    # Test the predictor
    print("Testing Wellness Predictor...\n")
    
    # Sample input
    sample_data = {
        'sleepHours': 7.5,
        'calories': 2000,
        'steps': 8000,
        'waterIntake': 2.5,
        'screenTime': 3,
        'stressLevel': 4
    }
    
    try:
        score = predict_wellness_score(sample_data)
        print(f"\n🎯 Predicted Wellness Score: {score:.2f}/100")
        
        predictor = get_predictor()
        print(f"\n📊 Feature Importance:")
        for feature, importance in predictor.get_feature_importance().items():
            print(f"  {feature:15s}: {importance:.4f}")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
