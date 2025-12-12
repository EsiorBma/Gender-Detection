"""Feature extraction module for gender classification."""

import re
import pandas as pd
from typing import List, Dict, Any
from .config import ENDINGS, PREFIXES, GENDER_EXCEPTIONS


class FeatureExtractor:
    """Extract linguistic features from Togolese names."""

    def __init__(self):
        """Initialize feature extractor with linguistic patterns."""
        self.endings = ENDINGS
        self.prefixes = PREFIXES
        self.exceptions = GENDER_EXCEPTIONS

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract all features from a DataFrame of names.

        Args:
            df: DataFrame with 'full_name' column

        Returns:
            DataFrame with extracted features
        """
        # 1. Normalize names
        df = self._normalize_names(df)

        # 2. Parse name components
        df = self._parse_name_components(df)

        # 3. Extract basic features
        df = self._extract_basic_features(df)

        # 4. Extract ethnic pattern features
        df = self._extract_ethnic_features(df)

        # 5. Extract phonetic features
        df = self._extract_phonetic_features(df)

        # 6. Handle exceptions
        df = self._handle_exceptions(df)

        # 7. Create composite features
        df = self._create_composite_features(df)

        return df

    def _normalize_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize name strings."""
        df = df.copy()
        df['full_name'] = (
            df['full_name']
            .str.upper()
            .str.strip()
            .str.replace(r'\s+', ' ', regex=True)
        )
        return df

    def _parse_name_components(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse full name into surname and first names."""
        df = df.copy()
        split_names = df['full_name'].str.split(n=1, expand=True)
        df['surname'] = split_names[0]
        df['first_names'] = split_names[1] if 1 in split_names.columns else ''
        df['first_names'] = df['first_names'].fillna('')

        # Handle compound first names
        df['first_names'] = (
            df['first_names']
            .str.replace('-', ' ')
            .str.split()
        )

        # Extract main first name (last one)
        df['first_name'] = df['first_names'].apply(
            lambda x: x[-1] if x else ''
        )

        return df

    def _extract_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract basic name features."""
        df = df.copy()
        df['first_name_length'] = df['first_name'].apply(len)
        df['nb_first_names'] = df['first_names'].apply(len)
        return df

    def _extract_ethnic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract ethnic pattern features (endings and prefixes)."""
        df = df.copy()

        # Ending patterns
        for group, terms in self.endings.items():
            df[f'ends_{group}'] = df['first_name'].apply(
                lambda x: int(any(x.endswith(e) for e in terms))
            )

        # Prefix patterns
        for group, terms in self.prefixes.items():
            df[f'starts_{group}'] = df['first_name'].apply(
                lambda x: int(any(x.startswith(p) for p in terms))
            )

        return df

    def _extract_phonetic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract phonetic features from names."""
        df = df.copy()

        # Vowel count
        df['vowel_count'] = df['first_name'].apply(
            lambda x: len(re.findall(r'[AEIOUYÉÈÊ]', x))
        )

        # Consonant count
        df['consonant_count'] = df['first_name'].apply(
            lambda x: len(re.findall(r'[BCDFGHJKLMNPQRSTVWXZ]', x))
        )

        # Vowel ratio
        df['vowel_ratio'] = df['vowel_count'] / (df['first_name_length'] + 1e-6)

        # Syllable count
        df['syllable_count'] = df['first_name'].apply(
            lambda x: len(re.findall(r'[AEIOUYÉÈÊ]+', x))
        )

        # Vowel position (first vowel position as ratio)
        df['vowel_position'] = df['first_name'].apply(self._get_vowel_position)

        return df

    def _get_vowel_position(self, name: str) -> float:
        """Get position of first vowel as ratio of name length."""
        if not name:
            return 0.0
        match = re.search(r'[AEIOUYÉÈÊ]', name)
        return match.start() / len(name) if match else 0.0

    def _handle_exceptions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle special case names with known gender."""
        df = df.copy()
        df['is_exception'] = df['first_name'].apply(
            lambda x: 1 if x in self.exceptions else 0
        )
        df['exception_value'] = df['first_name'].apply(
            lambda x: self.exceptions.get(x, 0.5)
        )
        return df

    def _create_composite_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create composite features from basic features."""
        df = df.copy()

        # Gender score based on weighted ethnic patterns
        df['gender_score'] = (
            0.4 * (df['ends_ewe_fem'] + df['ends_kabye_fem'] + df['ends_arabe_fem'])
            - 0.4 * (df['ends_ewe_masc'] + df['ends_kabye_masc'] + df['ends_arabe_masc'])
            + 0.2 * (df['starts_ewe_fem'] + df['starts_kabye_fem'])
            - 0.2 * (df['starts_ewe_masc'] + df['starts_kabye_masc'])
            + 0.1 * df['vowel_ratio']
        )

        return df


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function to extract features.

    Args:
        df: DataFrame with 'full_name' column

    Returns:
        DataFrame with extracted features
    """
    extractor = FeatureExtractor()
    return extractor.extract_features(df)
