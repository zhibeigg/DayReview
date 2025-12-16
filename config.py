"""
配置文件 - 请在使用前填写您的API密钥
"""
import os

# AI API 配置 (选择一个使用)
# OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-openai-api-key-here")
OPENAI_MODEL = "gpt-4o-mini"  # 或 gpt-4o

# Anthropic Claude
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "your-anthropic-api-key-here")
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

# 选择使用哪个AI (openai 或 anthropic)
AI_PROVIDER = "anthropic"

# 监控配置
WINDOW_CHECK_INTERVAL = 5  # 秒，检测窗口切换的间隔
INPUT_STATS_INTERVAL = 60  # 秒，统计键鼠活动的间隔
MIN_ACTIVITY_DURATION = 3  # 秒，最小活动记录时长（过滤短暂切换）

# 数据库路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "activity.db")

# 定时任务配置
DAILY_ANALYSIS_TIME = "00:00"  # 每日分析时间

# 应用分类规则
APP_CATEGORIES = {
    "work": [
        "code", "vscode", "visual studio", "pycharm", "idea", "webstorm",
        "sublime", "notepad++", "vim", "nvim", "atom",
        "word", "excel", "powerpoint", "wps", "outlook",
        "terminal", "cmd", "powershell", "windowsterminal",
        "postman", "insomnia", "datagrip", "navicat", "dbeaver",
        "figma", "sketch", "photoshop", "illustrator",
        "notion", "obsidian", "typora", "markdown",
        "git", "github desktop", "sourcetree",
        "slack", "teams", "zoom", "腾讯会议", "钉钉",
    ],
    "game": [
        "steam", "epic games", "origin", "uplay", "battle.net",
        "league of legends", "lol", "英雄联盟",
        "genshin", "原神", "崩坏", "honkai",
        "minecraft", "我的世界",
        "csgo", "cs2", "counter-strike",
        "valorant", "无畏契约",
        "apex", "pubg", "绝地求生",
        "王者荣耀", "和平精英",
        "dota", "overwatch", "守望先锋",
        "elden ring", "艾尔登法环",
        "game", "游戏",
    ],
    "entertainment": [
        "bilibili", "哔哩哔哩", "b站",
        "youtube", "netflix", "爱奇艺", "iqiyi", "优酷", "youku", "腾讯视频",
        "抖音", "tiktok", "快手",
        "spotify", "网易云", "cloudmusic", "qq音乐", "酷狗", "酷我",
        "potplayer", "vlc", "mpv", "kmplayer",
        "twitch", "虎牙", "斗鱼", "直播",
    ],
    "social": [
        "微信", "wechat", "weixin",
        "qq", "tim",
        "discord", "telegram", "signal",
        "twitter", "x", "微博", "weibo",
        "instagram", "facebook",
        "小红书", "知乎", "zhihu",
    ],
    "browse": [
        "chrome", "firefox", "edge", "safari", "opera", "brave",
        "浏览器", "browser",
    ],
}

# 隐私保护 - 这些关键词将从分析中过滤
PRIVACY_FILTER_KEYWORDS = [
    "password", "密码", "账号", "account",
    "银行", "bank", "支付", "payment",
    "身份证", "id card",
]
