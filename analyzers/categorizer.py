"""
应用分类器 - 将应用程序分类为工作、游戏、娱乐等
"""
from typing import Optional

from ..config import APP_CATEGORIES


class Categorizer:
    """应用分类器"""

    def __init__(self, custom_categories: dict = None):
        """
        初始化分类器

        Args:
            custom_categories: 自定义分类规则，会与默认规则合并
        """
        self.categories = APP_CATEGORIES.copy()
        if custom_categories:
            for category, keywords in custom_categories.items():
                if category in self.categories:
                    self.categories[category].extend(keywords)
                else:
                    self.categories[category] = keywords

    def categorize(self, process_name: str, window_title: str = "") -> str:
        """
        根据进程名和窗口标题判断分类

        Args:
            process_name: 进程名称
            window_title: 窗口标题

        Returns:
            分类名称 (work, game, entertainment, social, browse, other)
        """
        # 转小写进行匹配
        process_lower = process_name.lower() if process_name else ""
        title_lower = window_title.lower() if window_title else ""
        combined = f"{process_lower} {title_lower}"

        # 按优先级检查（游戏 > 工作 > 娱乐 > 社交 > 浏览）
        priority_order = ["game", "work", "entertainment", "social", "browse"]

        for category in priority_order:
            keywords = self.categories.get(category, [])
            for keyword in keywords:
                if keyword.lower() in combined:
                    return category

        return "other"

    def get_category_display_name(self, category: str) -> str:
        """获取分类的显示名称"""
        display_names = {
            "work": "工作",
            "game": "游戏",
            "entertainment": "娱乐",
            "social": "社交",
            "browse": "浏览",
            "other": "其他",
        }
        return display_names.get(category, category)

    def add_custom_keyword(self, category: str, keyword: str):
        """添加自定义关键词"""
        if category not in self.categories:
            self.categories[category] = []
        if keyword.lower() not in [k.lower() for k in self.categories[category]]:
            self.categories[category].append(keyword)

    def get_category_emoji(self, category: str) -> str:
        """获取分类的emoji"""
        emojis = {
            "work": "💼",
            "game": "🎮",
            "entertainment": "🎬",
            "social": "💬",
            "browse": "🌐",
            "other": "📁",
        }
        return emojis.get(category, "📁")

    def analyze_productivity(self, category_minutes: dict) -> dict:
        """
        分析生产力指标

        Args:
            category_minutes: 各分类的时长（分钟）

        Returns:
            生产力分析结果
        """
        work = category_minutes.get("work", 0)
        game = category_minutes.get("game", 0)
        entertainment = category_minutes.get("entertainment", 0)
        social = category_minutes.get("social", 0)
        browse = category_minutes.get("browse", 0)
        other = category_minutes.get("other", 0)

        total = work + game + entertainment + social + browse + other

        if total == 0:
            return {
                "productivity_ratio": 0,
                "leisure_ratio": 0,
                "work_focus_score": 0,
                "balance_score": 50,
            }

        # 生产力比例（工作时间占总时间）
        productivity_ratio = work / total * 100

        # 休闲比例（游戏+娱乐时间占总时间）
        leisure_ratio = (game + entertainment) / total * 100

        # 工作专注度（工作时间 / (工作+社交+浏览)）
        work_related = work + social + browse
        work_focus_score = (work / work_related * 100) if work_related > 0 else 0

        # 平衡度（理想比例：工作60%，休闲30%，其他10%）
        ideal_work = 60
        ideal_leisure = 30
        work_diff = abs(productivity_ratio - ideal_work)
        leisure_diff = abs(leisure_ratio - ideal_leisure)
        balance_score = max(0, 100 - work_diff - leisure_diff)

        return {
            "productivity_ratio": round(productivity_ratio, 1),
            "leisure_ratio": round(leisure_ratio, 1),
            "work_focus_score": round(work_focus_score, 1),
            "balance_score": round(balance_score, 1),
        }
