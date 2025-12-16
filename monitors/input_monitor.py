"""
键鼠活动监控模块 - 统计键盘和鼠标活动（不记录具体内容）
"""
import threading
import time
from datetime import datetime
from typing import Optional, Callable

from pynput import keyboard, mouse


class InputMonitor:
    """键鼠活动监控器 - 只统计次数，不记录内容"""

    def __init__(
        self,
        stats_interval: float = 60.0,
        on_stats_ready: Callable = None
    ):
        """
        初始化键鼠监控器

        Args:
            stats_interval: 统计间隔（秒）
            on_stats_ready: 统计数据就绪时的回调函数
        """
        self.stats_interval = stats_interval
        self.on_stats_ready = on_stats_ready

        self._running = False
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        self._stats_thread: Optional[threading.Thread] = None

        # 计数器
        self._keyboard_count = 0
        self._mouse_click_count = 0
        self._mouse_move_count = 0
        self._lock = threading.Lock()

    def start(self):
        """启动监控"""
        if self._running:
            return

        self._running = True
        self._reset_counters()

        # 启动键盘监听
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press
        )
        self._keyboard_listener.start()

        # 启动鼠标监听
        self._mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            on_move=self._on_mouse_move
        )
        self._mouse_listener.start()

        # 启动统计线程
        self._stats_thread = threading.Thread(target=self._stats_loop, daemon=True)
        self._stats_thread.start()

    def stop(self):
        """停止监控"""
        self._running = False

        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None

        if self._stats_thread:
            self._stats_thread.join(timeout=2)
            self._stats_thread = None

    def _on_key_press(self, key):
        """键盘按下事件（只计数）"""
        with self._lock:
            self._keyboard_count += 1

    def _on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件（只计数）"""
        if pressed:
            with self._lock:
                self._mouse_click_count += 1

    def _on_mouse_move(self, x, y):
        """鼠标移动事件（采样计数，避免过多）"""
        # 每10次移动计1次，减少数据量
        with self._lock:
            self._mouse_move_count += 0.1

    def _reset_counters(self):
        """重置计数器"""
        with self._lock:
            self._keyboard_count = 0
            self._mouse_click_count = 0
            self._mouse_move_count = 0

    def _get_and_reset_stats(self) -> dict:
        """获取统计数据并重置"""
        with self._lock:
            stats = {
                "timestamp": datetime.now(),
                "keyboard_count": self._keyboard_count,
                "mouse_count": int(self._mouse_click_count + self._mouse_move_count)
            }
            self._keyboard_count = 0
            self._mouse_click_count = 0
            self._mouse_move_count = 0
            return stats

    def _stats_loop(self):
        """统计循环"""
        while self._running:
            time.sleep(self.stats_interval)

            if not self._running:
                break

            stats = self._get_and_reset_stats()

            # 调用回调
            if self.on_stats_ready:
                self.on_stats_ready(stats)

    def get_current_stats(self) -> dict:
        """获取当前统计（不重置）"""
        with self._lock:
            return {
                "keyboard_count": self._keyboard_count,
                "mouse_count": int(self._mouse_click_count + self._mouse_move_count)
            }

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running
