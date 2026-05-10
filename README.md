
---

# 🚀 WeChat Moments Bot — 朋友圈技术人设智造家

**「让每一条朋友圈，都在为你积累职业信用与行业声望。」**

在这个信息过载的时代，持续且高质量的专业输出是构建**个人品牌**最快的路径。`WeChat Moments Bot` 自动化抓取全球顶尖 **AI 技术干货**与 **HSBC（汇丰）财讯**，通过大模型生成极具洞见的配文，助你轻松打造专业、前沿、有深度的 FinTech 技术专家形象。

---

## 🌟 核心价值

* **人设自动化**：AI 每日精选高含金量资讯，确保你的朋友圈永远走在技术前沿。
* **深度洞察力**：依托 Anthropic/QWEN 深度总结，配文自带“专家视角”，拒绝机械转发。
* **极简流转**：Server酱推送提醒，手机上一键复制粘贴，30 秒完成高质量更新。

---

## ⚡ 快速开始（环境要求：Python 3.13）

### 1. 虚拟环境配置

在项目根目录执行，确保环境独立纯净：

* **PowerShell (Windows)**:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

```


* **CMD (Windows)**:

```cmd
    python -m venv .venv
    .venv\Scripts\activate.bat
    ```
*   **macOS / Linux**:
    
```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

### 2. 安装依赖
```bash
pip install -r requirements.txt

```

### 3. 配置敏感 Key（推荐使用环境变量）

为了安全，请通过命令行设置临时环境变量进行测试（不要将 Key 直接写入代码）：

* **PowerShell**:

```powershell
    $env:ANTHROPIC_API_KEY = "sk-..."
    $env:SERVERCHAN_SENDKEY = "SCT..."
    ```
*   **CMD**:
    
```cmd
    set ANTHROPIC_API_KEY=sk-...
    set SERVERCHAN_SENDKEY=SCT...
    ```
*   **macOS / Linux**:
    
```bash
    export ANTHROPIC_API_KEY="sk-..."
    export SERVERCHAN_SENDKEY="SCT..."
    ```

---

## ⏰ 自动化部署（Windows 定时任务）

使用内置脚本实现每日自动抓取与推送。若需修改运行时间，请先更新 `config.py` 中的 `SCHEDULE` 配置。

**以管理员权限配置定时任务（PowerShell）：**
```powershell
Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd /d %CD% && setup_task.bat" -Verb RunAs

```

**或者在执行时动态指定时间并配置：**

```powershell
Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd /d C:\Users\13822\Desktop\wechat_moments_bot && set PUSH_HOUR=18 && set PUSH_MIN=44 && setup_task.bat" -Verb RunAs

```

---

## 🛠️ 常用操作命令

* **生成测试推送（检查配置是否成功）**：
```bash
python main.py test

```


* **立即手动触发运行**：

```powershell
    # Windows 示例：设定时间并立即运行
    $env:PUSH_HOUR=18; $env:PUSH_MIN=37; python main.py 
    ```
*   **查看运行日志**：
    ```bash
    ls logs/
    ```

---

## 📂 目录结构

```text
wechat_moments_bot/
├── config.py           ← 核心配置（含 RSS 源、筛选逻辑）
├── main.py             ← 程序入口
├── fetcher.py          ← 资讯抓取（RSS + 自动化筛选）
├── writer.py           ← AI 文案撰写（基于大模型评分）
├── pusher.py           ← 消息推送（Server酱接口）
├── setup_task.bat      ← Windows 任务一键安装
├── data/               ← 运行数据（含 seen_articles.json 去重记录）
└── logs/               ← 详细运行日志

```

---

## 📄 许可与商业合作

* **开源许可**：本项目基于 `Apache License 2.0`。
* **商业授权**：若用于商业产品或需法律保证，请参阅 `COMMERCIAL.md` 或联系 `13822124279@163.com`。

---

**把重复的抓取留给代码，把宝贵的思考留给未来。**

```

```