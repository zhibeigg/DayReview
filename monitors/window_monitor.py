"""
窗口监控模块 - 监控当前活动窗口
"""
import threading
import time
from datetime import datetime
from typing import Optional, Callable
import ctypes
from ctypes import wintypes

import win32gui
import win32process
import psutil


class WindowMonitor:
    """窗口监控器 - 追踪当前活动窗口"""

    def __init__(
        self,
        check_interval: float = 5.0,
        min_duration: float = 3.0,
        on_window_change: Callable = None
    ):
        """
        初始化窗口监控器

        Args:
            check_interval: 检查窗口的间隔（秒）
            min_duration: 最小记录时长（秒），过滤短暂切换
            on_window_change: 窗口切换时的回调函数
        """
        self.check_interval = check_interval
        self.min_duration = min_duration
        self.on_window_change = on_window_change

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._current_window: Optional[dict] = None
        self._window_start_time: Optional[datetime] = None

    def start(self):
        """启动监控"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """停止监控"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

        # 记录最后一个窗口
        if self._current_window and self._window_start_time:
            self._record_window_activity()

    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                window_info = self._get_active_window_info()

                if window_info:
                    # 检查窗口是否变化
                    if self._is_window_changed(window_info):
                        # 记录之前的窗口活动
                        if self._current_window and self._window_start_time:
                            self._record_window_activity()

                        # 更新当前窗口
                        self._current_window = window_info
                        self._window_start_time = datetime.now()

            except Exception as e:
                # 忽略临时错误（如窗口快速切换）
                pass

            time.sleep(self.check_interval)

    def _get_active_window_info(self) -> Optional[dict]:
        """获取当前活动窗口信息"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None

            # 获取窗口标题
            window_title = win32gui.GetWindowText(hwnd)
            if not window_title:
                return None

            # 获取进程ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            # 获取进程名称
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "Unknown"

            return {
                "hwnd": hwnd,
                "title": window_title,
                "process_name": process_name,
                "pid": pid
            }

        except Exception:
            return None

    def _is_window_changed(self, new_window: dict) -> bool:
        """检查窗口是否变化"""
        if not self._current_window:
            return True

        # 比较进程名和窗口句柄
        return (
            new_window["process_name"] != self._current_window["process_name"] or
            new_window["hwnd"] != self._current_window["hwnd"]
        )

    def _record_window_activity(self):
        """记录窗口活动"""
        if not self._current_window or not self._window_start_time:
            return

        end_time = datetime.now()
        duration = (end_time - self._window_start_time).total_seconds()

        # 过滤短暂活动
        if duration < self.min_duration:
            return

        activity = {
            "window_title": self._current_window["title"],
            "process_name": self._current_window["process_name"],
            "start_time": self._window_start_time,
            "end_time": end_time,
            "duration_seconds": int(duration)
        }

        # 调用回调
        if self.on_window_change:
            self.on_window_change(activity)

    def get_current_window(self) -> Optional[dict]:
        """获取当前正在监控的窗口"""
        return self._current_window

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running
