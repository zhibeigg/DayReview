"""
辅助函数模块
"""
from datetime import datetime, timedelta
import re
from typing import Optional


def format_duration(seconds: int) -> str:
    """将秒数转换为可读的时长格式"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}分钟"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}小时{minutes}分钟"
        return f"{hours}小时"


def format_minutes(minutes: int) -> str:
    """将分钟数转换为可读格式"""
    if minutes < 60:
        return f"{minutes}分钟"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes > 0:
        return f"{hours}小时{remaining_minutes}分钟"
    return f"{hours}小时"


def sanitize_text(text: str, filter_keywords: list[str] = None) -> str:
    """清理文本，移除敏感信息"""
    if not text:
        return ""

    # 默认过滤词
    default_filters = [
        "password", "密码", "账号", "account",
        "银行", "bank", "支付", "payment",
    ]

    filters = filter_keywords or default_filters

    result = text
    for keyword in filters:
        # 不区分大小写替换
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        result = pattern.sub("[隐私]", result)

    return result


def get_today_range() -> tuple[datetime, datetime]:
    """获取今天的时间范围"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    return today, tomorrow


def get_yesterday_range() -> tuple[datetime, datetime]:
    """获取昨天的时间范围"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    return yesterday, today


def parse_window_title(title: str) -> Optional[str]:
    """解析窗口标题，提取主要信息"""
    if not title:
        return None

    # 移除常见的后缀
    suffixes_to_remove = [
        " - Google Chrome",
        " - Mozilla Firefox",
        " - Microsoft Edge",
        " - Visual Studio Code",
        " - PyCharm",
        " | Microsoft Teams",
        " - Notepad++",
    ]

    result = title
    for suffix in suffixes_to_remove:
        if result.endswith(suffix):
            result = result[:-len(suffix)]

    return result.strip()


def calculate_activity_score(keyboard_count: int, mouse_count: int) -> float:
    """计算活跃度分数 (0-100)"""
    # 假设每分钟键盘100次+鼠标50次为满分活跃
    keyboard_score = min(keyboard_count / 100, 1) * 60  # 键盘占60%
    mouse_score = min(mouse_count / 50, 1) * 40  # 鼠标占40%
    return keyboard_score + mouse_score


def stars_display(score: float, max_score: float = 10, max_stars: int = 5) -> str:
    """将分数转换为星级显示"""
    ratio = score / max_score
    filled_stars = int(ratio * max_stars)
    return "⭐" * filled_stars + "☆" * (max_stars - filled_stars)
