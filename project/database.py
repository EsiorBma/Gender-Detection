import sqlite3
import pandas as pd
from datetime import datetime
import hashlib

class FeedbackDatabase:
    def __init__(self, db_path='./feedback.db.sqlite3'):
        self.db_path = db_path
        self.create_table()
        self.migrate_database()
    
    def get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)   
    
    def create_table(self):
        with self.get_conn() as conn:
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
    
    def save_prediction(self, full_name, surname, first_names, main_first_name, predicted_gender):
        with self.get_conn() as conn:    
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO feedback (full_name, surname, first_names, main_first_name, predicted_gender)
            VALUES (?, ?, ?, ?, ?)
            ''', (full_name, surname, str(first_names), main_first_name, predicted_gender))
            conn.commit()
            return cursor.lastrowid
    
    def update_feedback(self, feedback_id, actual_gender, is_correct):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE feedback 
            SET actual_gender = ?, is_correct = ?, timestamp = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (actual_gender, is_correct, feedback_id))
            conn.commit()
            
    def get_full_name(self, feedback_id):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT full_name FROM feedback WHERE id = ?', (feedback_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_new_feedback(self):
        with self.get_conn() as conn:
            # Vérifier si la colonne existe
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(feedback)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'used_for_training' in columns:
                query = "SELECT * FROM feedback WHERE actual_gender IS NOT NULL AND used_for_training = 0"
            else:
                # Fallback si la colonne n'existe pas encore
                query = "SELECT * FROM feedback WHERE actual_gender IS NOT NULL"
            
            return pd.read_sql_query(query, conn)
    
    def mark_feedback_as_used(self, feedback_ids):
        if not feedback_ids:
            return
        with self.get_conn() as conn:    
            cursor = conn.cursor()
            
            # Vérifier si la colonne existe
            cursor.execute("PRAGMA table_info(feedback)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'used_for_training' in columns:
                cursor.execute(f'''
                UPDATE feedback 
                SET used_for_training = 1
                WHERE id IN ({','.join(['?']*len(feedback_ids))})
                ''', feedback_ids)
                conn.commit()
    
    def get_feedback_stats(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            
            # Nombre total de feedbacks
            cursor.execute("SELECT COUNT(*) FROM feedback")
            total = cursor.fetchone()[0]
            
            # Feedback avec réponse
            cursor.execute("SELECT COUNT(*) FROM feedback WHERE actual_gender IS NOT NULL")
            with_feedback = cursor.fetchone()[0]
            
            # Précision globale
            cursor.execute("SELECT AVG(is_correct) FROM feedback WHERE is_correct IS NOT NULL")
            accuracy = cursor.fetchone()[0] or 0
            
            # Dernier feedback
            cursor.execute("SELECT MAX(timestamp) FROM feedback")
            last_feedback = cursor.fetchone()[0]
            
            return {
                'total': total,
                'with_feedback': with_feedback,
                'accuracy': round(accuracy * 100, 2),
                'last_feedback': last_feedback
            }
    def migrate_database(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            
            # Vérifier si la colonne existe
            cursor.execute("PRAGMA table_info(feedback)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'used_for_training' not in columns:
                print("Mise à jour de la structure de la base de données...")
                cursor.execute('''
                ALTER TABLE feedback 
                ADD COLUMN used_for_training BOOLEAN DEFAULT 0
                ''')
                conn.commit()
                print("Migration terminée.")
            
class UserDB:
    def __init__(self, db_path='./users.db.sqlite3'):
        self.db_path = db_path
        self.create_table()
    
    def get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def create_table(self):
        with self.get_conn() as conn:
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
    
    def create_user(self, email, password):
        password_hash = self._hash_password(password)
        with self.get_conn() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO users (email, password_hash)
                VALUES (?, ?)
                ''', (email, password_hash))
                conn.commit()
            except sqlite3.IntegrityError:
                # L'utilisateur existe déjà
                pass
    
    def authenticate(self, email, password):
        password_hash = self._hash_password(password)
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id FROM users 
            WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            return cursor.fetchone() is not None
    
    def _hash_password(self, password):
        """Hash le mot de passe avec SHA-256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Initialisation de la base
db = FeedbackDatabase()