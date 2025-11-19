"""
Database Utilities for User Health Data
SQLite database for storing and retrieving daily wellness entries
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json


# Database path
DB_DIR = Path(__file__).parent.parent / "db"
DB_PATH = DB_DIR / "wellness.db"


class WellnessDatabase:
    """SQLite database manager for wellness data"""
    
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
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def _init_database(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create wellness entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wellness_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                sleepHours REAL,
                calories REAL,
                steps INTEGER,
                waterIntake REAL,
                screenTime REAL,
                stressLevel INTEGER,
                wellnessScore REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Create index on date for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_date 
            ON wellness_entries(date DESC)
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Database initialized: {self.db_path}")
    
    def add_entry(self, data: Dict) -> bool:
        """
        Add or update a wellness entry
        
        Args:
            data: Dictionary with wellness metrics
                Required: date (YYYY-MM-DD format)
                Optional: sleepHours, calories, steps, waterIntake, 
                         screenTime, stressLevel, wellnessScore
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate date
            entry_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
            
            # Prepare data
            now = datetime.now().isoformat()
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if entry exists
            cursor.execute('SELECT id FROM wellness_entries WHERE date = ?', (entry_date,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing entry
                cursor.execute('''
                    UPDATE wellness_entries
                    SET sleepHours = ?,
                        calories = ?,
                        steps = ?,
                        waterIntake = ?,
                        screenTime = ?,
                        stressLevel = ?,
                        wellnessScore = ?,
                        updated_at = ?
                    WHERE date = ?
                ''', (
                    data.get('sleepHours'),
                    data.get('calories'),
                    data.get('steps'),
                    data.get('waterIntake'),
                    data.get('screenTime'),
                    data.get('stressLevel'),
                    data.get('wellnessScore'),
                    now,
                    entry_date
                ))
            else:
                # Insert new entry
                cursor.execute('''
                    INSERT INTO wellness_entries 
                    (date, sleepHours, calories, steps, waterIntake, screenTime, 
                     stressLevel, wellnessScore, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry_date,
                    data.get('sleepHours'),
                    data.get('calories'),
                    data.get('steps'),
                    data.get('waterIntake'),
                    data.get('screenTime'),
                    data.get('stressLevel'),
                    data.get('wellnessScore'),
                    now,
                    now
                ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"✗ Error adding entry: {e}")
            return False
    
    def get_latest(self, n: int = 1) -> Optional[Dict]:
        """
        Get the most recent wellness entry/entries
        
        Args:
            n: Number of recent entries to retrieve
        
        Returns:
            Dictionary (if n=1) or list of dictionaries with wellness data
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM wellness_entries 
                ORDER BY date DESC 
                LIMIT ?
            ''', (n,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return None
            
            entries = [dict(row) for row in rows]
            
            return entries[0] if n == 1 else entries
            
        except Exception as e:
            print(f"✗ Error getting latest entry: {e}")
            return None
    
    def get_history(self, days: int = 30, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get wellness history
        
        Args:
            days: Number of days to retrieve (if start_date/end_date not specified)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with wellness history
        """
        try:
            conn = self._get_connection()
            
            if start_date and end_date:
                query = '''
                    SELECT * FROM wellness_entries 
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date DESC
                '''
                df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            else:
                end = datetime.now()
                start = end - timedelta(days=days)
                query = '''
                    SELECT * FROM wellness_entries 
                    WHERE date >= ?
                    ORDER BY date DESC
                '''
                df = pd.read_sql_query(query, conn, params=(start.strftime('%Y-%m-%d'),))
            
            conn.close()
            return df
            
        except Exception as e:
            print(f"✗ Error getting history: {e}")
            return pd.DataFrame()
    
    def get_entry_by_date(self, date: str) -> Optional[Dict]:
        """
        Get wellness entry for a specific date
        
        Args:
            date: Date in YYYY-MM-DD format
        
        Returns:
            Dictionary with wellness data or None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM wellness_entries WHERE date = ?', (date,))
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
            
        except Exception as e:
            print(f"✗ Error getting entry: {e}")
            return None
    
    def delete_entry(self, date: str) -> bool:
        """
        Delete a wellness entry
        
        Args:
            date: Date in YYYY-MM-DD format
        
        Returns:
            True if successful
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM wellness_entries WHERE date = ?', (date,))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            
            return deleted
            
        except Exception as e:
            print(f"✗ Error deleting entry: {e}")
            return False
    
    def get_statistics(self, days: int = 30) -> Dict:
        """
        Get wellness statistics for specified period
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with statistics
        """
        try:
            df = self.get_history(days=days)
            
            if df.empty:
                return {}
            
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
                },
                'trends': self._calculate_trends(df)
            }
            
            return stats
            
        except Exception as e:
            print(f"✗ Error calculating statistics: {e}")
            return {}
    
    def _calculate_trends(self, df: pd.DataFrame) -> Dict:
        """Calculate trends from historical data"""
        if len(df) < 2:
            return {}
        
        # Sort by date
        df_sorted = df.sort_values('date')
        
        trends = {}
        numeric_cols = ['sleepHours', 'calories', 'steps', 'waterIntake', 
                       'screenTime', 'stressLevel', 'wellnessScore']
        
        for col in numeric_cols:
            if col in df_sorted.columns:
                recent_avg = df_sorted[col].tail(7).mean()
                older_avg = df_sorted[col].head(7).mean()
                
                if older_avg != 0:
                    change_pct = ((recent_avg - older_avg) / older_avg) * 100
                    trends[col] = {
                        'direction': 'up' if change_pct > 0 else 'down' if change_pct < 0 else 'stable',
                        'change_percent': float(change_pct)
                    }
        
        return trends
    
    def fetch_for_dashboard(self) -> Dict:
        """
        Fetch data optimized for dashboard display
        
        Returns:
            Dictionary with current entry, history, and statistics
        """
        return {
            'latest': self.get_latest(),
            'history_7d': self.get_history(days=7).to_dict('records'),
            'history_30d': self.get_history(days=30).to_dict('records'),
            'stats_7d': self.get_statistics(days=7),
            'stats_30d': self.get_statistics(days=30)
        }
    
    def export_to_csv(self, filepath: str, days: int = None):
        """
        Export wellness data to CSV
        
        Args:
            filepath: Path to save CSV file
            days: Number of days to export (None = all data)
        """
        try:
            if days:
                df = self.get_history(days=days)
            else:
                conn = self._get_connection()
                df = pd.read_sql_query('SELECT * FROM wellness_entries ORDER BY date DESC', conn)
                conn.close()
            
            df.to_csv(filepath, index=False)
            print(f"✓ Data exported to: {filepath}")
            return True
            
        except Exception as e:
            print(f"✗ Export failed: {e}")
            return False
    
    def get_total_entries(self) -> int:
        """Get total number of entries in database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM wellness_entries')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0


# Global database instance
_db = None


def get_db() -> WellnessDatabase:
    """Get or create global database instance"""
    global _db
    if _db is None:
        _db = WellnessDatabase()
    return _db


# Convenient wrapper functions
def add_entry(data: Dict) -> bool:
    """Add wellness entry"""
    return get_db().add_entry(data)


def get_latest(n: int = 1) -> Optional[Dict]:
    """Get latest entry"""
    return get_db().get_latest(n)


def get_history(days: int = 30) -> pd.DataFrame:
    """Get history"""
    return get_db().get_history(days)


def delete_entry(date: str) -> bool:
    """Delete entry"""
    return get_db().delete_entry(date)


def fetch_for_dashboard() -> Dict:
    """Fetch dashboard data"""
    return get_db().fetch_for_dashboard()


if __name__ == "__main__":
    # Test the database
    print("Testing Wellness Database...\n")
    
    db = WellnessDatabase()
    
    # Add sample entries
    print("📝 Adding sample entries...")
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        sample_data = {
            'date': date,
            'sleepHours': 7 + (i % 3) * 0.5,
            'calories': 2000 + i * 100,
            'steps': 8000 + i * 500,
            'waterIntake': 2.0 + (i % 4) * 0.3,
            'screenTime': 3 + (i % 3),
            'stressLevel': 3 + (i % 5),
            'wellnessScore': 70 + i * 2
        }
        add_entry(sample_data)
    
    print(f"✓ Added sample entries\n")
    
    # Test retrieval
    print("📊 Latest entry:")
    latest = get_latest()
    if latest:
        print(f"  Date: {latest['date']}")
        print(f"  Wellness Score: {latest['wellnessScore']}")
    
    print(f"\n📈 History (last 7 days):")
    history = get_history(7)
    print(f"  Entries: {len(history)}")
    
    print(f"\n📊 Statistics:")
    stats = db.get_statistics(7)
    if 'averages' in stats:
        print(f"  Avg Sleep: {stats['averages'].get('sleepHours', 0):.1f} hours")
        print(f"  Avg Steps: {stats['averages'].get('steps', 0):.0f}")
        print(f"  Avg Wellness: {stats['averages'].get('wellnessScore', 0):.1f}")
    
    print(f"\n✅ Database test complete!")
