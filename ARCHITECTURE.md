# 小红书 AI 运营平台 — 完整架构与演进设计

> 基于 `Spider_XHS`（小红书 API 封装）构建的 AI 数据分析 SaaS 平台。
> 覆盖热点雷达、爆文拆解、评论洞察、AI 创作、自动发布、竞品监控、达人库、关键词库、内容知识库、AI 运营 Agent。

---

## 目录

- [一、总体架构](#一总体架构)
- [二、MVP 与最终版两阶段策略](#二mvp-与最终版两阶段策略)
- [三、技术栈总结](#三技术栈总结)
- [四、Spring Boot 后端详细设计](#四spring-boot-后端详细设计)
- [五、Python AI 服务详细设计](#五python-ai-服务详细设计)
- [六、AI Orchestrator 编排层（核心新增）](#六ai-orchestrator-编排层核心新增)
- [七、数据流设计：全异步通道](#七数据流设计全异步通道)
- [八、基础设施 Provider 体系（平台化）](#八基础设施-provider-体系平台化)
- [九、功能模块映射](#九功能模块映射)
- [十、数据库设计](#十数据库设计)
- [十一、核心交互流程](#十一核心交互流程)
- [十二、模块完成状态追踪](#十二模块完成状态追踪)

---

## 一、总体架构

```
                         Vue3 + Naive UI
                      (前台: 仿小红书 / 后台: 管理面板)
                              │
                          REST/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│            Spring Boot Application Server (业务服务层)                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐  │
│  │ 用户中心  │ │ 权限认证  │ │ 数据管理  │ │ 发布流程  │ │ Dashboard   │  │
│  │         │ │ JWT     │ │ CRUD    │ │ Publish  │ │ 看板/报表    │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────┘  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────────────────┐ │
│  │ 任务调度  │ │ 通知    │ │ API管理  │ │ AI Client (调用编排层)   │ │
│  │(XXL-Job)│ │(Notif)  │ │(API Key)│ │                          │ │
│  └─────────┘ └─────────┘ └─────────┘ └──────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/Task (仅创建任务、查询状态、查询数据库)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│           AI Orchestrator（AI 编排层 — 新增）                        │
│                                                                     │
│  职责: 接收 AI 任务 → 路由到正确 Pipeline → 编排 Agent/Tools/Workflow │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Task Router        → 根据 type 路由到对应 Handler            │  │
│  │  Pipeline Manager   → 管理 Workflow 生命周期                   │  │
│  │  Agent Factory      → 创建 Planner → Executor → Reflection   │  │
│  │  Tool Router        → Agent 统一调用 Tools                     │  │
│  │  Event Bus          → 事件发布/订阅，驱动异步流程               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
               ┌─────────────┼──────────────┐
               ▼             ▼              ▼
┌──────────────────┐ ┌────────────┐ ┌──────────────────┐
│    Agent 层       │ │ Workflow   │ │    Tools 工具层    │
│  Planner          │ │ LangGraph  │ │  search_note     │
│  Executor         │ │ publish    │ │  get_comments    │
│  Reflection       │ │ trend      │ │  publish_note    │
│  Memory(短期/长期) │ │ report     │ │  analyze etc.    │
└──────────────────┘ └────────────┘ └──────────────────┘
               │             │              │
               └─────────────┼──────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│            Infrastructure Providers (平台化基础设施)                  │
│                                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────┐  │
│  │ 数据源 Provider │ │ LLM Provider  │ │  AI 能力      │ │ 存储     │  │
│  │ xiaohongshu   │ │ openai       │ │ PaddleOCR    │ │ MySQL    │  │
│  │ douyin(预留)  │ │ deepseek     │ │ CLIP/SigLIP  │ │ Redis    │  │
│  │ bilibili(预留) │ │ qwen         │ │  Embedding    │ │ Qdrant   │  │
│  │               │ │ claude       │ │              │ │ ES       │  │
│  │               │ │ gemini       │ │              │ │ MinIO    │  │
│  └──────────────┘ └────────────┘ └──────────────┘ └──────────┘  │
│                                                                     │
│  所有 Provider 实现统一接口:                                         │
│  - IDataProvider: search_notes(), get_comments(), publish_note()   │
│  - ILLMProvider: chat(), generate_embedding()                      │
│  - IOcrProvider: recognize_text()                                  │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  数据层 (Data Layer)                                 │
│  MySQL(业务)  Redis(缓存/限流)  ES(搜索)  Qdrant(向量)  MinIO(文件)  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 二、MVP 与最终版两阶段策略

### Phase 1 — MVP（2~4 周跑通闭环）

**核心目标**: 采集 → 分析 → AI 创作 → 发布

#### Spring Boot 模块（适度精简）

```
backend/
├── common/          # 工具、统一返回、全局异常
├── system/          # 用户、JWT、Spring Security、RBAC
├── crawler/         # 凭据管理 + 任务管理
├── analysis/        # 热点/爆文/评论 查询接口
├── publish/         # 笔记发布、草稿管理
├── ai-client/       # FastAPI 调用封装
├── dashboard/       # 基础看板（MVP 需要数据展示）
└── gateway/         # 路由、跨域、WebSocket、安全
```

#### Python AI 服务（MVP 精简结构）

```
python-agent/
├── main.py
├── config.py
├── api/routers/              # xhs_api, agent_chat, data_clean
├── application/services/     # 热点、爆文、评论、创作
├── domain/analyzers/         # 趋势、分类、情绪分析
├── infrastructure/
│   ├── spider/spider_xhs.py  # Spider_XHS 桥接
│   └── llm/                  # LLM 调用
├── tools/                    # Agent 工具
├── orchestrator/             # ★ MVP 也要有，路由 Task + 编排
├── crawler/                  # ★ MVP 独立（Cookie/限流/调度）
└── models/
```

#### 数据层

- ✅ MySQL — 用户、凭据、任务、笔记
- ✅ Redis — 缓存、Token 黑名单、频控
- ❌ ES / Qdrant / MinIO → MySQL JSON 字段替代，后续迁移

#### 前端

- **Vben Admin v5** 一个后台即可：登录 / Dashboard / 凭据管理 / 任务管理 / 数据分析

**MVP 范围**: 登录 → 凭据管理 → 创建爬取任务 → 查看笔记 → AI 分析评论 → AI 创作 → 手动发布

---

### Phase 2 — 平台化（MVP 稳定后迭代）

| 新增内容 | 优先级 | 说明 |
|---------|--------|------|
| Qdrant + RAG 知识库 | P0 | 向量检索替代 MySQL 模糊匹配 |
| Elasticsearch 全文检索 | P0 | 百万级笔记搜索 |
| MinIO 文件存储 | P0 | 图片/视频/OCR 文件 |
| LangGraph Workflow | P0 | 多步骤自动化流程 |
| Prompt 管理中心 | P0 | 版本 / A/B Test / 多模型 |
| 多模型 Provider | P1 | 不再只依赖单一 LLM |
| Agent Reflection | P1 | 反思机制提升 Agent 质量 |
| 前台 Nuxt3 页面 | P1 | 仿小红书瀑布流 |
| Dashboard 大屏 | P1 | 独立模块，WebSocket 实时 |
| 事件总线 events/ | P2 | 解耦模块间通信 |
| 插件系统 plugins/ | P2 | 动态加载 Skill |
| MCP Server | P2 | 对外暴露 MCP 协议 |
| RabbitMQ | P2 | 异步消息解耦 |
| XXL-Job 调度中心 | P2 | 替代 @Scheduled |
| Docker Compose / K8s | P2 | 生产部署 |

---

## 三、技术栈总结

| 层级 | 技术 |
|------|------|
| 前端 - 前台 (用户端) | Nuxt 3 + TailwindCSS + Shadcn Vue（Phase 2） |
| 前端 - 后台 (管理端) | Vben Admin v5 |
| 业务后端 | Spring Boot 3.4.x + MyBatis-Plus + Spring Security + JWT + RBAC |
| AI 编排层 | FastAPI 0.115.x + PydanticAI + LangGraph |
| 调度中心 | XXL-Job（Phase 2，MVP 用 @Scheduled） |
| 消息队列 | RabbitMQ（Phase 2，MVP 用 Redis Stream） |
| 缓存 / 限流 | Redis |
| 关系数据库 | MySQL 8 |
| 全文搜索 | Elasticsearch（Phase 2） |
| 向量数据库 | Qdrant（Phase 2） |
| 对象存储 | MinIO（Phase 2） |
| OCR | PaddleOCR |
| 图像理解 | CLIP / SigLIP |
| 数据分析 | DuckDB + Pandas + Polars |

---

## 四、Spring Boot 后端详细设计

### 命名说明

本层为 **Application Server（业务服务层）**，不是 API Gateway。
真正的 Gateway（认证/路由/限流）仅作为一个子模块存在。

### MVP 模块

```
backend/
├── pom.xml
├── common/                     # 公共模块
│   └── src/main/java/com/xhs/common/
│       ├── result/Result.java
│       ├── exception/BusinessException.java
│       ├── exception/GlobalExceptionHandler.java
│       ├── constant/ApiConstant.java
│       └── util/
├── system/                     # 用户 + 认证 + 权限
│   └── src/main/java/com/xhs/system/
│       ├── controller/AuthController.java
│       ├── controller/UserController.java
│       ├── service/UserService.java
│       ├── security/
│       │   ├── JwtTokenProvider.java
│       │   ├── JwtAuthenticationFilter.java
│       │   └── UserDetailsServiceImpl.java
│       ├── model/entity/User.java
│       ├── model/dto/LoginRequest.java
│       ├── model/dto/RegisterRequest.java
│       └── mapper/UserMapper.java
├── crawler/                    # 采集中心
│   └── src/main/java/com/xhs/crawler/
│       ├── controller/CredentialController.java
│       ├── controller/TaskController.java
│       ├── service/CredentialService.java
│       ├── service/TaskService.java
│       ├── model/entity/XhsCredential.java
│       ├── model/entity/Task.java
│       ├── model/dto/TaskCreateRequest.java
│       └── mapper/
├── analysis/                   # 数据分析
│   └── src/main/java/com/xhs/analysis/
│       ├── controller/
│       │   ├── HotRadarController.java
│       │   ├── ArticleAnalysisController.java
│       │   └── CommentInsightController.java
│       └── service/AnalysisService.java
├── publish/                    # 发布管理
│   └── src/main/java/com/xhs/publish/
│       ├── controller/PublishController.java
│       └── service/PublishService.java
├── dashboard/                  # 数据看板（MVP 要有基础版本）
│   └── src/main/java/com/xhs/dashboard/
│       ├── controller/DashboardController.java
│       └── service/DashboardService.java
├── ai-client/                  # AI 编排层客户端
│   └── src/main/java/com/xhs/aiclient/
│       ├── client/AiOrchestratorClient.java   # 调用 Orchestrator
│       ├── config/RestClientConfig.java
│       └── dto/
└── gateway/                    # 网关（路由/跨域/WebSocket/安全）
    └── src/main/java/com/xhs/gateway/
        ├── config/
        │   ├── CorsConfig.java
        │   ├── WebSocketConfig.java
        │   └── SecurityConfig.java
        └── websocket/TaskLogWebSocketHandler.java
```

### Phase 2 新增

```
backend/ 新增:
├── notification/    # 通知（站内信、邮件、Webhook）
├── job/             # XXL-Job 调度任务
├── monitor/         # 竞品监控
└── project/         # 项目管理（多租户基础）
```

---

## 五、Python AI 服务详细设计

### DDD 分层

```
python-agent/
│
├── main.py                           # FastAPI 入口
├── config.py                         # 配置
├── requirements.txt
│
├── api/                              # 路由层 — 仅做请求/响应转换
│   ├── dependencies.py               # 依赖注入（认证、DB session）
│   └── routers/
│       ├── xhs_api.py                # 小红书数据代理
│       ├── agent_chat.py             # AI 智能体对话
│       ├── agent_pipeline.py         # 运营全链路
│       ├── rag.py                    # RAG 检索
│       └── data_clean.py             # 数据清洗
│
├── application/                      # 应用服务层 — 编排业务
│   ├── services/
│   │   ├── hot_radar_service.py
│   │   ├── article_analysis_service.py
│   │   ├── comment_insight_service.py
│   │   ├── content_writer_service.py
│   │   ├── competitor_monitor_service.py
│   │   └── kol_analysis_service.py
│   └── repositories/                 # ★ 统一数据访问
│       ├── note_repository.py
│       ├── comment_repository.py
│       └── task_repository.py
│
├── domain/                           # 领域层 — 核心业务逻辑
│   ├── entities/
│   │   ├── note.py
│   │   ├── comment.py
│   │   └── user_profile.py
│   ├── analyzers/                    # 纯算法，无外部依赖
│   │   ├── trend_analyzer.py
│   │   ├── comment_classifier.py
│   │   ├── topic_extractor.py
│   │   └── sentiment_analyzer.py
│   └── services/
│       ├── note_scorer.py
│       └── kol_scorer.py
│
├── orchestrator/                     # ★ AI 编排层（核心）
│   ├── __init__.py
│   ├── router.py                     # Task 路由：type → handler
│   ├── pipeline_manager.py           # Pipeline 生命周期管理
│   └── task_dispatcher.py            # 任务分发 + 状态回调
│
├── agent/                            # 智能体层
│   ├── __init__.py
│   ├── factory.py                    # Agent 工厂
│   ├── planner.py                    # 任务规划器
│   ├── executor.py                   # 任务执行器
│   ├── reflection.py                 # ★ 反思机制
│   └── memory/
│       ├── base.py
│       ├── buffer_memory.py          # 短期记忆
│       └── vector_memory.py          # 长期记忆（Phase 2）
│
├── workflow/                         # LangGraph 工作流
│   ├── __init__.py
│   ├── executor.py                   # 工作流引擎
│   ├── publish_flow.py
│   ├── trend_flow.py
│   ├── report_flow.py
│   ├── review_flow.py
│   └── nodes/
│       ├── collect_node.py
│       ├── analyze_node.py
│       ├── generate_node.py
│       ├── review_node.py
│       └── notify_node.py
│
├── tools/                            # Agent 工具层
│   ├── __init__.py
│   ├── base_tool.py
│   ├── search_note_tool.py
│   ├── get_note_detail_tool.py
│   ├── get_comments_tool.py
│   ├── search_user_tool.py
│   ├── publish_note_tool.py
│   ├── analyze_sentiment_tool.py
│   ├── analyze_trend_tool.py
│   └── data_clean_tool.py
│
├── prompts/                          # Prompt 管理中心
│   ├── __init__.py
│   ├── manager.py                    # 管理器（CRUD + 版本）
│   ├── templates/
│   │   ├── article_analysis.yaml
│   │   ├── sentiment_analysis.yaml
│   │   ├── content_writer.yaml
│   │   ├── title_generator.yaml
│   │   └── topic_recommend.yaml
│   └── evaluation/
│       └── evaluator.py              # A/B Test 评估（Phase 2）
│
├── events/                           # 事件总线（Phase 2）
│   ├── __init__.py
│   ├── bus.py
│   ├── topic_event.py
│   ├── publish_event.py
│   └── comment_event.py
│
├── providers/                        # ★ 基础设施 Provider
│   ├── __init__.py
│   ├── data/                         # 数据源 Provider
│   │   ├── base.py                   # IDataProvider 接口
│   │   ├── xiaohongshu.py            # 小红书实现
│   │   ├── douyin.py                 # 预留
│   │   └── bilibili.py               # 预留
│   ├── llm/                          # LLM Provider
│   │   ├── base.py                   # ILLMProvider 接口
│   │   ├── openai_provider.py
│   │   ├── deepseek_provider.py
│   │   ├── qwen_provider.py
│   │   ├── claude_provider.py
│   │   └── gemini_provider.py
│   ├── ocr/
│   │   ├── base.py
│   │   └── paddle_ocr.py
│   └── vector/
│       ├── base.py
│       └── qdrant_client.py
│
├── crawler/                          # ★ 数据采集中心（MVP 独立）
│   ├── __init__.py
│   ├── account_manager.py
│   ├── cookie_manager.py
│   ├── proxy_manager.py
│   ├── scheduler.py
│   ├── limiter.py
│   ├── retry.py
│   └── incremental.py
│
├── rag/                              # RAG 检索系统（Phase 2）
│   ├── __init__.py
│   ├── retriever.py
│   ├── embedder.py
│   ├── reranker.py
│   └── knowledge_base.py
│
├── plugins/                          # 插件系统（Phase 2）
│   ├── __init__.py
│   └── loader.py
│
├── mcp/                              # MCP Server（Phase 2）
│   ├── __init__.py
│   └── xhs_mcp_server.py
│
└── models/
    └── schemas.py
```

### 职责边界（解决 Skills vs Application 重复的问题）

| 目录 | 职责 | 示例 |
|------|------|------|
| `application/services/` | 编排流程、调用 domain + infrastructure | `HotRadarService` 调用 `TrendAnalyzer` + `spider` + `LLM` |
| `domain/analyzers/` | 纯算法、无 I/O、可测试 | `TrendAnalyzer` 只算趋势分数，不调 API |
| `tools/` | Agent 可调用的 LangChain 工具封装 | `SearchNoteTool` 封装搜索逻辑给 Agent |
| `prompts/templates/` | Prompt 模板定义 | `article_analysis.yaml` 是纯文本模板 |
| `orchestrator/` | 任务路由 + 编排 | 收到分析任务 → 路由到正确的 Service |

---

## 六、AI Orchestrator 编排层（核心新增）

### 为什么要加这一层

没有编排层时，SpringBoot 直接调用 FastAPI 各个路由，导致：
1. 每次新增 AI 能力都要改 SpringBoot 代码
2. 无法统一管理 Task 生命周期
3. 无法做任务路由、重试、排队

有了编排层后：

```
SpringBoot 只知道:
  创建 Task → Orchestrator 接收 → 路由到 Handler → 完成 → 回调状态

编排层内部:
  Task Router → Pipeline Manager → Agent / Workflow / Tools
```

### 编排层核心代码结构

```python
# orchestrator/router.py
class TaskRouter:
    """根据 task.type 路由到对应的 Handler"""
    
    handlers = {
        "hot_radar": HotRadarHandler,
        "article_analysis": ArticleAnalysisHandler,
        "comment_insight": CommentInsightHandler,
        "content_write": ContentWriteHandler,
        "pipeline": PipelineHandler,
        "data_clean": DataCleanHandler,
    }
    
    async def route(self, task: Task):
        handler = self.handlers[task.type]
        return await handler.execute(task)

# orchestrator/pipeline_manager.py
class PipelineManager:
    """管理 Workflow 生命周期"""
    
    async def execute(self, pipeline_id: str, flow_type: str):
        workflow = self.create_workflow(flow_type)
        # LangGraph 执行
        result = await workflow.run()
        # 回调 SpringBoot 更新状态
        await self.callback(pipeline_id, result)
```

### 数据流（全异步）

```
用户点击分析
  → SpringBoot: 创建 Task(status=PENDING)
  → Orchestrator: 接收 Task
  → TaskRouter: 路由到对应 Handler
  → Pipeline Manager: 创建工作流 / 启动 Agent
  → 每步: 更新 Task progress + WebSocket 推送日志
  → 完成: Task(status=SUCCESS), 结果写入 MySQL
  → 前端: 从 MySQL 读取结果，无需等待 HTTP 响应
```

---

## 七、数据流设计：全异步通道

### 关键原则

> **所有采集都是异步的，SpringBoot 不直接等待 Spider 返回数据**

```
SpringBoot 请求 → 创建 Task (status=PENDING)
                 ↓
            Orchestrator 接收
                 ↓
            Spider / Agent / Workflow 执行
                 ↓
            写入 MySQL (result 字段)
                 ↓
            SpringBoot 查询 MySQL 返回
```

### MVP 通道（Redis Stream）

```python
# SpringBoot → Redis → Python
redis.stream().add("task:queue", task_data)

# Python 消费
while True:
    task = redis.stream().read("task:queue")
    result = await orchestrator.route(task)
    # 结果写入 MySQL
    mysql.update(task.id, result)
    # 通知 SpringBoot
    redis.publish("task:notify", task.id)
```

### Phase 2 通道（RabbitMQ）

```python
# SpringBoot → RabbitMQ → Python
rabbitTemplate.convertAndSend("ai.task", taskData)

# Python 消费 (aio-pika)
@router.on_message
async def handle_task(message):
    task = json.loads(message.body)
    result = await orchestrator.route(task)
    # 结果回写
    message.ack()
```

---

## 八、基础设施 Provider 体系（平台化）

### 数据源 Provider 接口

```python
# providers/data/base.py
class IDataProvider(ABC):
    """所有数据平台实现此接口"""
    
    @abstractmethod
    async def search_notes(self, keyword: str, **kwargs) -> list[Note]:
        pass
    
    @abstractmethod
    async def get_comments(self, note_id: str, **kwargs) -> list[Comment]:
        pass
    
    @abstractmethod
    async def get_user_info(self, user_id: str) -> UserProfile:
        pass
    
    @abstractmethod
    async def publish_note(self, content: dict) -> PublishResult:
        pass

# providers/data/xiaohongshu.py
class XiaoHongShuProvider(IDataProvider):
    """小红书实现 — 内部调用 Spider_XHS"""
    
    async def search_notes(self, keyword: str, **kwargs):
        # 调用 Spider_XHS
        ...
```

### 业务层不感知数据源

```python
# application/services/hot_radar_service.py
class HotRadarService:
    def __init__(self, data_provider: IDataProvider):
        self.data_provider = data_provider  # 注入抽象接口
    
    async def analyze(self, keyword: str):
        notes = await self.data_provider.search_notes(keyword)
        # 业务逻辑，不关心数据从哪来
```

### LLM Provider 接口

```python
# providers/llm/base.py
class ILLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        pass

# 切换模型只需改配置
# config.py
LLM_PROVIDER = "openai"  # 或 "claude" / "qwen" / "deepseek"
```

---

## 九、功能模块映射

| 模块 | SpringBoot 负责 | Python AI 负责 |
|------|----------------|----------------|
| 🔥 热点雷达 | 任务调度、数据存储、查询接口 | 趋势预测、关键词聚类、热点检测 |
| 🔥 爆文拆解 | 爆文管理、结果展示 | 标题分析、OCR、图片分类、结构分析 |
| 🔥 评论洞察 | 评论采集、缓存 | 情绪分析、主题聚类、痛点提取 |
| 🔥 AI 创作 | 发布流程、草稿管理 | 标题生成、正文生成、标签推荐 |
| 🔥 自动发布 | 发布 API、定时任务、审核 | 发布时间推荐、策略优化 |
| ⭐ 竞品监控 | 竞品管理 | 内容差异分析、增长趋势 |
| ⭐ 达人库 | 达人 CRUD | 达人画像、合作评分 |
| ⭐ 关键词库 | 搜索管理 | TF-IDF、Embedding、长尾词 |
| ⭐ 内容知识库 | 文档管理、权限 | RAG、Embedding、知识检索 |
| 🔥 AI Agent | Workflow 编排、调度 | Planner/Executor/Reflection + Tools |

---

## 十、数据库设计

```sql
-- 用户表
CREATE TABLE `user` (
  `id`          BIGINT AUTO_INCREMENT PRIMARY KEY,
  `username`    VARCHAR(50) NOT NULL UNIQUE,
  `password`    VARCHAR(255) NOT NULL,          -- BCrypt
  `nickname`    VARCHAR(50),
  `avatar`      VARCHAR(500),
  `email`       VARCHAR(100),
  `role`        VARCHAR(20) DEFAULT 'USER',     -- USER / ADMIN / API
  `status`      TINYINT DEFAULT 1,
  `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 小红书凭据表
CREATE TABLE `xhs_credential` (
  `id`          BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`     BIGINT NOT NULL,
  `name`        VARCHAR(50) NOT NULL,
  `cookies`     TEXT NOT NULL,                 -- AES 加密
  `is_valid`    TINYINT DEFAULT 1,
  `expires_at`  DATETIME,
  `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_id (`user_id`)
);

-- 异步任务表
CREATE TABLE `task` (
  `id`            BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`       BIGINT NOT NULL,
  `type`          VARCHAR(30) NOT NULL,         -- NOTE_COLLECT / ANALYZE / PIPELINE / DATA_CLEAN
  `status`        VARCHAR(20) DEFAULT 'PENDING', -- PENDING / RUNNING / SUCCESS / FAILED / CANCELLED
  `params`        JSON,
  `result`        JSON,
  `progress`      INT DEFAULT 0,
  `error_message` TEXT,
  `credential_id` BIGINT,
  `started_at`    DATETIME,
  `finished_at`   DATETIME,
  `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_status (`user_id`, `status`),
  INDEX idx_type_status (`type`, `status`)
);

-- AI 对话记录表
CREATE TABLE `agent_conversation` (
  `id`          BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`     BIGINT NOT NULL,
  `title`       VARCHAR(200),
  `messages`    JSON NOT NULL,
  `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_id (`user_id`)
);

-- 知识库文档表（Phase 2 配合 Qdrant）
CREATE TABLE `knowledge_doc` (
  `id`          BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`     BIGINT NOT NULL,
  `title`       VARCHAR(200),
  `content`     TEXT,
  `tags`        JSON,
  `source_url`  VARCHAR(500),
  `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_tags (`user_id`)
);

-- 项目表（Phase 2 多租户基础）
CREATE TABLE `project` (
  `id`          BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`     BIGINT NOT NULL,
  `name`        VARCHAR(100) NOT NULL,
  `description` TEXT,
  `config`      JSON,
  `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_id (`user_id`)
);
```

---

## 十一、核心交互流程

### 1. 同步查询（手动触发，小数据量）
```
前端请求 → SpringBoot Controller → PythonApiClient(HTTP) → FastAPI
                                                          → Spider_XHS
         ← 返回 JSON （走 Redis 缓存）
```

### 2. 异步采集 + 分析（大数据量，标准通道）
```
用户创建任务
  → SpringBoot: INSERT task(status=PENDING)
  → Redis Stream: push task
  → Python Orchestrator: pop task → 路由到 Handler
     → Spider 采集 / LLM 分析
     → 结果写入 MySQL (task.result)
     → Redis Pub: task:{id}:completed
  → SpringBoot: 收到通知 → WebSocket 推前端
  → 前端: 查询 MySQL 获取结果
```

### 3. AI Agent 对话（SSE 流式）
```
用户发送消息
  → SpringBoot: POST /api/agent/chat
  → PythonApiClient: POST /api/v1/agent/chat (SSE)
  → Orchestrator → Agent Factory → Planner → Executor → Tools
  → SSE stream → 前端实时展示
```

### 4. AI 运营全链路（LangGraph Workflow）
```
配置 Pipeline（前端）
  → SpringBoot: INSERT task(type=pipeline)
  → Orchestrator → Pipeline Manager → Workflow Executor
  → nodes: collect → analyze → generate → review → publish → notify
  → 每步: 更新 progress + WebSocket 日志
  → 完成 → 复盘报告
```

---

## 十二、模块完成状态追踪

### 当前状态总览

| 层级 | 模块 | 状态 | 备注 |
|------|------|------|------|
| 基础设施 | MySQL 数据库 | ✅ 已完成 | Docker xhs-mysql 运行中, 5 tables |
| 基础设施 | Redis 缓存 | ✅ 已完成 | Docker xhs-redis 运行中, v7.4.9 |
| 基础设施 | RabbitMQ | ✅ 已完成 | Docker xhs-rabbitmq 运行中 |
| 基础设施 | Elasticsearch | ✅ 已完成 | Docker xhs-elasticsearch 运行中, v8.12 |
| 基础设施 | Qdrant | ✅ 已完成 | Docker xhs-qdrant 运行中, v1.9 |
| 基础设施 | MinIO | ✅ 已完成 | Docker xhs-minio 运行中 |

### Spring Boot 后端

| 模块 | 子模块 | 状态 | 负责人 | 预计完成 |
|------|--------|------|--------|---------|
| common | 统一返回 Result | ✅ 已完成 | | |
| common | 全局异常处理 | ✅ 已完成 | | |
| common | 工具类 | ✅ 已完成 | | |
| system | 用户注册/登录 | ✅ 已完成 | | |
| system | JWT 生成/验证 | ✅ 已完成 | | |
| system | Spring Security 配置 | ✅ 已完成 | | |
| system | 用户 CRUD | ✅ 已完成 | | |
| crawler | 凭据管理 CRUD | ✅ 已完成 | | |
| crawler | 任务创建/查询/取消 | ✅ 已完成 | | |
| analysis | 热点雷达查询接口 | ✅ 已完成 | | |
| analysis | 爆文拆解接口 | ✅ 已完成 | | |
| analysis | 评论洞察接口 | ✅ 已完成 | | |
| publish | 笔记发布接口 | ✅ 已完成 | | |
| publish | 定时发布 | ✅ 已完成 | | |
| dashboard | 基础看板 | ✅ 已完成 | | |
| ai-client | Orchestrator Client | ✅ 已完成 | | |
| gateway | 跨域/WebSocket/安全 | ✅ 已完成 | | |

### Python AI 服务

| 模块 | 子模块 | 状态 | 负责人 | 预计完成 |
|------|--------|------|--------|---------|
| api | FastAPI 入口 + 配置 | ✅ 已完成 | | |
| api | xhs_api 路由 | ✅ 已完成 | search/detail/comments/hot-topics |
| api | agent_chat 路由 | ✅ 已完成 | SSE 流式 + 意图识别 |
| api | agent_pipeline 路由 | ✅ 已完成 | Workflow 触发 |
| api | analysis 路由 | ✅ 已完成 | 热度分析 + 爆文拆解 |
| api | data_clean 路由 | ✅ 已完成 | |
| orchestrator | Task Router | ✅ 已完成 | |
| orchestrator | Pipeline Manager | ✅ 已完成 | |
| orchestrator | Task Dispatcher | ✅ 已完成 | 调用真实 Service |
| providers | IDataProvider 接口 | ✅ 已完成 | |
| providers | XiaoHongShu Provider | ✅ 已完成 | XhsBridge 桥接 Spider_XHS |
| providers | LLM Provider 接口 | 🚧 开发中 | |
| providers | OpenAI Provider | ❌ 未开始 | |
| providers | 其他模型 Provider | ⏳ Phase 2 | |
| providers | PaddleOCR | ❌ 未开始 | |
| providers | Qdrant 适配 | ❌ 未开始 | |
| application | 热点雷达服务 | ✅ 已完成 | 调用 XhsBridge + TrendAnalyzer |
| application | 爆文拆解服务 | ✅ 已完成 | 标题/互动/评论分析 |
| application | 评论洞察服务 | ✅ 已完成 | |
| application | AI 创作服务 | ❌ 未开始 | |
| application | 竞品监控服务 | ❌ 未开始 | |
| application | Repositories | ❌ 未开始 | |
| domain | TrendAnalyzer | ✅ 已完成 | 热度分/趋势方向/聚类 |
| domain | ArticleAnalyzer | ✅ 已完成 | 标题评分/互动率 |
| domain | CommentClassifier | ❌ 未开始 | |
| domain | SentimentAnalyzer | ❌ 未开始 | |
| domain | TopicExtractor | ❌ 未开始 | |
| tools | search_note_tool | ❌ 未开始 | |
| tools | get_comments_tool | ❌ 未开始 | |
| tools | publish_note_tool | ❌ 未开始 | |
| tools | analyze_sentiment_tool | ❌ 未开始 | |
| tools | data_clean_tool | ❌ 未开始 | |
| agent | Planner | ❌ 未开始 | |
| agent | Executor | ❌ 未开始 | |
| agent | Reflection | ⏳ Phase 2 | |
| agent | Memory | ❌ 未开始 | |
| workflow | 发布工作流 | ✅ 已完成 | Collect → Analyze → Review → Notify |
| workflow | 热点发现工作流 | ✅ 已完成 | Collect → Analyze → Generate → Notify |
| workflow | 日报生成工作流 | ✅ 已完成 | Collect → Analyze → Generate → Review → Notify |
| workflow | Nodes (5种) | ✅ 已完成 | Collect/Analyze/Generate/Review/Notify |
| crawler | Account Manager | ✅ 已完成 | |
| crawler | Cookie Manager | ✅ 已完成 | |
| crawler | Proxy Manager | ✅ 已完成 | |
| crawler | Rate Limiter | ✅ 已完成 | 滑动窗口 30次/60s |
| crawler | Retry Handler | ✅ 已完成 | 指数退避重试 |
| crawler | Incremental Collector | ✅ 已完成 | |
| crawler | Scheduler | ✅ 已完成 | 集成所有子模块 |
| prompts | 模板 (YAML) | ✅ 已完成 | hot_radar/article/comment/writer 4个 |
| prompts | Prompt Service | ✅ 已完成 | 加载/渲染/列表 |
| prompts | 版本管理 | ⏳ Phase 2 | |
| prompts | 评估 | ⏳ Phase 2 | |
| infrastructure | Redis Stream 消费者 | ✅ 已完成 | |
| infrastructure | MySQL 客户端 | ✅ 已完成 | |
| infrastructure | WebSocket 通知器 | ✅ 已完成 | |
| rag | 全部 | ⏳ Phase 2 | |
| events | 全部 | ⏳ Phase 2 | |
| plugins | 全部 | ⏳ Phase 2 | |
| mcp | MCP Server | ⏳ Phase 2 | |

### 前端

| 模块 | 子模块 | 状态 | 负责人 | 预计完成 |
|------|--------|------|--------|---------|
| 后台 | Vite + Vue3 + NaiveUI 初始化 | ✅ 已完成 | |
| 后台 | 登录页面 | ✅ 已完成 | |
| 后台 | Dashboard 看板 | ✅ 已完成 | 4卡片 + 趋势/排行/分布表 |
| 后台 | 凭据管理页面 | ✅ 已完成 | |
| 后台 | 任务管理页面 | ✅ 已完成 | |
| 后台 | 数据分析页面 | ✅ 已完成 | 热点雷达 + 爆文拆解 + 评论洞察 |
| 后台 | 笔记浏览页面 | ✅ 已完成 | 搜索 + 瀑布流 + 详情抽屉 |
| 后台 | 笔记发布页面 | ✅ 已完成 | 草稿 CRUD + 状态流转 |
| 后台 | AI 智能体对话页面 | ✅ 已完成 | SSE 流式 + 对话侧栏 |
| 前台 | Nuxt3 项目初始化 | ⏳ Phase 2 | |
| 前台 | 瀑布流首页 | ⏳ Phase 2 | |
| 前台 | 笔记搜索/详情 | ⏳ Phase 2 | |
| 前台 | 用户主页 | ⏳ Phase 2 | |
| 前台 | 热点雷达页面 | ⏳ Phase 2 | | |

---

### 图例

- ✅ **已完成**
- ❌ **未开始**
- ⏳ **计划中（Phase 2）**
- 🚧 **开发中**
