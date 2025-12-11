"""
Gender Detection Package for Togolese Names.

A machine learning-based system for predicting gender from full names,
optimized for Togolese naming conventions (Ewe, Kabyé, Arabic).
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "ambroisekouwadan52@gmail.com"

from .model import GenderClassifier
from .features import FeatureExtractor

__all__ = ["GenderClassifier", "FeatureExtractor"]
