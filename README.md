# DayReview - 一天回顾

自动监控你的电脑使用行为，每天0点生成分析报告和朋友圈文案。

## 功能特点

- **全面监控**: 记录应用使用时长、键鼠活跃度
- **智能分类**: 自动将应用分为工作、游戏、娱乐、社交等类别
- **AI分析**: 使用AI分析心情指数、压力指数
- **朋友圈文案**: 自动生成隐私安全的朋友圈文案
- **桌面通知**: 0点弹窗提醒，一键复制文案
- **系统托盘**: 后台静默运行

## 安装

```bash
cd DayReview
pip install -r requirements.txt
```

或双击运行 `install.bat`

## 配置

编辑 `config.py` 文件:

```python
# 选择AI提供商 (openai 或 anthropic)
AI_PROVIDER = "openai"

# 填写对应的API密钥
OPENAI_API_KEY = "your-api-key"
# 或
ANTHROPIC_API_KEY = "your-api-key"
```

也可以通过环境变量设置:
```bash
set OPENAI_API_KEY=your-api-key
```

## 运行

### 命令行模式
```bash
python main.py
```

可用命令:
- `r` - 立即生成今日报告
- `s` - 显示今日统计
- `q` - 退出程序

### 系统托盘模式（推荐）
```bash
python tray_app.py
```
或双击 `start.bat`

程序会最小化到系统托盘，右键点击图标可以:
- 查看今日统计
- 立即生成报告
- 暂停/恢复监控
- 退出程序

## 数据存储

- 数据库文件: `data/activity.db`
- 详细数据保留30天
- 每日汇总永久保留

## 隐私保护

- 仅统计键鼠活动次数，不记录具体按键内容
- 朋友圈文案不包含:
  - 具体工作项目/代码内容
  - 访问的具体网站
  - 聊天对象和内容
  - 敏感关键词

## 自定义分类

在 `config.py` 中修改 `APP_CATEGORIES` 添加自定义应用分类:

```python
APP_CATEGORIES = {
    "work": ["your-app", ...],
    "game": ["your-game", ...],
    ...
}
```

## 文件结构

```
DayReview/
├── main.py              # 命令行主程序
├── tray_app.py          # 系统托盘版
├── config.py            # 配置文件
├── requirements.txt     # 依赖包
├── install.bat          # 安装脚本
├── start.bat            # 启动脚本
├── monitors/            # 监控模块
├── analyzers/           # 分析模块
├── database/            # 数据库模块
├── notifier/            # 通知模块
├── utils/               # 工具函数
└── data/                # 数据存储目录
```

## 注意事项

1. 首次运行需要管理员权限（监控键鼠需要）
2. 防病毒软件可能误报，请添加白名单
3. 如果AI分析失败，会自动降级为本地规则分析
