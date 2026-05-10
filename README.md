明白，之前的排版确实稍微有点“常规”。为了让这份 README 既保留你**所有的核心关键命令**，又能体现出“技术大牛”的高级质感，我采用了**侧边导栏风格**、**逻辑色块隔离**和**符号指引**的设计。

这种排版模仿了现代开源项目的文档风格，重点更突出，层级更清晰。

---

# 📱 WeChat Moments Bot

### —— 打造你的 FinTech 技术人设专家

**让每一条朋友圈，都成为你职业形象的“信用背书”。**
本工具自动化抓取全球顶尖 **AI 技术干货**与 **HSBC (汇丰) 行业资讯**，利用 LLM (Claude/GPT) 深度建模，为你生成极具洞察力的朋友圈文案。

---

## 💎 核心愿景

* **【深度人设】** 拒绝简单的信息搬运，AI 模拟专家视角提供深度点评。
* **【自动化流】** 从抓取、筛选到文案生成及推送，实现全链条“零人工”参与。
* **【高效同步】** 通过 Server酱 直达微信，手机一键复制即可完成每日高质量输出。

---

## ⚡ 快速开始

### 1️⃣ 环境初始化

在项目根目录执行以下命令，构建独立的运行空间：

| 平台 | 激活命令 (Virtual Env) |
| --- | --- |
| **PowerShell** | `python -m venv .venv; .venv\Scripts\Activate.ps1` |
| **CMD** | `python -m venv .venv` & ` .venv\Scripts\activate.bat` |
| **Linux/macOS** | `python3 -m venv .venv && source .venv/bin/activate` |

**安装依赖库：**

```bash
pip install -r requirements.txt

```

### 2️⃣ 敏感 Key 配置 (环境变量)

推荐使用环境变量而非修改源码，以保障 API 安全：

> [!IMPORTANT]
> **PowerShell:**
> `$env:ANTHROPIC_API_KEY = "sk-..."`
> `$env:SERVERCHAN_SENDKEY = "SCT..."`
> **CMD:**
> `set ANTHROPIC_API_KEY=sk-...`
> `set SERVERCHAN_SENDKEY=SCT...`

---

## ⏰ 生产力部署 (Windows 任务计划)

无需手动触发，利用内置脚本将程序挂载为 Windows 后台定时任务。

**一键管理员部署 (PowerShell):**

```powershell
Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd /d %CD% && setup_task.bat" -Verb RunAs

```

**进阶：动态设定时间并部署：**

```powershell
# 指定在 18:44 运行并安装任务
Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd /d C:\Users\13822\Desktop\wechat_moments_bot && set PUSH_HOUR=18 && set PUSH_MIN=44 && setup_task.bat" -Verb RunAs

```

---

## 🛠️ 常用维护命令

| 需求 | 命令 |
| --- | --- |
| **功能自测** | `python main.py test` |
| **手动立即触发** | `$env:PUSH_HOUR=18; $env:PUSH_MIN=37; python main.py` |
| **查看运行日志** | `ls logs/` |
| **重置已读记录** | `rm data/seen_articles.json` |

---

## 📁 项目结构分解

```bash
wechat_moments_bot/
├── config.py           # 🧠 逻辑配置 (RSS源、AI 筛选准则)
├── main.py             # 🎮 入口程序
├── fetcher.py          # 📡 资讯检索 (RSS 抓取引擎)
├── writer.py           # ✍️ AI 文案 (大模型评分与撰写)
├── pusher.py           # 📲 消息分发 (Server酱 接口)
├── setup_task.bat      # 🛠️ 自动化工具 (Windows 任务安装)
├── data/               # 💾 数据持久化 (去重记录)
└── logs/               # 📝 系统运行日志

```

---

## 📄 商业与许可

* **开源协议**：本项目遵循 **Apache License 2.0** 协议。
* **商业授权**：若需商业使用或定制开发，请参考 `COMMERCIAL.md` 或发送邮件至 [13822124279@163.com]()。

---

**“把重复的看技术文章留给AI，把宝贵的思考留给未来”**