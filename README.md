# NEXXBot 供应链 AI 解决方案

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **多智能体协作的供应链 AI 系统 - 从"人操作软件管理仓库"到"人指挥 AI，AI 管理仓库"**

## 🎯 核心理念

NEXXBot 采用 **Agentic AI** 架构，实现"去软件化"（De-software-ization）：
- ❌ 传统方式：人 → 学习软件 → 点击菜单 → 查看报表 → 手动分析 → 执行操作
- ✅ NEXXBot：人 → 提出需求 → AI自动分析 → AI执行操作 → 获得结果

## 🚀 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/prep2001-cloud/codex-mail.git
cd codex-mail

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
cp .env.example .env
# 编辑 .env 文件，设置 OPENAI_API_KEY

# 4. 启动服务
python main.py

# 5. 访问 API 文档
# http://localhost:8000/docs
```

## 📖 系统架构

### 多智能体系统

| 智能体 | 角色 | 核心能力 |
|--------|------|----------|
| **Connexx** | 调度中枢 | 用户交互入口，任务分发 |
| **Annexx** | 数据分析师 | BI分析、可视化、异常检测 |
| **Ronnexx** | 运营助理 | OCR、文档处理、WMS操作 |
| **Visionexx** | 视觉质检员 | 图像识别、缺陷检测 |
| **Salexx** | 销售顾问 | 客户咨询、报价、RAG检索 |
| **Robo-Agent** | 具身控制 | 机器人控制、路径规划 |

## 💡 使用示例

```bash
# 示例 1: 数据分析
curl -X POST "http://localhost:8000/task" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "统计本月设备耗电量，对比每层能耗差异，并分析原因"}'

# 示例 2: 运营自动化
curl -X POST "http://localhost:8000/examples/operations"

# 示例 3: 客户服务
curl -X POST "http://localhost:8000/examples/sales"
```

## 🛠️ 技术栈

- **LangChain**: 智能体编排
- **FastAPI**: 后端 API 服务
- **ChromaDB**: 向量数据库（RAG）
- **OpenAI GPT-4**: 核心推理引擎

## 📁 项目结构

```
nexxbot/
├── core/          # 核心模块 (NexxLM大脑)
├── agents/        # 多智能体系统
├── memory/        # 记忆系统
├── tools/         # 工具箱
└── api/           # FastAPI接口
```

## 📄 许可证

MIT License

---

**NEXXBot - 让 AI 成为你的供应链专家团队 🚀**
