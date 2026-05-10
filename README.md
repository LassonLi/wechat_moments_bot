# 📱 朋友圈助手 — 使用说明

自动抓取 AI 技术文章 + HSBC 资讯，生成朋友圈配文，每天早上推送到你的微信。

---

## 📁 文件结构

```
wechat_moments_bot/
├── config.py          ← ⭐ 所有配置（只需改这个）
├── main.py            ← 主程序入口
├── fetcher.py         ← 抓取 RSS + 筛选文章
├── writer.py          ← 调用 Claude 生成配文
├── pusher.py          ← 通过 Server酱 推送微信
├── setup_task.bat     ← 一键配置定时任务（Windows）
├── requirements.txt   ← 依赖库
├── data/              ← 自动生成（存储已推送记录）
└── logs/              ← 自动生成（每天运行日志）
```

---

## 🚀 第一步：安装依赖

打开命令提示符（CMD），进入项目目录，运行：

```cmd
cd 你的项目路径\wechat_moments_bot
pip install -r requirements.txt
```

---

## 🔑 第二步：配置 API Key

打开 `config.py`，填入以下两个 Key：

### 1. Anthropic API Key（生成配文用）
- 注册地址：https://console.anthropic.com/
- 注册后在 "API Keys" 页面创建 Key
- 填入 `config.py` 的 `ANTHROPIC_API_KEY`

### 2. Server酱 SendKey（推送微信通知用）
- 注册地址：https://sct.ftqq.com/
- 用微信扫码登录，即可获得 SendKey
- 填入 `config.py` 的 `SERVERCHAN_SENDKEY`
- 免费版每天可推送 500 条，完全够用

---

## ✅ 第三步：测试配置是否正确

```cmd
python main.py test
```

如果微信收到"✅ 朋友圈助手配置成功"的通知，说明一切正常。

---

## ⏰ 第四步：配置每日自动运行（Windows 任务计划）

**右键点击 `setup_task.bat` → 以管理员身份运行**

脚本会自动创建一个 Windows 定时任务，每天早上 9:00 自动运行。

> ⚠️ 注意：电脑需要在早上 9:00 处于开机状态。
> 如需修改运行时间，打开 `config.py` 修改 `push_hour`，然后重新运行 `setup_task.bat`。

---

## 📲 使用流程

每天早上 9:00，你的微信会收到这样的通知：

```
📱 朋友圈推荐 05月09日 — AI文章×2

---
1. [文章标题](链接)
来源：量子位 | 类型：🤖 AI技术 | 发布：2026-05-08

📝 朋友圈配文（直接复制）：

大模型可解释性迎来重要突破...
#LLM

https://www.qbitai.com/...
---
```

你只需要：
1. 点击文章链接确认内容
2. 复制配文框里的文字
3. 打开朋友圈粘贴发布 ← 全程约 30 秒

---

## ⚙️ 自定义配置

所有配置都在 `config.py` 里，可以按需调整：

| 配置项 | 说明 |
|--------|------|
| `push_hour` | 每天几点运行（改完需重跑 setup_task.bat） |
| `ai_per_week` | 每周推几篇 AI 文章 |
| `hsbc_per_biweek` | 每两周推几篇 HSBC 文章 |
| `AI_CRITERIA.keywords_must` | AI 文章必含关键词 |
| `HSBC_CRITERIA.keywords_ban` | HSBC 文章黑名单词 |
| `RSS_SOURCES` | 增减抓取来源 |

---

## 🛠️ 手动运行

```cmd
# 正常执行一次（不等定时，立刻抓取推送）
python main.py

# 测试 Server酱 连接
python main.py test
```

---

## ❓ 常见问题

**Q: 收不到微信通知？**
先运行 `python main.py test` 看测试消息能否送达。如果也收不到，检查 Server酱 页面上 SendKey 是否填写正确。

**Q: 某个 RSS 源抓取失败？**
查看 `logs/` 目录下当天的日志文件，会有具体错误信息。部分国内源可能需要代理。

**Q: 想添加新的文章来源？**
在 `config.py` 的 `RSS_SOURCES` 里添加新条目，格式参考现有的即可。

**Q: 文章重复推送？**
`data/seen_articles.json` 记录了所有已推送过的文章 ID，正常情况下不会重复。如需重置，删除该文件即可。

---

## 🧰 虚拟环境（推荐）

建议在虚拟环境中运行本项目以避免与系统包冲突。下面是在不同环境下的常用命令（均在项目根目录下运行）：

PowerShell (Windows)：

```powershell
# 创建虚拟环境（只需执行一次）
python -m venv venv

# 激活虚拟环境
venv\Scripts\Activate.ps1

# 安装依赖（如尚未安装）
pip install -r requirements.txt

# 运行项目
python main.py
```

如果 PowerShell 报错阻止运行脚本，可临时允许当前用户运行脚本（以管理员或当前用户权限运行一次）：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

命令提示符（CMD）：

```cmd
venv\Scripts\activate.bat
```

Git Bash / WSL / macOS / Linux：

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

退出虚拟环境：

```bash
deactivate
```

如果你需要，我可以把这些命令也添加到 `setup_task.bat` 或写成一个简短的 `setup_venv.bat` 脚本来一键创建并激活（Windows）。
