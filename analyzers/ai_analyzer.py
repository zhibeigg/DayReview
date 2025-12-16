"""
AI分析模块 - 使用AI分析每日数据并生成朋友圈文案
"""
import json
from datetime import date
from typing import Optional

from ..config import (
    AI_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL
)
from ..utils.helpers import format_minutes


class AIAnalyzer:
    """AI分析器 - 分析数据并生成文案"""

    def __init__(self, provider: str = None):
        """
        初始化AI分析器

        Args:
            provider: AI提供商 (openai 或 anthropic)
        """
        self.provider = provider or AI_PROVIDER

    def analyze_daily_data(self, daily_stats: dict) -> dict:
        """
        分析每日数据，生成心情、压力指数和朋友圈文案

        Args:
            daily_stats: 每日统计数据，包含：
                - category_minutes: 各分类时长
                - top_apps: 使用最多的应用
                - avg_activity_score: 平均活跃度
                - productivity_analysis: 生产力分析

        Returns:
            分析结果，包含：
                - mood_score: 心情指数 (1-10)
                - stress_score: 压力指数 (1-10)
                - summary: 总结文本
                - wechat_post: 朋友圈文案
        """
        prompt = self._build_analysis_prompt(daily_stats)

        try:
            if self.provider == "openai":
                return self._call_openai(prompt)
            elif self.provider == "anthropic":
                return self._call_anthropic(prompt)
            else:
                # 降级到本地规则分析
                return self._local_analysis(daily_stats)
        except Exception as e:
            print(f"AI分析失败，使用本地分析: {e}")
            return self._local_analysis(daily_stats)

    def _build_analysis_prompt(self, stats: dict) -> str:
        """构建AI分析提示词"""
        category_minutes = stats.get("category_minutes", {})
        productivity = stats.get("productivity_analysis", {})
        avg_activity = stats.get("avg_activity_score", 0)

        # 格式化时长
        work_time = format_minutes(category_minutes.get("work", 0))
        game_time = format_minutes(category_minutes.get("game", 0))
        entertainment_time = format_minutes(category_minutes.get("entertainment", 0))
        social_time = format_minutes(category_minutes.get("social", 0))

        prompt = f"""请分析以下用户今日电脑使用数据，并生成分析报告和朋友圈文案。

## 今日数据
- 工作时长: {work_time}
- 游戏时长: {game_time}
- 娱乐时长: {entertainment_time}
- 社交时长: {social_time}
- 生产力比例: {productivity.get('productivity_ratio', 0)}%
- 休闲比例: {productivity.get('leisure_ratio', 0)}%
- 活跃度分数: {avg_activity:.1f}/100

## 分析要求
请根据以上数据推断：
1. 心情指数 (1-10分)：基于工作/休闲比例、活跃度推断
2. 压力指数 (1-10分)：工作时间长+活跃度高=压力大
3. 今日总结：简短描述今天的状态（1-2句话）
4. 朋友圈文案：有趣、积极、不暴露隐私的文案（不提及具体工作内容、网站、聊天对象）

## 朋友圈文案要求
- 长度：2-4行
- 风格：轻松、有趣、可以带emoji
- 不要提及：具体工作项目、访问的网站、聊天内容
- 可以提及：整体状态、效率感受、生活感悟
- 示例风格：
  "今日效率指数爆表💪 难得的专注日！"
  "又是和代码相爱相杀的一天"
  "工作与摸鱼的平衡艺术 ✨"

## 输出格式（JSON）
请严格按以下JSON格式输出：
{{
    "mood_score": 7,
    "stress_score": 5,
    "summary": "今天工作效率较高，休息适度",
    "wechat_post": "今日能量满格🔋\\n效率指数: ★★★★☆\\n充实的一天，晚安💤"
}}
"""
        return prompt

    def _call_openai(self, prompt: str) -> dict:
        """调用OpenAI API"""
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个友好的生活助手，擅长分析用户的日常活动数据并生成有趣的朋友圈文案。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        return json.loads(result_text)

    def _call_anthropic(self, prompt: str) -> dict:
        """调用Anthropic API"""
        import anthropic

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        result_text = response.content[0].text
        # 尝试从响应中提取JSON
        try:
            # 查找JSON块
            import re
            json_match = re.search(r'\{[^{}]*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        return json.loads(result_text)

    def _local_analysis(self, stats: dict) -> dict:
        """本地规则分析（无需API）"""
        category_minutes = stats.get("category_minutes", {})
        productivity = stats.get("productivity_analysis", {})
        avg_activity = stats.get("avg_activity_score", 0)

        work = category_minutes.get("work", 0)
        game = category_minutes.get("game", 0)
        entertainment = category_minutes.get("entertainment", 0)
        total = sum(category_minutes.values())

        # 计算心情分数
        if total == 0:
            mood_score = 5
        else:
            # 休闲时间多 -> 心情好
            leisure_ratio = (game + entertainment) / total
            mood_score = min(10, 5 + leisure_ratio * 5)

        # 计算压力分数
        if total == 0:
            stress_score = 3
        else:
            # 工作时间长+活跃度高 -> 压力大
            work_ratio = work / total
            stress_score = min(10, 3 + work_ratio * 4 + avg_activity / 25)

        # 生成总结
        if work > 360:  # 6小时以上
            summary = "今天工作时间较长，注意休息"
        elif game > 180:  # 3小时以上
            summary = "今天游戏时间较多，享受生活"
        elif productivity.get("balance_score", 0) > 70:
            summary = "今天工作与休息比较均衡"
        else:
            summary = "普通的一天"

        # 生成朋友圈文案
        wechat_post = self._generate_local_post(
            work, game, entertainment, total, avg_activity
        )

        return {
            "mood_score": round(mood_score, 1),
            "stress_score": round(stress_score, 1),
            "summary": summary,
            "wechat_post": wechat_post
        }

    def _generate_local_post(
        self,
        work: int,
        game: int,
        entertainment: int,
        total: int,
        activity: float
    ) -> str:
        """本地生成朋友圈文案"""
        posts = []

        if total == 0:
            return "今天好像没怎么用电脑 📱\n难得的数字断联日"

        work_hours = work // 60
        game_hours = game // 60

        # 根据不同情况选择文案
        if work > 480:  # 8小时以上工作
            posts = [
                f"今日肝度: MAX 💪\n效率指数拉满的一天",
                "又是被工作填满的一天\n但充实的感觉还不错 ✨",
                f"专注模式: ON\n今日战绩: {work_hours}h+",
            ]
        elif game > 180:  # 3小时以上游戏
            posts = [
                "今天的快乐源泉 🎮\n偶尔也要给自己放个假",
                "工作是为了更好的生活\n游戏是生活的一部分 ✌️",
                "充电完毕 🔋\n明天继续加油",
            ]
        elif work > 240 and game > 60:  # 工作4小时+游戏1小时
            posts = [
                "工作与摸鱼的平衡艺术 ⚖️\n今天很满意",
                "认真工作，快乐生活\n这就是成年人的日常",
                f"效率满满的一天 ✨\n劳逸结合才是王道",
            ]
        elif entertainment > 120:  # 娱乐2小时以上
            posts = [
                "今日份的放松时光 🎬\n生活需要仪式感",
                "偷得浮生半日闲 ☕\n享受当下",
            ]
        else:
            posts = [
                "普通但美好的一天 ☀️",
                "日常进行中...\n一切都是最好的安排",
                f"今日活力值: {'⭐' * min(5, int(activity / 20))}",
            ]

        import random
        return random.choice(posts)
