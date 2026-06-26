# 小红书 AI 运营平台

基于 Spider_XHS 构建的 AI 数据分析 SaaS 平台。覆盖热点雷达、爆文拆解、评论洞察、AI 创作、自动发布、竞品监控、达人库、关键词库、内容知识库、AI 运营 Agent。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后台前端 | Vben Admin v5 |
| 业务后端 | Spring Boot 3.4.x + MyBatis-Plus + Spring Security + JWT |
| AI 微服务 | FastAPI + PydanticAI + LangGraph |
| 数据库 | MySQL 8 + Redis 7 |
| 消息队列 | Redis Stream (MVP) / RabbitMQ (Phase 2) |
| 搜索引擎 | Elasticsearch (Phase 2) |
| 向量数据库 | Qdrant (Phase 2) |
| 对象存储 | MinIO (Phase 2) |

## 项目结构

```
xiaohongshu/
├── backend/                    # SpringBoot 多模块后端
│   ├── common/                 # 公共模块：工具、统一返回、全局异常
│   ├── system/                 # 用户中心 + JWT 认证
│   ├── crawler/                # 采集中心：凭据管理 + 任务调度
│   ├── analysis/               # 数据分析：热点雷达/爆文拆解/评论洞察
│   ├── publish/                # 发布管理：笔记发布/定时发布
│   ├── dashboard/              # 数据看板
│   ├── ai-client/              # AI 编排层客户端
│   └── gateway/                # API 网关：路由/跨域/WebSocket/安全
│
├── python-agent/               # FastAPI AI 微服务
│   ├── api/routers/            # 路由层
│   ├── application/services/   # 应用服务层
│   ├── domain/analyzers/       # 领域算法层
│   ├── orchestrator/           # AI 编排层
│   ├── agent/                  # 智能体层
│   ├── workflow/               # LangGraph 工作流
│   ├── tools/                  # Agent 工具层
│   ├── providers/              # 基础设施 Provider
│   ├── crawler/                # 采集中心
│   ├── prompts/                # Prompt 管理中心
│   └── rag/                    # RAG 知识库
│
├── deploy/infra/               # Docker 基础设施部署
│   ├── docker-compose.yml      # MySQL + Redis + RabbitMQ + ES + Qdrant + MinIO
│   ├── mysql/init/             # 数据库初始化脚本
│   ├── redis/                  # Redis 配置
│   └── elasticsearch/          # ES 配置
│
└── skills/xhs-apis/            # Spider_XHS 原版封装（不改动）
```

## 快速开始

### 1. 启动基础设施

```bash
cd deploy/infra
docker compose up -d mysql redis
```

### 2. 启动 SpringBoot

```bash
cd backend
mvn compile
mvn spring-boot:run -pl gateway
```

### 3. 启动 Python AI 服务

```bash
cd python-agent
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## 数据流

```
用户操作 → SpringBoot (创建 Task) → Redis Stream
                                        ↓
                                  Python Orchestrator
                                        ↓
                                  Spider_XHS / LLM 执行
                                        ↓
                                  回写 MySQL
                                        ↓
                                  WebSocket 推送
                                        ↓
                                  前端实时展示
```

## 许可证

MIT
