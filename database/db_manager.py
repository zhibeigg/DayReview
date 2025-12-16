"""
数据库管理模块 - 使用 SQLite 存储活动数据
"""
import sqlite3
import os
from datetime import datetime, date
from typing import Optional
from contextlib import contextmanager

from ..config import DATABASE_PATH


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 活动记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    window_title TEXT,
                    process_name TEXT,
                    category TEXT,
                    start_time DATETIME,
                    end_time DATETIME,
                    duration_seconds INTEGER
                )
            """)

            # 活跃度记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_levels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    keyboard_count INTEGER,
                    mouse_count INTEGER
                )
            """)

            # 每日汇总表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE,
                    work_minutes INTEGER DEFAULT 0,
                    game_minutes INTEGER DEFAULT 0,
                    entertainment_minutes INTEGER DEFAULT 0,
                    social_minutes INTEGER DEFAULT 0,
                    browse_minutes INTEGER DEFAULT 0,
                    other_minutes INTEGER DEFAULT 0,
                    total_active_minutes INTEGER DEFAULT 0,
                    avg_activity_score REAL DEFAULT 0,
                    mood_score REAL,
                    stress_score REAL,
                    summary_text TEXT,
                    wechat_post TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activities_start_time
                ON activities(start_time)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activity_levels_timestamp
                ON activity_levels(timestamp)
            """)

    def insert_activity(
        self,
        window_title: str,
        process_name: str,
        category: str,
        start_time: datetime,
        end_time: datetime,
        duration_seconds: int
    ):
        """插入活动记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activities
                (window_title, process_name, category, start_time, end_time, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (window_title, process_name, category, start_time, end_time, duration_seconds))

    def insert_activity_level(
        self,
        timestamp: datetime,
        keyboard_count: int,
        mouse_count: int
    ):
        """插入活跃度记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activity_levels (timestamp, keyboard_count, mouse_count)
                VALUES (?, ?, ?)
            """, (timestamp, keyboard_count, mouse_count))

    def get_activities_by_date(self, target_date: date) -> list[dict]:
        """获取指定日期的所有活动"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM activities
                WHERE DATE(start_time) = ?
                ORDER BY start_time
            """, (target_date.isoformat(),))
            return [dict(row) for row in cursor.fetchall()]

    def get_activity_levels_by_date(self, target_date: date) -> list[dict]:
        """获取指定日期的活跃度数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM activity_levels
                WHERE DATE(timestamp) = ?
                ORDER BY timestamp
            """, (target_date.isoformat(),))
            return [dict(row) for row in cursor.fetchall()]

    def get_category_duration_by_date(self, target_date: date) -> dict[str, int]:
        """获取指定日期各分类的总时长（分钟）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT category, SUM(duration_seconds) / 60 as minutes
                FROM activities
                WHERE DATE(start_time) = ?
                GROUP BY category
            """, (target_date.isoformat(),))
            return {row["category"]: row["minutes"] for row in cursor.fetchall()}

    def get_top_activities_by_date(self, target_date: date, limit: int = 10) -> list[dict]:
        """获取指定日期使用时间最长的应用"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT process_name, category, SUM(duration_seconds) / 60 as minutes
                FROM activities
                WHERE DATE(start_time) = ?
                GROUP BY process_name
                ORDER BY minutes DESC
                LIMIT ?
            """, (target_date.isoformat(), limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_avg_activity_score_by_date(self, target_date: date) -> float:
        """获取指定日期的平均活跃度分数"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AVG(keyboard_count + mouse_count * 0.5) as avg_score
                FROM activity_levels
                WHERE DATE(timestamp) = ?
            """, (target_date.isoformat(),))
            result = cursor.fetchone()
            return result["avg_score"] if result and result["avg_score"] else 0

    def save_daily_summary(
        self,
        target_date: date,
        work_minutes: int,
        game_minutes: int,
        entertainment_minutes: int,
        social_minutes: int,
        browse_minutes: int,
        other_minutes: int,
        total_active_minutes: int,
        avg_activity_score: float,
        mood_score: float = None,
        stress_score: float = None,
        summary_text: str = None,
        wechat_post: str = None
    ):
        """保存每日汇总"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO daily_summary
                (date, work_minutes, game_minutes, entertainment_minutes,
                 social_minutes, browse_minutes, other_minutes, total_active_minutes,
                 avg_activity_score, mood_score, stress_score, summary_text, wechat_post)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (target_date.isoformat(), work_minutes, game_minutes, entertainment_minutes,
                  social_minutes, browse_minutes, other_minutes, total_active_minutes,
                  avg_activity_score, mood_score, stress_score, summary_text, wechat_post))

    def get_daily_summary(self, target_date: date) -> Optional[dict]:
        """获取每日汇总"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM daily_summary WHERE date = ?
            """, (target_date.isoformat(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_recent_summaries(self, days: int = 7) -> list[dict]:
        """获取最近几天的汇总"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM daily_summary
                ORDER BY date DESC
                LIMIT ?
            """, (days,))
            return [dict(row) for row in cursor.fetchall()]

    def cleanup_old_data(self, days_to_keep: int = 30):
        """清理旧数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 只保留活动详情30天，汇总数据永久保留
            cursor.execute("""
                DELETE FROM activities
                WHERE DATE(start_time) < DATE('now', ? || ' days')
            """, (f"-{days_to_keep}",))
            cursor.execute("""
                DELETE FROM activity_levels
                WHERE DATE(timestamp) < DATE('now', ? || ' days')
            """, (f"-{days_to_keep}",))
