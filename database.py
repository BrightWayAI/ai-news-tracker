"""
Database module for storing AI news articles
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os


class NewsDatabase:
    """Manages SQLite database for AI news articles"""

    def __init__(self, db_path: str = "ai_news.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                link TEXT UNIQUE NOT NULL,
                summary TEXT,
                published_date TEXT,
                scraped_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_source ON articles(source)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_published_date ON articles(published_date)
        ''')

        conn.commit()
        conn.close()

    def article_exists(self, link: str) -> bool:
        """Check if an article with given link already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM articles WHERE link = ?', (link,))
        count = cursor.fetchone()[0]

        conn.close()
        return count > 0

    def add_article(self, source: str, title: str, link: str,
                    summary: Optional[str], published_date: Optional[str]) -> bool:
        """
        Add a new article to the database
        Returns True if added, False if already exists
        """
        if self.article_exists(link):
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        scraped_date = datetime.now().isoformat()

        try:
            cursor.execute('''
                INSERT INTO articles (source, title, link, summary, published_date, scraped_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (source, title, link, summary, published_date, scraped_date))

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def get_recent_articles(self, days: int = 7) -> List[Dict]:
        """Get articles scraped in the last N days"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM articles
            WHERE scraped_date >= date('now', '-' || ? || ' days')
            ORDER BY published_date DESC, scraped_date DESC
        ''', (days,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_articles_by_source(self, source: str, days: int = 7) -> List[Dict]:
        """Get recent articles from a specific source"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM articles
            WHERE source = ? AND scraped_date >= date('now', '-' || ? || ' days')
            ORDER BY published_date DESC, scraped_date DESC
        ''', (source, days))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_all_articles(self) -> List[Dict]:
        """Get all articles from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM articles ORDER BY published_date DESC, scraped_date DESC')

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_stats(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM articles')
        total = cursor.fetchone()[0]

        cursor.execute('SELECT source, COUNT(*) as count FROM articles GROUP BY source')
        by_source = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        return {
            'total_articles': total,
            'by_source': by_source
        }
