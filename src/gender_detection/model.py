"""Model training and prediction module."""

import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from pathlib import Path

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import classification_report, make_scorer, recall_score
from sklearn.inspection import permutation_importance
from xgboost import XGBClassifier

from .config import (
    MODEL_PATH,
    DATASET_PATH,
    FEATURE_NAMES,
    FEATURE_IMPORTANCE_PATH,
    TRAINING_REPORT_PATH,
    MODEL_CONFIG
)
from .features import FeatureExtractor
from .database import db


class GenderClassifier:
    """Machine learning model for gender classification from names."""

    def __init__(self, model_path: str = None):
        """
        Initialize gender classifier.

        Args:
            model_path: Path to saved model file
        """
        self.model_path = model_path or str(MODEL_PATH)
        self.model_data = None
        self.feature_extractor = FeatureExtractor()
        self.load_model()

    def load_model(self) -> bool:
        """
        Load trained model from disk.

        Returns:
            True if model loaded successfully
        """
        try:
            self.model_data = joblib.load(self.model_path)
            return True
        except FileNotFoundError:
            print(f"Model not found at {self.model_path}")
            return False

    def predict(self, full_name: str) -> Dict[str, Any]:
        """
        Predict gender from full name.

        Args:
            full_name: Complete name to analyze

        Returns:
            Dictionary with prediction results
        """
        if self.model_data is None:
            raise ValueError("Model not loaded. Train model first.")

        # Create DataFrame and extract features
        temp_df = pd.DataFrame([{'full_name': full_name}])
        temp_df = self.feature_extractor.extract_features(temp_df)

        # Ensure all features are present
        for feature in self.model_data['features']:
            if feature not in temp_df.columns:
                temp_df[feature] = 0

        # Make prediction
        prediction = int(
            self.model_data['model'].predict(
                temp_df[self.model_data['features']]
            )[0]
        )

        return {
            'gender': "Homme" if prediction == 1 else "Femme",
            'predicted_value': prediction,
            'surname': temp_df['surname'].iloc[0],
            'first_names': temp_df['first_names'].iloc[0],
            'main_first_name': temp_df['first_name'].iloc[0]
        }

    def train(
        self,
        dataset_path: str = None,
        save: bool = True
    ) -> Dict[str, Any]:
        """
        Train the gender classification model.

        Args:
            dataset_path: Path to training dataset CSV
            save: Whether to save the trained model

        Returns:
            Dictionary with training results
        """
        dataset_path = dataset_path or str(DATASET_PATH)

        # Load data
        data = pd.read_csv(dataset_path)
        print(f"Loaded {len(data)} samples from {dataset_path}")

        # Extract features
        data = self.feature_extractor.extract_features(data)

        # Prepare features and target
        X = data[FEATURE_NAMES]
        y = data['gender']

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=MODEL_CONFIG['test_size'],
            random_state=MODEL_CONFIG['random_state'],
            stratify=y
        )

        # Create and train ensemble model
        model = self._create_ensemble(X_train, y_train)
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred)

        print("Model Performance:")
        print(report)

        # Feature importance
        result = permutation_importance(model, X_test, y_test, n_repeats=10)
        importance_df = pd.DataFrame({
            'feature': FEATURE_NAMES,
            'importance': result.importances_mean
        }).sort_values('importance', ascending=False)

        # Save feature importance
        importance_df.to_csv(str(FEATURE_IMPORTANCE_PATH), index=False)
        print(f"Feature importance saved to {FEATURE_IMPORTANCE_PATH}")

        # Prepare model data
        self.model_data = {
            'model': model,
            'features': FEATURE_NAMES,
            'training_date': datetime.now().isoformat(),
            'data_size': len(data),
            'performance_report': report,
            'feature_importance': importance_df.to_dict(orient='records')
        }

        # Save model
        if save:
            joblib.dump(self.model_data, self.model_path)
            print(f"Model saved to {self.model_path}")

            # Save training report
            self._save_training_report(len(data), 0, report)

        return {
            'data_size': len(data),
            'report': report,
            'feature_importance': importance_df
        }

    def update_with_feedback(self) -> bool:
        """
        Update model with new feedback data.

        Returns:
            True if model was updated
        """
        print(f"\n{datetime.now()} - Starting automatic training update")

        # Get new feedback
        feedback_data = db.get_new_feedback()

        if feedback_data.empty:
            print("No new feedback - No update needed")
            return False

        print(f"{len(feedback_data)} new feedback entries to integrate")

        # Load original data
        original_data = pd.read_csv(str(DATASET_PATH))

        # Prepare feedback data
        feedback_data['gender'] = feedback_data['actual_gender']
        feedback_data = feedback_data[['full_name', 'gender']]

        # Combine with original data
        combined_data = pd.concat([original_data, feedback_data], ignore_index=True)
        combined_data = combined_data.drop_duplicates(subset=['full_name'])

        # Save updated dataset
        combined_data.to_csv(str(DATASET_PATH), index=False)
        print(f"Updated dataset saved with {len(combined_data)} entries")

        # Retrain model
        result = self.train(save=True)

        # Mark feedback as used
        feedback_ids = feedback_data.index.tolist()
        if feedback_ids:
            # Get actual IDs from database
            with db._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM feedback WHERE used_for_training = 0"
                )
                feedback_ids = [row[0] for row in cursor.fetchall()]

            if feedback_ids:
                db.mark_feedback_as_used(feedback_ids)

        print(f"Model updated with {len(feedback_data)} new examples")
        return True

    def _create_ensemble(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series
    ) -> VotingClassifier:
        """
        Create ensemble model with multiple classifiers.

        Args:
            X_train: Training features
            y_train: Training labels

        Returns:
            Voting classifier ensemble
        """
        # Calculate class ratio for XGBoost
        class_ratio = np.sum(y_train == 1) / np.sum(y_train == 0)

        # Model 1: XGBoost optimized for female recall
        xgb_fem = self._optimize_recall_female(X_train, y_train)

        # Model 2: Balanced Random Forest
        rf = RandomForestClassifier(
            n_estimators=MODEL_CONFIG['rf_n_estimators'],
            max_depth=MODEL_CONFIG['rf_max_depth'],
            min_samples_split=MODEL_CONFIG['rf_min_samples_split'],
            class_weight=MODEL_CONFIG['rf_class_weight'],
            random_state=MODEL_CONFIG['random_state']
        )

        # Model 3: Standard XGBoost
        xgb_std = XGBClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=6,
            scale_pos_weight=class_ratio,
            random_state=MODEL_CONFIG['random_state']
        )

        # Create voting ensemble
        return VotingClassifier(
            estimators=[
                ('xgb_fem', xgb_fem),
                ('rf', rf),
                ('xgb_std', xgb_std)
            ],
            voting='soft',
            weights=MODEL_CONFIG['ensemble_weights']
        )

    def _optimize_recall_female(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series
    ) -> XGBClassifier:
        """
        Optimize XGBoost specifically for female recall.

        Args:
            X_train: Training features
            y_train: Training labels

        Returns:
            Optimized XGBoost classifier
        """
        base_model = XGBClassifier(
            scale_pos_weight=MODEL_CONFIG['xgb_scale_pos_weight'],
            max_depth=MODEL_CONFIG['xgb_max_depth'],
            learning_rate=MODEL_CONFIG['xgb_learning_rate'],
            subsample=MODEL_CONFIG['xgb_subsample'],
            reg_alpha=MODEL_CONFIG['xgb_reg_alpha'],
            random_state=MODEL_CONFIG['random_state']
        )

        param_dist = {
            'scale_pos_weight': [1.5, 1.7, 2.0],
            'max_depth': [4, 5, 6],
            'learning_rate': [0.05, 0.1],
            'subsample': [0.7, 0.8],
            'reg_alpha': [0, 0.1],
            'reg_lambda': [1, 1.5]
        }

        # Focus on recall for class 0 (female)
        scorer = make_scorer(recall_score, pos_label=0)

        search = RandomizedSearchCV(
            base_model,
            param_distributions=param_dist,
            n_iter=30,
            scoring=scorer,
            cv=5,
            random_state=MODEL_CONFIG['random_state'],
            n_jobs=-1
        )

        search.fit(X_train, y_train)
        return search.best_estimator_

    def _save_training_report(
        self,
        data_size: int,
        new_feedback: int,
        report: str
    ) -> None:
        """
        Save training report to file.

        Args:
            data_size: Total dataset size
            new_feedback: Number of new feedback entries
            report: Classification report string
        """
        with open(str(TRAINING_REPORT_PATH), 'w') as f:
            f.write(f"Last update: {datetime.now()}\n")
            f.write(f"Dataset size: {data_size} entries\n")
            f.write(f"New feedback integrated: {new_feedback}\n\n")
            f.write(report)


def train_model() -> None:
    """Train the gender classification model."""
    classifier = GenderClassifier()
    classifier.train()


def update_model_with_feedback() -> None:
    """Update model with new feedback data."""
    classifier = GenderClassifier()
    classifier.update_with_feedback()
