"""
DayReview - 一天回顾 | 每日活动分析与朋友圈文案生成
"""
import sys
import os
import time
import threading
import signal
from datetime import datetime, date, timedelta

import schedule

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DayReview.config import (
    WINDOW_CHECK_INTERVAL, INPUT_STATS_INTERVAL,
    MIN_ACTIVITY_DURATION, DAILY_ANALYSIS_TIME
)
from DayReview.monitors import WindowMonitor, InputMonitor
from DayReview.analyzers import Categorizer, AIAnalyzer
from DayReview.database import DatabaseManager
from DayReview.notifier import Notifier
from DayReview.notifier.notification import show_daily_report_notification


class ActivityMonitorApp:
    """活动监控应用主类"""

    def __init__(self):
        """初始化应用"""
        self.db = DatabaseManager()
        self.categorizer = Categorizer()
        self.ai_analyzer = AIAnalyzer()
        self.notifier = Notifier()

        # 初始化监控器
        self.window_monitor = WindowMonitor(
            check_interval=WINDOW_CHECK_INTERVAL,
            min_duration=MIN_ACTIVITY_DURATION,
            on_window_change=self._on_window_change
        )

        self.input_monitor = InputMonitor(
            stats_interval=INPUT_STATS_INTERVAL,
            on_stats_ready=self._on_input_stats
        )

        self._running = False
        self._scheduler_thread = None

    def _on_window_change(self, activity: dict):
        """窗口切换回调"""
        try:
            # 获取分类
            category = self.categorizer.categorize(
                activity["process_name"],
                activity["window_title"]
            )

            # 保存到数据库
            self.db.insert_activity(
                window_title=activity["window_title"][:200],  # 限制长度
                process_name=activity["process_name"],
                category=category,
                start_time=activity["start_time"],
                end_time=activity["end_time"],
                duration_seconds=activity["duration_seconds"]
            )
        except Exception as e:
            print(f"记录活动失败: {e}")

    def _on_input_stats(self, stats: dict):
        """键鼠统计回调"""
        try:
            self.db.insert_activity_level(
                timestamp=stats["timestamp"],
                keyboard_count=stats["keyboard_count"],
                mouse_count=stats["mouse_count"]
            )
        except Exception as e:
            print(f"记录活跃度失败: {e}")

    def start(self):
        """启动监控"""
        if self._running:
            return

        self._running = True
        print("🚀 DayReview 已启动")

        # 启动监控器
        self.window_monitor.start()
        self.input_monitor.start()
        print("  ✓ 窗口监控已启动")
        print("  ✓ 键鼠监控已启动")

        # 设置定时任务
        self._setup_scheduler()
        print(f"  ✓ 定时任务已设置 (每日 {DAILY_ANALYSIS_TIME} 生成报告)")

        # 启动调度器线程
        self._scheduler_thread = threading.Thread(
            target=self._run_scheduler,
            daemon=True
        )
        self._scheduler_thread.start()

    def stop(self):
        """停止监控"""
        if not self._running:
            return

        self._running = False

        # 停止监控器
        self.window_monitor.stop()
        self.input_monitor.stop()

        print("\n🛑 DayReview 已停止")

    def _setup_scheduler(self):
        """设置定时任务"""
        # 每日0点生成报告
        schedule.every().day.at(DAILY_ANALYSIS_TIME).do(self.generate_daily_report)

        # 每周清理旧数据
        schedule.every().sunday.at("03:00").do(self._cleanup_old_data)

    def _run_scheduler(self):
        """运行调度器"""
        while self._running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

    def _cleanup_old_data(self):
        """清理旧数据"""
        try:
            self.db.cleanup_old_data(days_to_keep=30)
            print("✓ 已清理30天前的详细数据")
        except Exception as e:
            print(f"清理数据失败: {e}")

    def generate_daily_report(self, target_date: date = None):
        """
        生成每日报告

        Args:
            target_date: 目标日期，默认为昨天
        """
        try:
            # 默认分析昨天的数据（因为是0点触发）
            if target_date is None:
                target_date = (datetime.now() - timedelta(days=1)).date()

            print(f"\n📊 正在生成 {target_date} 的每日报告...")

            # 获取分类时长
            category_minutes = self.db.get_category_duration_by_date(target_date)

            if not category_minutes:
                print("  ⚠️ 当日无活动数据")
                return

            # 获取活跃度
            avg_activity = self.db.get_avg_activity_score_by_date(target_date)

            # 生产力分析
            productivity = self.categorizer.analyze_productivity(category_minutes)

            # 准备数据
            daily_stats = {
                "category_minutes": category_minutes,
                "avg_activity_score": avg_activity,
                "productivity_analysis": productivity,
            }

            # AI分析
            print("  🤖 正在进行AI分析...")
            analysis = self.ai_analyzer.analyze_daily_data(daily_stats)

            # 保存汇总
            total_minutes = sum(category_minutes.values())
            self.db.save_daily_summary(
                target_date=target_date,
                work_minutes=category_minutes.get("work", 0),
                game_minutes=category_minutes.get("game", 0),
                entertainment_minutes=category_minutes.get("entertainment", 0),
                social_minutes=category_minutes.get("social", 0),
                browse_minutes=category_minutes.get("browse", 0),
                other_minutes=category_minutes.get("other", 0),
                total_active_minutes=total_minutes,
                avg_activity_score=avg_activity,
                mood_score=analysis.get("mood_score"),
                stress_score=analysis.get("stress_score"),
                summary_text=analysis.get("summary"),
                wechat_post=analysis.get("wechat_post")
            )

            # 显示结果
            print(f"  ✓ 分析完成!")
            print(f"    心情指数: {analysis.get('mood_score')}/10")
            print(f"    压力指数: {analysis.get('stress_score')}/10")
            print(f"    总结: {analysis.get('summary')}")
            print(f"    朋友圈文案:\n    {analysis.get('wechat_post')}")

            # 发送通知
            show_daily_report_notification(
                wechat_post=analysis.get("wechat_post", ""),
                mood_score=analysis.get("mood_score", 5),
                stress_score=analysis.get("stress_score", 5),
                summary=analysis.get("summary", "")
            )

            print("  ✓ 已发送桌面通知并复制文案")

        except Exception as e:
            print(f"  ❌ 生成报告失败: {e}")
            import traceback
            traceback.print_exc()

    def get_today_stats(self) -> dict:
        """获取今日实时统计"""
        today = datetime.now().date()
        category_minutes = self.db.get_category_duration_by_date(today)
        avg_activity = self.db.get_avg_activity_score_by_date(today)

        return {
            "date": today.isoformat(),
            "category_minutes": category_minutes,
            "avg_activity_score": avg_activity,
            "productivity": self.categorizer.analyze_productivity(category_minutes)
        }


def main():
    """主函数"""
    app = ActivityMonitorApp()

    # 处理退出信号
    def signal_handler(sig, frame):
        print("\n收到退出信号...")
        app.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 启动应用
    app.start()

    print("\n" + "=" * 50)
    print("DayReview 正在后台运行")
    print("=" * 50)
    print("命令:")
    print("  r - 立即生成今日报告")
    print("  s - 显示今日统计")
    print("  q - 退出程序")
    print("=" * 50 + "\n")

    # 主循环
    while True:
        try:
            cmd = input().strip().lower()

            if cmd == "q":
                break
            elif cmd == "r":
                # 生成今日报告（用于测试）
                app.generate_daily_report(datetime.now().date())
            elif cmd == "s":
                # 显示今日统计
                stats = app.get_today_stats()
                print("\n📊 今日统计:")
                for cat, minutes in stats["category_minutes"].items():
                    display_name = app.categorizer.get_category_display_name(cat)
                    emoji = app.categorizer.get_category_emoji(cat)
                    print(f"  {emoji} {display_name}: {minutes} 分钟")
                print(f"  📈 活跃度: {stats['avg_activity_score']:.1f}")
                prod = stats["productivity"]
                print(f"  💼 生产力: {prod['productivity_ratio']}%")
                print()

        except EOFError:
            break
        except Exception as e:
            print(f"错误: {e}")

    app.stop()


if __name__ == "__main__":
    main()
