"""
DayReview - 系统托盘版主程序
"""
import sys
import os
import threading
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("警告: pystray 或 Pillow 未安装，无法使用系统托盘")

from DayReview.main import ActivityMonitorApp


class TrayApp:
    """系统托盘应用"""

    def __init__(self):
        """初始化托盘应用"""
        self.app = ActivityMonitorApp()
        self.icon = None

    def create_icon_image(self) -> 'Image':
        """创建托盘图标"""
        # 创建一个简单的图标
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 绘制一个圆形（代表监控状态）
        margin = 4
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=(76, 175, 80),  # 绿色
            outline=(255, 255, 255)
        )

        # 绘制一个小眼睛图案
        eye_size = 20
        center = size // 2
        draw.ellipse(
            [center - eye_size // 2, center - eye_size // 2,
             center + eye_size // 2, center + eye_size // 2],
            fill=(255, 255, 255)
        )
        pupil_size = 8
        draw.ellipse(
            [center - pupil_size // 2, center - pupil_size // 2,
             center + pupil_size // 2, center + pupil_size // 2],
            fill=(33, 33, 33)
        )

        return image

    def get_menu(self) -> 'pystray.Menu':
        """创建托盘菜单"""
        return pystray.Menu(
            pystray.MenuItem(
                "📊 查看今日统计",
                self.show_stats
            ),
            pystray.MenuItem(
                "📝 立即生成报告",
                self.generate_report
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "⏸️ 暂停监控" if self.app._running else "▶️ 恢复监控",
                self.toggle_monitoring
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "❌ 退出",
                self.quit
            )
        )

    def show_stats(self, icon=None, item=None):
        """显示今日统计"""
        stats = self.app.get_today_stats()

        message = "今日统计:\n"
        for cat, minutes in stats["category_minutes"].items():
            display_name = self.app.categorizer.get_category_display_name(cat)
            message += f"{display_name}: {minutes}分钟\n"

        prod = stats["productivity"]
        message += f"\n生产力: {prod['productivity_ratio']}%"
        message += f"\n活跃度: {stats['avg_activity_score']:.0f}"

        self.app.notifier.send_notification(
            title="📊 今日活动统计",
            message=message,
            timeout=10
        )

    def generate_report(self, icon=None, item=None):
        """生成报告"""
        def _generate():
            self.app.generate_daily_report(datetime.now().date())

        threading.Thread(target=_generate, daemon=True).start()

    def toggle_monitoring(self, icon=None, item=None):
        """切换监控状态"""
        if self.app._running:
            self.app.window_monitor.stop()
            self.app.input_monitor.stop()
            self.app._running = False
            self.app.notifier.send_notification(
                "DayReview",
                "监控已暂停",
                timeout=3
            )
        else:
            self.app._running = True
            self.app.window_monitor.start()
            self.app.input_monitor.start()
            self.app.notifier.send_notification(
                "DayReview",
                "监控已恢复",
                timeout=3
            )

        # 更新菜单
        if self.icon:
            self.icon.menu = self.get_menu()

    def quit(self, icon=None, item=None):
        """退出应用"""
        self.app.stop()
        if self.icon:
            self.icon.stop()

    def run(self):
        """运行托盘应用"""
        if not TRAY_AVAILABLE:
            print("系统托盘不可用，使用命令行模式")
            from DayReview.main import main
            main()
            return

        # 启动监控
        self.app.start()

        # 创建托盘图标
        self.icon = pystray.Icon(
            "DayReview",
            self.create_icon_image(),
            "DayReview",
            self.get_menu()
        )

        # 显示启动通知
        self.app.notifier.send_notification(
            "DayReview 已启动",
            "程序正在后台运行\n右键托盘图标查看选项",
            timeout=5
        )

        # 运行托盘图标（阻塞）
        self.icon.run()


def main():
    """主函数"""
    tray_app = TrayApp()
    tray_app.run()


if __name__ == "__main__":
    main()
