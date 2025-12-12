"""Unit tests for feature extraction module."""

import pytest
import pandas as pd
from gender_detection.features import FeatureExtractor, extract_features


class TestFeatureExtractor:
    """Test suite for FeatureExtractor class."""

    @pytest.fixture
    def extractor(self):
        """Create FeatureExtractor instance."""
        return FeatureExtractor()

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'full_name': [
                'AMEGANVI Koffi Ama',
                'KOKOU Mensah',
                'DZIFA Akossiwa',
                'EDEM Kodjo'
            ]
        })

    def test_normalize_names(self, extractor, sample_data):
        """Test name normalization."""
        result = extractor._normalize_names(sample_data)
        
        assert result['full_name'].iloc[0] == 'AMEGANVI KOFFI AMA'
        assert all(result['full_name'].str.isupper())

    def test_parse_name_components(self, extractor, sample_data):
        """Test parsing of name components."""
        df = extractor._normalize_names(sample_data)
        result = extractor._parse_name_components(df)
        
        assert 'surname' in result.columns
        assert 'first_name' in result.columns
        assert result['surname'].iloc[0] == 'AMEGANVI'
        assert result['first_name'].iloc[0] == 'AMA'

    def test_extract_basic_features(self, extractor, sample_data):
        """Test basic feature extraction."""
        df = extractor._normalize_names(sample_data)
        df = extractor._parse_name_components(df)
        result = extractor._extract_basic_features(df)
        
        assert 'first_name_length' in result.columns
        assert 'nb_first_names' in result.columns
        assert result['first_name_length'].iloc[0] == 3  # AMA

    def test_extract_ethnic_features(self, extractor, sample_data):
        """Test ethnic pattern feature extraction."""
        df = extractor._normalize_names(sample_data)
        df = extractor._parse_name_components(df)
        result = extractor._extract_ethnic_features(df)
        
        # Check that ethnic features are created
        assert 'ends_ewe_fem' in result.columns
        assert 'ends_ewe_masc' in result.columns
        assert 'starts_ewe_fem' in result.columns

    def test_extract_phonetic_features(self, extractor, sample_data):
        """Test phonetic feature extraction."""
        df = extractor._normalize_names(sample_data)
        df = extractor._parse_name_components(df)
        result = extractor._extract_phonetic_features(df)
        
        assert 'vowel_count' in result.columns
        assert 'vowel_ratio' in result.columns
        assert 'syllable_count' in result.columns

    def test_full_feature_extraction(self, extractor, sample_data):
        """Test complete feature extraction pipeline."""
        result = extractor.extract_features(sample_data)
        
        # Check all expected features are present
        expected_features = [
            'first_name_length', 'nb_first_names',
            'ends_ewe_fem', 'ends_kabye_fem', 'ends_arabe_fem',
            'vowel_count', 'vowel_ratio', 'syllable_count',
            'gender_score', 'is_exception'
        ]
        
        for feature in expected_features:
            assert feature in result.columns

    def test_exception_handling(self, extractor):
        """Test handling of exception names."""
        df = pd.DataFrame({'full_name': ['SURNAME KOMI', 'SURNAME MAWULI']})
        result = extractor.extract_features(df)
        
        # KOMI should be marked as exception (female)
        komi_row = result[result['first_name'] == 'KOMI']
        assert komi_row['is_exception'].iloc[0] == 1
        assert komi_row['exception_value'].iloc[0] == 0

    def test_empty_dataframe(self, extractor):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame({'full_name': []})
        result = extractor.extract_features(df)
        
        assert len(result) == 0
        assert 'first_name_length' in result.columns

    def test_single_name(self, extractor):
        """Test handling of single names (no first name)."""
        df = pd.DataFrame({'full_name': ['AMEGANVI']})
        result = extractor.extract_features(df)
        
        assert result['first_name'].iloc[0] == ''
        assert result['nb_first_names'].iloc[0] == 0


def test_extract_features_convenience_function():
    """Test the convenience function."""
    df = pd.DataFrame({'full_name': ['AMEGANVI Koffi Ama']})
    result = extract_features(df)
    
    assert 'first_name_length' in result.columns
    assert 'gender_score' in result.columns
