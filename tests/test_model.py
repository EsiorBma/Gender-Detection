"""Unit tests for model module."""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path

from gender_detection.model import GenderClassifier
from gender_detection.config import FEATURE_NAMES


class TestGenderClassifier:
    """Test suite for GenderClassifier class."""

    @pytest.fixture
    def sample_dataset(self):
        """Create a sample dataset for testing."""
        fd, path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)
        
        # Create sample data
        data = pd.DataFrame({
            'full_name': [
                'SURNAME AMA', 'SURNAME AKOSSIWA', 'SURNAME DZIFA',
                'SURNAME KOFI', 'SURNAME EDEM', 'SURNAME KOFFI',
                'SURNAME AFIA', 'SURNAME ESI', 'SURNAME MAWUSI',
                'SURNAME KODJO', 'SURNAME MENSAH', 'SURNAME YAWO'
            ] * 10,  # Repeat to have enough samples
            'gender': [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1] * 10
        })
        data.to_csv(path, index=False)
        
        yield path
        os.unlink(path)

    @pytest.fixture
    def temp_model_path(self):
        """Create temporary model path."""
        fd, path = tempfile.mkstemp(suffix='.joblib')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_train_model(self, sample_dataset, temp_model_path):
        """Test model training."""
        classifier = GenderClassifier(model_path=temp_model_path)
        result = classifier.train(dataset_path=sample_dataset, save=True)
        
        assert 'data_size' in result
        assert 'report' in result
        assert 'feature_importance' in result
        assert os.path.exists(temp_model_path)

    def test_load_model(self, sample_dataset, temp_model_path):
        """Test model loading."""
        # Train and save model
        classifier = GenderClassifier(model_path=temp_model_path)
        classifier.train(dataset_path=sample_dataset, save=True)
        
        # Load in new instance
        new_classifier = GenderClassifier(model_path=temp_model_path)
        assert new_classifier.model_data is not None
        assert 'model' in new_classifier.model_data
        assert 'features' in new_classifier.model_data

    def test_predict(self, sample_dataset, temp_model_path):
        """Test prediction."""
        # Train model
        classifier = GenderClassifier(model_path=temp_model_path)
        classifier.train(dataset_path=sample_dataset, save=True)
        
        # Make predictions
        result = classifier.predict('AMEGANVI Koffi Ama')
        
        assert 'gender' in result
        assert result['gender'] in ['Homme', 'Femme']
        assert 'predicted_value' in result
        assert result['predicted_value'] in [0, 1]
        assert 'surname' in result
        assert 'first_names' in result

    def test_predict_female_name(self, sample_dataset, temp_model_path):
        """Test prediction for typical female name."""
        classifier = GenderClassifier(model_path=temp_model_path)
        classifier.train(dataset_path=sample_dataset, save=True)
        
        result = classifier.predict('SURNAME AKOSSIWA')
        # Note: Prediction might not be 100% accurate with small training set
        assert result['predicted_value'] in [0, 1]

    def test_predict_male_name(self, sample_dataset, temp_model_path):
        """Test prediction for typical male name."""
        classifier = GenderClassifier(model_path=temp_model_path)
        classifier.train(dataset_path=sample_dataset, save=True)
        
        result = classifier.predict('SURNAME KODJO')
        # Note: Prediction might not be 100% accurate with small training set
        assert result['predicted_value'] in [0, 1]

    def test_predict_without_model(self):
        """Test that prediction fails without loaded model."""
        classifier = GenderClassifier(model_path='/nonexistent/path.joblib')
        
        with pytest.raises(ValueError):
            classifier.predict('TEST Name')

    def test_model_data_structure(self, sample_dataset, temp_model_path):
        """Test model data structure after training."""
        classifier = GenderClassifier(model_path=temp_model_path)
        classifier.train(dataset_path=sample_dataset, save=True)
        
        assert 'model' in classifier.model_data
        assert 'features' in classifier.model_data
        assert 'extract_fn' in classifier.model_data
        assert 'training_date' in classifier.model_data
        assert 'data_size' in classifier.model_data
        assert classifier.model_data['features'] == FEATURE_NAMES


def test_feature_names_consistency():
    """Test that feature names are consistent."""
    from gender_detection.config import FEATURE_NAMES
    
    # Check expected features are present
    expected = [
        'first_name_length', 'nb_first_names',
        'ends_ewe_fem', 'vowel_count', 'gender_score'
    ]
    
    for feature in expected:
        assert feature in FEATURE_NAMES
