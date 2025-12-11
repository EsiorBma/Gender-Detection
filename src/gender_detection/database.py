"""Database management module for feedback and user authentication."""

import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any
import pandas as pd

from .config import FEEDBACK_DB_PATH, USERS_DB_PATH


class FeedbackDatabase:
    """Manage feedback data for model improvement."""

    def __init__(self, db_path: str = None):
        """
        Initialize feedback database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or str(FEEDBACK_DB_PATH)
        self._create_table()
        self._migrate_database()

    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _create_table(self) -> None:
        """Create feedback table if it doesn't exist."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    surname TEXT,
                    first_names TEXT,
                    main_first_name TEXT,
                    predicted_gender INTEGER,
                    actual_gender INTEGER,
                    is_correct BOOLEAN,
                    used_for_training BOOLEAN DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def _migrate_database(self) -> None:
        """Add missing columns to existing database."""
        with self._get_conn() as conn:
            cursor = conn.cursor()

            # Check existing columns
            cursor.execute("PRAGMA table_info(feedback)")
            columns = [column[1] for column in cursor.fetchall()]

            # Add used_for_training column if missing
            if 'used_for_training' not in columns:
                print("Migrating database: adding used_for_training column...")
                cursor.execute('''
                    ALTER TABLE feedback 
                    ADD COLUMN used_for_training BOOLEAN DEFAULT 0
                ''')
                conn.commit()
                print("Migration completed.")

    def save_prediction(
        self,
        full_name: str,
        surname: str,
        first_names: str,
        main_first_name: str,
        predicted_gender: int
    ) -> int:
        """
        Save a prediction for later feedback.

        Args:
            full_name: Complete name
            surname: Family name
            first_names: List of first names as string
            main_first_name: Main first name
            predicted_gender: Predicted gender (0=Female, 1=Male)

        Returns:
            ID of saved prediction
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback (
                    full_name, surname, first_names, 
                    main_first_name, predicted_gender
                )
                VALUES (?, ?, ?, ?, ?)
            ''', (full_name, surname, str(first_names), main_first_name, predicted_gender))
            conn.commit()
            return cursor.lastrowid

    def update_feedback(
        self,
        feedback_id: int,
        actual_gender: int,
        is_correct: bool
    ) -> None:
        """
        Update feedback with actual gender.

        Args:
            feedback_id: ID of the prediction
            actual_gender: Actual gender (0=Female, 1=Male)
            is_correct: Whether prediction was correct
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE feedback 
                SET actual_gender = ?, is_correct = ?, timestamp = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (actual_gender, is_correct, feedback_id))
            conn.commit()

    def get_full_name(self, feedback_id: int) -> Optional[str]:
        """
        Get full name for a feedback entry.

        Args:
            feedback_id: ID of the feedback

        Returns:
            Full name or None if not found
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT full_name FROM feedback WHERE id = ?', (feedback_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_new_feedback(self) -> pd.DataFrame:
        """
        Get feedback entries not yet used for training.

        Returns:
            DataFrame with new feedback data
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(feedback)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'used_for_training' in columns:
                query = """
                    SELECT * FROM feedback 
                    WHERE actual_gender IS NOT NULL 
                    AND used_for_training = 0
                """
            else:
                query = """
                    SELECT * FROM feedback 
                    WHERE actual_gender IS NOT NULL
                """

            return pd.read_sql_query(query, conn)

    def mark_feedback_as_used(self, feedback_ids: List[int]) -> None:
        """
        Mark feedback entries as used for training.

        Args:
            feedback_ids: List of feedback IDs to mark
        """
        if not feedback_ids:
            return

        with self._get_conn() as conn:
            cursor = conn.cursor()

            # Check if column exists
            cursor.execute("PRAGMA table_info(feedback)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'used_for_training' in columns:
                placeholders = ','.join(['?'] * len(feedback_ids))
                cursor.execute(f'''
                    UPDATE feedback 
                    SET used_for_training = 1
                    WHERE id IN ({placeholders})
                ''', feedback_ids)
                conn.commit()

    def get_feedback_stats(self) -> Dict[str, Any]:
        """
        Get statistics about feedback data.

        Returns:
            Dictionary with statistics
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()

            # Total feedback count
            cursor.execute("SELECT COUNT(*) FROM feedback")
            total = cursor.fetchone()[0]

            # Feedback with actual gender
            cursor.execute(
                "SELECT COUNT(*) FROM feedback WHERE actual_gender IS NOT NULL"
            )
            with_feedback = cursor.fetchone()[0]

            # Accuracy
            cursor.execute(
                "SELECT AVG(is_correct) FROM feedback WHERE is_correct IS NOT NULL"
            )
            accuracy = cursor.fetchone()[0] or 0

            # Last feedback timestamp
            cursor.execute("SELECT MAX(timestamp) FROM feedback")
            last_feedback = cursor.fetchone()[0]

            return {
                'total': total,
                'with_feedback': with_feedback,
                'accuracy': round(accuracy * 100, 2),
                'last_feedback': last_feedback
            }


class UserDatabase:
    """Manage user authentication."""

    def __init__(self, db_path: str = None):
        """
        Initialize user database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or str(USERS_DB_PATH)
        self._create_table()

    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _create_table(self) -> None:
        """Create users table if it doesn't exist."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def create_user(self, email: str, password: str) -> bool:
        """
        Create a new user.

        Args:
            email: User email
            password: User password (will be hashed)

        Returns:
            True if user created, False if already exists
        """
        password_hash = self._hash_password(password)
        with self._get_conn() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (email, password_hash)
                    VALUES (?, ?)
                ''', (email, password_hash))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # User already exists
                return False

    def authenticate(self, email: str, password: str) -> bool:
        """
        Authenticate a user.

        Args:
            email: User email
            password: User password

        Returns:
            True if authentication successful
        """
        password_hash = self._hash_password(password)
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM users 
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            return cursor.fetchone() is not None

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hash password using SHA-256.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()


# Singleton instances
db = FeedbackDatabase()
user_db = UserDatabase()
