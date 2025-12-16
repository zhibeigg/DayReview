"""
桌面通知模块 - 发送通知并复制文案到剪贴板
"""
import subprocess
import webbrowser
from typing import Optional

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

try:
    from win10toast import ToastNotifier
    WIN10TOAST_AVAILABLE = True
except ImportError:
    WIN10TOAST_AVAILABLE = False


class Notifier:
    """桌面通知器"""

    def __init__(self):
        """初始化通知器"""
        self.toaster = None
        if WIN10TOAST_AVAILABLE:
            self.toaster = ToastNotifier()

    def send_notification(
        self,
        title: str,
        message: str,
        timeout: int = 10,
        callback: callable = None
    ) -> bool:
        """
        发送桌面通知

        Args:
            title: 通知标题
            message: 通知内容
            timeout: 显示时长（秒）
            callback: 点击回调

        Returns:
            是否发送成功
        """
        try:
            if WIN10TOAST_AVAILABLE and self.toaster:
                self.toaster.show_toast(
                    title,
                    message,
                    duration=timeout,
                    threaded=True
                )
                return True
            elif PLYER_AVAILABLE:
                notification.notify(
                    title=title,
                    message=message,
                    timeout=timeout
                )
                return True
            else:
                # 降级：使用PowerShell显示通知
                return self._powershell_notify(title, message)
        except Exception as e:
            print(f"发送通知失败: {e}")
            return False

    def _powershell_notify(self, title: str, message: str) -> bool:
        """使用PowerShell发送Windows通知"""
        try:
            # 转义特殊字符
            title = title.replace("'", "''")
            message = message.replace("'", "''").replace("\n", "`n")

            script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $template = @"
            <toast>
                <visual>
                    <binding template="ToastText02">
                        <text id="1">{title}</text>
                        <text id="2">{message}</text>
                    </binding>
                </visual>
            </toast>
"@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Activity Monitor").Show($toast)
            '''

            subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True,
                timeout=10
            )
            return True
        except Exception:
            return False

    def copy_to_clipboard(self, text: str) -> bool:
        """
        复制文本到剪贴板

        Args:
            text: 要复制的文本

        Returns:
            是否复制成功
        """
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except ImportError:
            # 使用PowerShell作为备选
            try:
                # 处理换行符
                text = text.replace("\n", "`n")
                subprocess.run(
                    ["powershell", "-Command", f'Set-Clipboard -Value "{text}"'],
                    capture_output=True,
                    timeout=5
                )
                return True
            except Exception:
                pass

        return False

    def open_wechat(self) -> bool:
        """
        尝试打开微信

        Returns:
            是否成功
        """
        try:
            # 常见的微信安装路径
            wechat_paths = [
                r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
                r"C:\Program Files\Tencent\WeChat\WeChat.exe",
                r"D:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
                r"D:\Program Files\Tencent\WeChat\WeChat.exe",
            ]

            import os
            for path in wechat_paths:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    return True

            # 尝试通过协议打开
            webbrowser.open("weixin://")
            return True
        except Exception:
            return False

    def notify_with_copy(
        self,
        title: str,
        message: str,
        copy_text: str,
        open_wechat: bool = True
    ) -> bool:
        """
        发送通知并复制文案

        Args:
            title: 通知标题
            message: 通知内容（显示在通知中）
            copy_text: 要复制的文本（朋友圈文案）
            open_wechat: 是否打开微信

        Returns:
            是否成功
        """
        # 复制文案到剪贴板
        copy_success = self.copy_to_clipboard(copy_text)

        # 发送通知
        if copy_success:
            message += "\n\n✅ 文案已复制到剪贴板"
        else:
            message += "\n\n⚠️ 复制失败，请手动复制"

        notify_success = self.send_notification(title, message, timeout=15)

        # 打开微信
        if open_wechat:
            self.open_wechat()

        return notify_success and copy_success


def show_daily_report_notification(
    wechat_post: str,
    mood_score: float,
    stress_score: float,
    summary: str
):
    """
    显示每日报告通知

    Args:
        wechat_post: 朋友圈文案
        mood_score: 心情指数
        stress_score: 压力指数
        summary: 今日总结
    """
    notifier = Notifier()

    title = "📊 今日活动报告"
    message = f"心情: {'😊' * int(mood_score / 2)} ({mood_score}/10)\n"
    message += f"压力: {'😰' * int(stress_score / 2)} ({stress_score}/10)\n"
    message += f"{summary}"

    notifier.notify_with_copy(
        title=title,
        message=message,
        copy_text=wechat_post,
        open_wechat=True
    )
