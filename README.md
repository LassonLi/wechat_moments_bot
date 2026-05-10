
---

# 🚀 WeChat Moments Bot — 朋友圈技术人设智造家

**「让每一条朋友圈，都在为你积累职业信用与行业声望。」**

在这个信息过载的时代，持续且高质量的专业输出是构建**个人品牌**最快的路径。`WeChat Moments Bot` 专为追求卓越的开发者与金融科技从业者设计，自动化抓取全球顶尖 **AI 技术干货**与 **HSBC（汇丰）财讯**，通过大模型深度理解并撰写极具洞见的配文，助你轻松打造专业、前沿、有深度的朋友圈人设。

---

### 🌟 为什么选择这个工具？

* **人设自动化**：告别“不知道发什么”，AI 每日为你精选高含金量资讯，确保你的朋友圈永远走在技术前沿。
* **深度洞察力**：依托 Anthropic/QWEN 的强大总结能力，配文不再是简单的转发，而是带有“专家视角”的点评。
* **极致省时**：从抓取、筛选、总结到推送，全流程自动化。你只需在 Server酱收到提醒后，顺手完成最后一次快意的转发。
* **精准双赛道**：深度锁定 **AI 浪潮**与 **HSBC 全球金融动态**，完美契合 FinTech 复合型人才的定位。

---

## 📁 架构概览

```
wechat_moments_bot/
├── config.py           ← 逻辑中枢（支持环境变量，安全合规）
├── main.py             ← 指挥官：主程序入口
├── fetcher.py          ← 侦察兵：全球 RSS 实时抓取
├── writer.py           ← 智囊团：AI 驱动的配文生成与质量评估
├── pusher.py           ← 传递者：通过 Server酱 直达微信
├── setup_task.bat      ← 自动化：Windows 定时任务一键配置
├── requirements.txt    ← 运行基石
├── data/               ← 记忆库：文章去重记录
└── logs/               ← 运行轨迹：详尽日志

```

---

## ⚡ 快速启程

**运行环境：** Python 3.13+

### 1. 搭建运行环境

建议使用虚拟环境以保持系统纯净：

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```

### 2. 配置你的“数字大脑” (API Keys)

为了保障安全，建议通过环境变量注入 Key（避免源码泄露）：

* `ANTHROPIC_API_KEY`: ANTHROPIC模型赋予 AI 思考能力。
* `SERVERCHAN_SENDKEY`: 连接微信的通道。
* `DASHSCOPE_API_KEY`: 中国制造qwen模型具有大国特色。

> **小贴士**：在 Windows 中，可以通过“系统属性 -> 环境变量”持久化设置这些 Key，重启终端即可生效。

### 3. 灵感初探（测试运行）

```bash
python main.py test

```

*当手机响起 Server酱 的推送铃声时，你的朋友圈进化之旅已正式开启。*

---

## ⏰ 生产力释放：自动化定时任务

无需手动干预，让脚本配合你的作息。

1. **调整节奏**：在 `config.py` 中修改 `SCHEDULE`（例如设为早晨 8:30 或晚间 20:00）。
2. **一键部署**：右键以**管理员身份**运行 `setup_task.bat`。
3. **静候佳音**：脚本将化身你的虚拟助手，每天准时献上精心挑选的行业盛宴。

---

## 🛠️ 进阶自定义

* **定制品味**：修改 `AI_CRITERIA` 和 `HSBC_CRITERIA`，调教 AI 对文章的口味。
* **扩展信源**：在 `RSS_SOURCES` 中加入你钟爱的技术博客或媒体。
* **人设微调**：在 `writer.py` 中调整 Prompt，让 AI 的语气更符合你的真实性格（或是冷峻专家，或是幽默极客）。

---

## 📄 许可与商业价值

* **开源基因**：采用 `Apache License 2.0` 协议，开放、包容、受保护。
* **商业授权**：如果您希望将此方案集成到商业产品或需要定制化开发支持，请联系：`13822124279@163.com` 获取 `COMMERCIAL.md` 说明。

---

**把重复的抓取留给代码，把宝贵的思考留给未来。**
立即开始你的朋友圈**专业化**转型之路！ 🚀