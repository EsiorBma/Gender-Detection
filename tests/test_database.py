"""Unit tests for database module."""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path

from gender_detection.database import FeedbackDatabase, UserDatabase


class TestFeedbackDatabase:
    """Test suite for FeedbackDatabase class."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        db = FeedbackDatabase(db_path=path)
        yield db
        os.unlink(path)

    def test_create_table(self, temp_db):
        """Test table creation."""
        with temp_db._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'"
            )
            assert cursor.fetchone() is not None

    def test_save_prediction(self, temp_db):
        """Test saving a prediction."""
        feedback_id = temp_db.save_prediction(
            full_name='AMEGANVI Koffi Ama',
            surname='AMEGANVI',
            first_names="['KOFFI', 'AMA']",
            main_first_name='AMA',
            predicted_gender=0
        )
        
        assert feedback_id > 0
        assert temp_db.get_full_name(feedback_id) == 'AMEGANVI Koffi Ama'

    def test_update_feedback(self, temp_db):
        """Test updating feedback with actual gender."""
        feedback_id = temp_db.save_prediction(
            full_name='TEST Name',
            surname='TEST',
            first_names="['Name']",
            main_first_name='Name',
            predicted_gender=1
        )
        
        temp_db.update_feedback(feedback_id, actual_gender=0, is_correct=0)
        
        with temp_db._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT actual_gender, is_correct FROM feedback WHERE id = ?', (feedback_id,))
            result = cursor.fetchone()
            
            assert result[0] == 0  # actual_gender
            assert result[1] == 0  # is_correct

    def test_get_new_feedback(self, temp_db):
        """Test retrieving new feedback."""
        # Add some feedback
        id1 = temp_db.save_prediction('Name1 First1', 'Name1', "['First1']", 'First1', 1)
        id2 = temp_db.save_prediction('Name2 First2', 'Name2', "['First2']", 'First2', 0)
        
        # Update with actual gender
        temp_db.update_feedback(id1, 1, 1)
        temp_db.update_feedback(id2, 1, 0)
        
        # Get new feedback
        new_feedback = temp_db.get_new_feedback()
        
        assert len(new_feedback) == 2
        assert 'actual_gender' in new_feedback.columns

    def test_mark_feedback_as_used(self, temp_db):
        """Test marking feedback as used."""
        id1 = temp_db.save_prediction('Name1 First1', 'Name1', "['First1']", 'First1', 1)
        temp_db.update_feedback(id1, 1, 1)
        
        temp_db.mark_feedback_as_used([id1])
        
        new_feedback = temp_db.get_new_feedback()
        assert len(new_feedback) == 0

    def test_get_feedback_stats(self, temp_db):
        """Test getting feedback statistics."""
        # Add some feedback
        id1 = temp_db.save_prediction('Name1 First1', 'Name1', "['First1']", 'First1', 1)
        id2 = temp_db.save_prediction('Name2 First2', 'Name2', "['First2']", 'First2', 0)
        
        temp_db.update_feedback(id1, 1, 1)  # Correct
        temp_db.update_feedback(id2, 1, 0)  # Incorrect
        
        stats = temp_db.get_feedback_stats()
        
        assert stats['total'] == 2
        assert stats['with_feedback'] == 2
        assert stats['accuracy'] == 50.0


class TestUserDatabase:
    """Test suite for UserDatabase class."""

    @pytest.fixture
    def temp_user_db(self):
        """Create temporary user database for testing."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        db = UserDatabase(db_path=path)
        yield db
        os.unlink(path)

    def test_create_table(self, temp_user_db):
        """Test users table creation."""
        with temp_user_db._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            )
            assert cursor.fetchone() is not None

    def test_create_user(self, temp_user_db):
        """Test user creation."""
        result = temp_user_db.create_user('test@example.com', 'password123')
        assert result is True
        
        # Try creating same user again
        result = temp_user_db.create_user('test@example.com', 'password456')
        assert result is False

    def test_authenticate(self, temp_user_db):
        """Test user authentication."""
        temp_user_db.create_user('test@example.com', 'password123')
        
        # Correct credentials
        assert temp_user_db.authenticate('test@example.com', 'password123') is True
        
        # Wrong password
        assert temp_user_db.authenticate('test@example.com', 'wrongpass') is False
        
        # Non-existent user
        assert temp_user_db.authenticate('nonexistent@example.com', 'password') is False

    def test_password_hashing(self, temp_user_db):
        """Test that passwords are hashed."""
        temp_user_db.create_user('test@example.com', 'password123')
        
        with temp_user_db._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password_hash FROM users WHERE email = ?', ('test@example.com',))
            password_hash = cursor.fetchone()[0]
            
            # Hash should not be plain text
            assert password_hash != 'password123'
            assert len(password_hash) == 64  # SHA-256 produces 64 hex characters
