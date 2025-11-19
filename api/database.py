"""
Multi-User Database Manager
Enhanced SQLite database with user authentication and multi-user support
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json

# Database path
DB_DIR = Path(__file__).parent.parent / "app" / "db"
DB_PATH = DB_DIR / "wellness_multiuser.db"


class DatabaseManager:
    """Multi-user SQLite database manager"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        self.db_path = db_path or str(DB_PATH)
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Create database directory if it doesn't exist"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                created_at TEXT NOT NULL,
                last_login TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Health entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                sleepHours REAL,
                calories REAL,
                steps INTEGER,
                waterIntake REAL,
                screenTime REAL,
                stressLevel INTEGER,
                wellnessScore REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, date)
            )
        ''')
        
        # Device sync log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                device_type TEXT NOT NULL,
                sync_date TEXT NOT NULL,
                synced_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_user_date ON health_entries(user_id, date DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_device_user ON device_sync_log(user_id)')
        
        conn.commit()
        conn.close()
        print(f"✓ Multi-user database initialized: {self.db_path}")
        
        # Create default admin account if it doesn't exist
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin account"""
        try:
            from .auth import AuthManager
            auth = AuthManager()
            
            admin_email = "admin@wellness.com"
            admin_password = "admin"
            
            # Check if admin exists
            if not self.get_user_by_email(admin_email):
                conn = self._get_connection()
                cursor = conn.cursor()
                
                password_hash = auth.hash_password(admin_password)
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO users (email, password_hash, full_name, is_admin, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (admin_email, password_hash, "System Administrator", 1, now))
                
                conn.commit()
                conn.close()
                print(f"✓ Created default admin account: {admin_email} / {admin_password}")
        except Exception as e:
            print(f"Note: Admin account may already exist or error occurred: {e}")
    
    # User Management
    def create_user(self, email: str, password_hash: str, full_name: str, is_admin: bool = False) -> int:
        """Create new user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, is_admin, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, password_hash, full_name, 1 if is_admin else 0, now))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return user_id
        
        except sqlite3.IntegrityError:
            raise ValueError("Email already exists")
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
        
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
        
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_last_login(self, user_id: int):
        """Update user's last login time"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE id = ?
            ''', (datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating last login: {e}")
    
    # Health Entry Management
    def add_health_entry(self, user_id: int, date: str, sleep_hours: float,
                        calories: float, steps: int, water_intake: float,
                        screen_time: float, stress_level: int, wellness_score: float) -> bool:
        """Add or update health entry for user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # Check if entry exists
            cursor.execute('''
                SELECT id FROM health_entries WHERE user_id = ? AND date = ?
            ''', (user_id, date))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update
                cursor.execute('''
                    UPDATE health_entries
                    SET sleepHours = ?, calories = ?, steps = ?, waterIntake = ?,
                        screenTime = ?, stressLevel = ?, wellnessScore = ?, updated_at = ?
                    WHERE user_id = ? AND date = ?
                ''', (sleep_hours, calories, steps, water_intake, screen_time,
                      stress_level, wellness_score, now, user_id, date))
            else:
                # Insert
                cursor.execute('''
                    INSERT INTO health_entries
                    (user_id, date, sleepHours, calories, steps, waterIntake,
                     screenTime, stressLevel, wellnessScore, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, date, sleep_hours, calories, steps, water_intake,
                      screen_time, stress_level, wellness_score, now, now))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"Error adding health entry: {e}")
            return False
    
    def get_user_health_history(self, user_id: int, days: int = 30) -> List[Dict]:
        """Get health history for user"""
        try:
            conn = self._get_connection()
            
            end = datetime.now()
            start = end - timedelta(days=days)
            
            query = '''
                SELECT * FROM health_entries
                WHERE user_id = ? AND date >= ?
                ORDER BY date DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id, start.strftime('%Y-%m-%d')))
            conn.close()
            
            return df.to_dict('records')
        
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    def get_latest_entry(self, user_id: int) -> Optional[Dict]:
        """Get latest health entry for user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM health_entries
                WHERE user_id = ?
                ORDER BY date DESC
                LIMIT 1
            ''', (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
        
        except Exception as e:
            print(f"Error getting latest entry: {e}")
            return None
    
    def delete_health_entry(self, user_id: int, date: str) -> bool:
        """Delete health entry for user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM health_entries
                WHERE user_id = ? AND date = ?
            ''', (user_id, date))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return deleted
        
        except Exception as e:
            print(f"Error deleting entry: {e}")
            return False
    
    def get_user_statistics(self, user_id: int, days: int = 30) -> Dict:
        """Get statistics for user"""
        try:
            entries = self.get_user_health_history(user_id, days)
            
            if not entries:
                return {}
            
            df = pd.DataFrame(entries)
            
            stats = {
                'total_entries': len(df),
                'date_range': {
                    'start': df['date'].min(),
                    'end': df['date'].max()
                },
                'averages': {
                    'sleepHours': float(df['sleepHours'].mean()) if 'sleepHours' in df else None,
                    'calories': float(df['calories'].mean()) if 'calories' in df else None,
                    'steps': int(df['steps'].mean()) if 'steps' in df else None,
                    'waterIntake': float(df['waterIntake'].mean()) if 'waterIntake' in df else None,
                    'screenTime': float(df['screenTime'].mean()) if 'screenTime' in df else None,
                    'stressLevel': float(df['stressLevel'].mean()) if 'stressLevel' in df else None,
                    'wellnessScore': float(df['wellnessScore'].mean()) if 'wellnessScore' in df else None,
                }
            }
            
            return stats
        
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {}
    
    # Device Sync Logging
    def log_device_sync(self, user_id: int, device_type: str, sync_date: str):
        """Log fitness device sync"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO device_sync_log (user_id, device_type, sync_date, synced_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, device_type, sync_date, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging device sync: {e}")
    
    def get_user_device_syncs(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent device syncs for user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM device_sync_log
                WHERE user_id = ?
                ORDER BY synced_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting device syncs: {e}")
            return []


if __name__ == "__main__":
    # Test the database
    print("Testing Multi-User Database...\n")
    
    db = DatabaseManager()
    
    # Test would go here (skipped for brevity)
    print("✓ Database manager initialized")
