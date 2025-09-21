# models/database.py
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import uuid
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = 'social_media_automation.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with self.get_connection() as conn:
                # Posts table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS posts (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        category TEXT,
                        hashtags TEXT,
                        platforms TEXT,
                        files TEXT,
                        status TEXT DEFAULT 'draft',
                        schedule_time TEXT,
                        created_at TEXT,
                        updated_at TEXT,
                        results TEXT,
                        ai_content TEXT,
                        viral_score INTEGER DEFAULT 0
                    )
                ''')
                
                # Platform credentials table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS platform_credentials (
                        platform TEXT PRIMARY KEY,
                        credentials TEXT,
                        created_at TEXT,
                        updated_at TEXT,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # Analytics table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS analytics (
                        id TEXT PRIMARY KEY,
                        post_id TEXT,
                        platform TEXT,
                        metric_name TEXT,
                        metric_value INTEGER,
                        recorded_at TEXT,
                        FOREIGN KEY (post_id) REFERENCES posts (id)
                    )
                ''')
                
                # Scheduled jobs table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS scheduled_jobs (
                        id TEXT PRIMARY KEY,
                        post_id TEXT,
                        job_type TEXT,
                        schedule_time TEXT,
                        status TEXT DEFAULT 'pending',
                        created_at TEXT,
                        executed_at TEXT,
                        FOREIGN KEY (post_id) REFERENCES posts (id)
                    )
                ''')
                
                # User settings table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TEXT
                    )
                ''')
                
                # Templates table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS content_templates (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        category TEXT,
                        template_data TEXT,
                        created_at TEXT,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            conn.close()
    
    def generate_id(self) -> str:
        """Generate unique ID"""
        return str(uuid.uuid4())
    
    def save_post(self, post_data: Dict) -> bool:
        """Save post to database"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO posts 
                    (id, title, description, category, hashtags, platforms, files, 
                     status, schedule_time, created_at, updated_at, results, ai_content, viral_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_data['id'],
                    post_data['title'],
                    post_data.get('description', ''),
                    post_data.get('category', ''),
                    json.dumps(post_data.get('hashtags', [])),
                    json.dumps(post_data.get('platforms', [])),
                    json.dumps(post_data.get('files', [])),
                    post_data.get('status', 'draft'),
                    post_data.get('schedule_time'),
                    post_data.get('created_at', datetime.now().isoformat()),
                    datetime.now().isoformat(),
                    json.dumps(post_data.get('results', {})),
                    json.dumps(post_data.get('ai_content', {})),
                    post_data.get('viral_score', 0)
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save post: {e}")
            return False
    
    def get_post(self, post_id: str) -> Optional[Dict]:
        """Get post by ID"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(
                    'SELECT * FROM posts WHERE id = ?', (post_id,)
                ).fetchone()
                
                if result:
                    post = dict(result)
                    # Parse JSON fields
                    post['hashtags'] = json.loads(post['hashtags'] or '[]')
                    post['platforms'] = json.loads(post['platforms'] or '[]')
                    post['files'] = json.loads(post['files'] or '[]')
                    post['results'] = json.loads(post['results'] or '{}')
                    post['ai_content'] = json.loads(post['ai_content'] or '{}')
                    return post
                return None
        except Exception as e:
            logger.error(f"Failed to get post {post_id}: {e}")
            return None
    
    def get_posts(self, filters: Dict = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get posts with optional filtering"""
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM posts WHERE 1=1"
                params = []
                
                if filters:
                    if filters.get('status'):
                        query += " AND status = ?"
                        params.append(filters['status'])
                    
                    if filters.get('platform'):
                        query += " AND platforms LIKE ?"
                        params.append(f"%{filters['platform']}%")
                    
                    if filters.get('category'):
                        query += " AND category = ?"
                        params.append(filters['category'])
                
                query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                results = conn.execute(query, params).fetchall()
                
                posts = []
                for result in results:
                    post = dict(result)
                    # Parse JSON fields
                    post['hashtags'] = json.loads(post['hashtags'] or '[]')
                    post['platforms'] = json.loads(post['platforms'] or '[]')
                    post['files'] = json.loads(post['files'] or '[]')
                    post['results'] = json.loads(post['results'] or '{}')
                    post['ai_content'] = json.loads(post['ai_content'] or '{}')
                    posts.append(post)
                
                return posts
                
        except Exception as e:
            logger.error(f"Failed to get posts: {e}")
            return []
    
    def update_post(self, post_id: str, updates: Dict) -> bool:
        """Update post with new data"""
        try:
            with self.get_connection() as conn:
                set_clause = []
                values = []
                
                for key, value in updates.items():
                    if key in ['hashtags', 'platforms', 'files', 'results', 'ai_content']:
                        value = json.dumps(value)
                    set_clause.append(f"{key} = ?")
                    values.append(value)
                
                set_clause.append("updated_at = ?")
                values.append(datetime.now().isoformat())
                values.append(post_id)
                
                query = f"UPDATE posts SET {', '.join(set_clause)} WHERE id = ?"
                cursor = conn.execute(query, values)  # Store cursor
                conn.commit()
                return cursor.rowcount > 0  # Use cursor.rowcount
                
        except Exception as e:
            logger.error(f"Failed to update post {post_id}: {e}")
            return False
    
    def delete_post(self, post_id: str) -> bool:
        """Delete post"""
        try:
            with self.get_connection() as conn:
                # Delete related records first
                conn.execute('DELETE FROM analytics WHERE post_id = ?', (post_id,))
                conn.execute('DELETE FROM scheduled_jobs WHERE post_id = ?', (post_id,))
                
                # Delete the post
                cursor = conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to delete post {post_id}: {e}")
            return False
    
    def get_scheduled_posts(self, filters: Dict = None) -> List[Dict]:
        """Get scheduled posts with optional filtering"""
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM posts WHERE status = 'scheduled'"
                params = []
                
                if filters:
                    if filters.get('platform'):
                        query += " AND platforms LIKE ?"
                        params.append(f"%{filters['platform']}%")
                    
                    if filters.get('date'):
                        query += " AND DATE(schedule_time) = ?"
                        params.append(filters['date'])
                
                query += " ORDER BY schedule_time ASC"
                
                results = conn.execute(query, params).fetchall()
                
                posts = []
                for result in results:
                    post = dict(result)
                    post['hashtags'] = json.loads(post['hashtags'] or '[]')
                    post['platforms'] = json.loads(post['platforms'] or '[]')
                    post['files'] = json.loads(post['files'] or '[]')
                    posts.append(post)
                
                return posts
                
        except Exception as e:
            logger.error(f"Failed to get scheduled posts: {e}")
            return []
    
    def save_platform_credentials(self, platform: str, credentials: Dict) -> bool:
        """Save encrypted platform credentials"""
        try:
            with self.get_connection() as conn:
                # In production, encrypt credentials before storing
                conn.execute('''
                    INSERT OR REPLACE INTO platform_credentials 
                    (platform, credentials, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    platform,
                    json.dumps(credentials),  # Encrypt this in production
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save credentials for {platform}: {e}")
            return False
    
    def get_platform_credentials(self, platform: str) -> Optional[Dict]:
        """Get platform credentials"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(
                    'SELECT credentials FROM platform_credentials WHERE platform = ? AND is_active = 1',
                    (platform,)
                ).fetchone()
                
                if result:
                    return json.loads(result['credentials'])
                return None
        except Exception as e:
            logger.error(f"Failed to get credentials for {platform}: {e}")
            return None
    
    def save_analytics(self, post_id: str, platform: str, metrics: Dict) -> bool:
        """Save analytics data"""
        try:
            with self.get_connection() as conn:
                for metric_name, metric_value in metrics.items():
                    conn.execute('''
                        INSERT INTO analytics (id, post_id, platform, metric_name, metric_value, recorded_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        self.generate_id(),
                        post_id,
                        platform,
                        metric_name,
                        int(metric_value) if isinstance(metric_value, (int, float)) else 0,
                        datetime.now().isoformat()
                    ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save analytics: {e}")
            return False
    
    def get_analytics_summary(self, days: int = 30) -> Dict:
        """Get analytics summary for the last N days"""
        try:
            with self.get_connection() as conn:
                # Get date threshold
                from datetime import timedelta
                threshold = (datetime.now() - timedelta(days=days)).isoformat()
                
                # Get total metrics
                result = conn.execute('''
                    SELECT 
                        metric_name,
                        SUM(metric_value) as total_value
                    FROM analytics 
                    WHERE recorded_at >= ?
                    GROUP BY metric_name
                ''', (threshold,)).fetchall()
                
                summary = {}
                for row in result:
                    summary[row['metric_name']] = row['total_value']
                
                # Get post count
                post_count_result = conn.execute('''
                    SELECT COUNT(DISTINCT post_id) as count
                    FROM analytics 
                    WHERE recorded_at >= ?
                ''', (threshold,)).fetchone()
                
                summary['total_posts'] = post_count_result['count'] if post_count_result else 0
                
                return summary
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {}
    
    def save_scheduled_job(self, job_data: Dict) -> bool:
        """Save scheduled job"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO scheduled_jobs 
                    (id, post_id, job_type, schedule_time, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    job_data.get('id', self.generate_id()),
                    job_data['post_id'],
                    job_data.get('job_type', 'post'),
                    job_data['schedule_time'],
                    job_data.get('status', 'pending'),
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save scheduled job: {e}")
            return False
    
    def update_scheduled_job(self, job_id: str, updates: Dict) -> bool:
        """Update scheduled job"""
        try:
            with self.get_connection() as conn:
                set_clause = []
                values = []
                
                for key, value in updates.items():
                    set_clause.append(f"{key} = ?")
                    values.append(value)
                
                values.append(job_id)
                query = f"UPDATE scheduled_jobs SET {', '.join(set_clause)} WHERE id = ?"
                
                cursor = conn.execute(query, values)
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to update scheduled job {job_id}: {e}")
            return False
    
    def save_user_setting(self, key: str, value: str) -> bool:
        """Save user setting"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO user_settings (key, value, updated_at)
                    VALUES (?, ?, ?)
                ''', (key, value, datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save user setting {key}: {e}")
            return False
    
    def get_user_setting(self, key: str, default=None):
        """Get user setting"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(
                    'SELECT value FROM user_settings WHERE key = ?', (key,)
                ).fetchone()
                
                return result['value'] if result else default
        except Exception as e:
            logger.error(f"Failed to get user setting {key}: {e}")
            return default
    
    def save_template(self, template_data: Dict) -> bool:
        """Save content template"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO content_templates 
                    (id, name, category, template_data, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    template_data.get('id', self.generate_id()),
                    template_data['name'],
                    template_data.get('category', 'general'),
                    json.dumps(template_data),
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False
    
    def get_templates(self, category: str = None) -> List[Dict]:
        """Get content templates"""
        try:
            with self.get_connection() as conn:
                if category:
                    results = conn.execute(
                        'SELECT * FROM content_templates WHERE category = ? AND is_active = 1',
                        (category,)
                    ).fetchall()
                else:
                    results = conn.execute(
                        'SELECT * FROM content_templates WHERE is_active = 1'
                    ).fetchall()
                
                templates = []
                for result in results:
                    template = dict(result)
                    template['template_data'] = json.loads(template['template_data'] or '{}')
                    templates.append(template)
                
                return templates
        except Exception as e:
            logger.error(f"Failed to get templates: {e}")
            return []
    
    def is_healthy(self) -> bool:
        """Check database health"""
        try:
            with self.get_connection() as conn:
                conn.execute('SELECT 1').fetchone()
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                stats = {}
                
                # Count records in each table
                tables = ['posts', 'platform_credentials', 'analytics', 'scheduled_jobs', 'user_settings', 'content_templates']
                for table in tables:
                    result = conn.execute(f'SELECT COUNT(*) as count FROM {table}').fetchone()
                    stats[table] = result['count'] if result else 0
                
                # Database file size
                if os.path.exists(self.db_path):
                    stats['file_size_bytes'] = os.path.getsize(self.db_path)
                    stats['file_size_mb'] = stats['file_size_bytes'] / (1024 * 1024)
                
                return stats
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 90) -> bool:
        """Clean up old analytics and job data"""
        try:
            with self.get_connection() as conn:
                from datetime import timedelta
                threshold = (datetime.now() - timedelta(days=days)).isoformat()
                
                # Clean old analytics
                conn.execute('DELETE FROM analytics WHERE recorded_at < ?', (threshold,))
                
                # Clean completed jobs
                conn.execute('DELETE FROM scheduled_jobs WHERE status = "completed" AND executed_at < ?', (threshold,))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return False