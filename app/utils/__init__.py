"""Utility package for wellness prediction system"""

from .predict import predict_wellness_score, get_predictor, reload_model
from .recommend import get_recommendations, get_category_scores
from .db_utils import (
    add_entry,
    get_latest,
    get_history,
    delete_entry,
    fetch_for_dashboard,
    get_db
)

__all__ = [
    'predict_wellness_score',
    'get_predictor',
    'reload_model',
    'get_recommendations',
    'get_category_scores',
    'add_entry',
    'get_latest',
    'get_history',
    'delete_entry',
    'fetch_for_dashboard',
    'get_db'
]
