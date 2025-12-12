#!/usr/bin/env python3
"""Script to update the model with new feedback data."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from gender_detection.model import update_model_with_feedback


def main():
    """Update model with feedback."""
    print("🔄 Updating model with feedback data...")
    update_model_with_feedback()
    print("✅ Model update complete!")


if __name__ == '__main__':
    main()
