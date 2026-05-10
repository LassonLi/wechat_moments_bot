# 📱 朋友圈助手 — 使用说明

自动抓取 AI 技术文章与 HSBC 资讯，生成朋友圈配文并按计划推送到你的微信。

---

## 📁 文件结构

```
wechat_moments_bot/
├── config.py          ← 配置（支持从环境变量读取敏感 key）
├── main.py            ← 主程序入口
├── fetcher.py         ← 抓取 RSS + 筛选文章
├── writer.py          ← 调用大模型生成配文与评分逻辑
├── pusher.py          ← 通过 Server酱 推送微信
├── setup_task.bat     ← 一键配置 Windows 定时任务
├── requirements.txt   ← 依赖库
├── data/              ← 运行时数据（seen_articles.json 等）
└── logs/              ← 运行日志
```

---

## ⚡ 快速开始（推荐顺序）

运行环境要求：Python 3.13

1) 创建并激活虚拟环境（在项目根目录执行）：

PowerShell (Windows)：
```powershell
# 创建虚拟环境（使用 .venv）
python -m venv .venv
.venv\Scripts\Activate.ps1
```

CMD (Windows)：
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

macOS / Linux / WSL：
```bash
python -m venv .venv
source .venv/bin/activate
```

2) 安装依赖：
```bash
pip install -r requirements.txt
```

3) 配置敏感 Key（推荐通过环境变量，不要把 Key 写入仓库）

在 `config.py` 中，项目优先从环境变量读取两个敏感 Key：
- `ANTHROPIC_API_KEY`（用于生成配文/评分）
- `SERVERCHAN_SENDKEY`（用于通过 Server酱推送微信）

在 PowerShell 设置（临时当前会话）：
```powershell
$env:ANTHROPIC_API_KEY = "sk-..."
$env:SERVERCHAN_SENDKEY = "SCT..."
```

在 CMD（临时当前会话）：
```cmd
set ANTHROPIC_API_KEY=sk-...
set SERVERCHAN_SENDKEY=SCT...
```

在 macOS/Linux（临时当前会话）：
```bash
export ANTHROPIC_API_KEY="sk-..."
export SERVERCHAN_SENDKEY="SCT..."
```

（可选）把变量写入系统环境或用户 profile，以便长期使用。

4) 运行一次测试：
```bash
python main.py test
```
如果收到测试推送，说明配置正确。

---

## ⏰ 将脚本设置为每天自动运行（Windows 任务计划）

使用 `setup_task.bat`（右键→以管理员运行）可以创建定时任务。修改运行时间请更新 `config.py` 中的 `SCHEDULE` 项，然后重新运行该脚本。

---

## 使用流程简介

每日运行时，系统会抓取候选文章、进行两轮（标题+内容）筛选并生成配文，最后通过 Server酱推送到微信。推送中包含文章标题、来源、配文文本，直接复制到朋友圈即可。

---

## 常见命令

立即运行一次：
```bash
python main.py
```

生成测试推送：
```bash
python main.py test
```

查看本地日志：
```bash
ls logs/
```

---

## 配置说明（简要）

- `config.py` 中包含抓取源、筛选规则和推送节奏等设置；敏感 Key 推荐通过环境变量提供。
- `AI_CRITERIA` / `HSBC_CRITERIA`：用于过滤与命中候选文章。
- `RSS_SOURCES`：可在此添加或移除抓取源。

---

## 许可与商业使用

- 本仓库代码以 `Apache License 2.0` 许可（详见 `LICENSE`）。这允许广泛的使用、修改和分发，并包含专利授权条款。
- 如果你计划将本项目用于商业产品、付费服务或需要额外的法律/支持保证，请参阅 `COMMERCIAL.md` 或联系 13822124279@163.com 获取商业授权。
- 贡献者请阅读 `CONTRIBUTING.md`，提交代码即表示同意贡献许可条款（允许项目方在必要时以商业方式使用贡献）。

---

## 开发 / 调试提示

- 如果抓取某些 RSS 源失败，可检查网络或使用代理。错误信息会记录在 `logs/`。
- 去重信息保存在 `data/seen_articles.json`，删除该文件可重置记录。

---

如果你希望我把虚拟环境创建命令写进 `setup_venv.bat` 或添加一个示例 `.env.example`，我可以继续处理。
