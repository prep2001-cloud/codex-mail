# NEXXBot 系统架构文档

## 1. 系统概述

NEXXBot 是一个基于多智能体协作的供应链 AI 解决方案，采用 Agentic AI 架构实现"去软件化"的目标。

## 2. 核心架构

### 2.1 NexxLM 核心大脑

NexxLM 是系统的中央编排器，负责：

- **意图识别** (Intent Recognition): 理解用户自然语言输入的真实意图
- **任务拆解** (Task Decomposition): 将复杂任务分解为可执行的原子步骤
- **智能体路由** (Agent Routing): 将任务分配给最合适的专门智能体
- **推理反思** (Reasoning & Reflection): 分析执行结果并优化决策

### 2.2 多智能体系统

#### Connexx（调度中枢）
- 角色：用户交互入口
- 职责：接收请求、意图识别、任务分发、结果聚合

#### Annexx（数据分析师）
- 角色：BI 数据分析专家
- 职责：
  - SQL 查询生成
  - 数据可视化
  - 异常检测
  - 根因分析
  - 优化建议

#### Ronnexx（运营助理）
- 角色：运营流程自动化
- 职责：
  - OCR 文档识别
  - 数据提取与验证
  - ASN 创建
  - 库存管理
  - WMS 系统集成

#### Visionexx（视觉质检员）
- 角色：AI 质量控制
- 职责：
  - 实时图像流处理
  - 缺陷检测
  - 标准样本对比
  - 自动剔除不合格品

#### Salexx（销售顾问）
- 角色：客户服务与销售
- 职责：
  - 24/7 多渠道响应
  - RAG 知识库检索
  - 报价计算
  - 个性化推荐

#### Robo-Agent（具身控制）
- 角色：机器人控制器
- 职责：
  - 自然语言到动作转译
  - 路径规划
  - 避障算法
  - 物理任务执行

### 2.3 共享组件

#### Memory Stream（记忆流）
- **短期记忆**: 当前会话上下文
- **长期记忆**: 历史决策案例、SOP 文档
- **情节记忆**: 特定事件记录
- **语义记忆**: 领域知识

#### Vector Store（向量存储）
- 基于 ChromaDB
- 支持 RAG（检索增强生成）
- 存储 SOP、案例研究、产品知识

#### Tool Registry（工具注册表）
- 数据工具：QueryDatabase, GenerateChart, CalculateMetrics
- WMS 工具：CreateASN, UpdateInventory, GetWarehouseInfo
- 通信工具：SendEmail, SendNotification

## 3. 数据流

```
用户输入
  ↓
NexxLM (意图识别)
  ↓
Connexx (任务分发)
  ↓
专门智能体 (执行任务)
  ↓
工具调用 (操作系统)
  ↓
Memory Stream (存储经验)
  ↓
结果返回用户
```

## 4. Agentic 工作流

每个智能体遵循标准工作流：

1. **感知** (Perceive): 理解输入和环境
2. **规划** (Plan): 制定执行计划
3. **执行** (Execute): 调用工具完成步骤
4. **推理** (Reason): 分析结果
5. **反思** (Reflect): 优化后续行动

## 5. 技术选型

### 后端
- FastAPI: 高性能异步 Web 框架
- Pydantic: 数据验证
- SQLAlchemy: ORM

### AI 框架
- LangChain: 智能体编排
- OpenAI GPT-4: 核心推理引擎
- Sentence Transformers: 文本嵌入

### 存储
- ChromaDB: 向量数据库
- PostgreSQL: 关系数据库
- Redis: 缓存

### 计算机视觉
- OpenCV: 图像处理
- YOLO: 目标检测
- Tesseract: OCR

## 6. 安全性

- API Key 管理
- 数据隐私保护
- 权限控制
- 审计日志

## 7. 扩展性

- 横向扩展：多实例部署
- 纵向扩展：GPU 加速
- 模块化设计：易于添加新智能体
- 插件系统：自定义工具

## 8. 监控与日志

- 结构化日志
- 性能指标
- 错误追踪
- 用户行为分析
