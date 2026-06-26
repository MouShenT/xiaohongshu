
> 本文档定义本项目使用 Claude Code 进行开发、测试、Debug 的完整工作流程。
> 结合项目架构（SpringBoot 多模块 + FastAPI + Vue 前后台）制定。

---

## 目录

- [一、核心理念](#一核心理念)
- [二、CLAUDE.md 配置](#二claudemd-配置)
- [三、settings.json 配置](#三settingsjson-配置)
- [四、开发工作流](#四开发工作流)
- [五、编码工作流](#五编码工作流)
- [六、测试工作流](#六测试工作流)
- [七、Bug 修复工作流](#七bug-修复工作流)
- [八、代码审查工作流](#八代码审查工作流)
- [九、调试技巧](#九调试技巧)
- [十、项目专用命令速查](#十项目专用命令速查)

---

## 一、核心理念

```
[明确需求] → [理解现有代码] → [设计方案] → [编写代码] → [测试验证] → [提交]
     ↑                                                             |
     └────────────────────── Bug 发现 ─────────────────────────────┘
```

### 基本原则

1. **先理解，后修改** — 修改前先读现有代码
2. **小步提交** — 每个功能点独立 commit
3. **测试驱动** — 关键逻辑先写测试再写实现
4. **Plan Mode 先行** — 架构变更、多文件修改需先出计划
5. **日志可观测** — 先复现问题，再修代码

---

## 二、CLAUDE.md 配置

项目根目录的 `CLAUDE.md` 是 Claude Code 的核心配置文件，定义了项目上下文、命令别名和行为规则。

```markdown
# 小红书 AI 运营平台

## 项目概述
基于 Spider_XHS 构建的 AI 数据分析 SaaS 平台。
SpringBoot 3.4.x 多模块后端 + FastAPI/PydanticAI 微服务 + Vue3 (Nuxt+Vben Admin) 前端。

## 技术栈
- 后端: JDK 23, Spring Boot 3.4.x, MyBatis-Plus, Spring Security, JWT
- AI: Python 3.12, FastAPI 0.115.x, PydanticAI, LangGraph
- 数据: MySQL 8, Redis 7, RabbitMQ, Qdrant, ES, MinIO
- 前端: Nuxt 3 + Shadcn Vue (前台), Vben Admin v5 (后台)

## 目录结构
- `backend/` — SpringBoot 多模块项目
- `python-agent/` — FastAPI 微服务
- `web-front/` — Nuxt 3 前台
- `web-admin/` — Vben Admin v5 后台
- `deploy/infra/` — Docker 基础设施部署
- `skills/xhs-apis/` — Spider_XHS 封装（不动）

## 构建命令
- SpringBoot: `cd backend && mvn clean install -DskipTests`
- SpringBoot 运行: `cd backend && mvn spring-boot:run -pl {module}`
- FastAPI: `cd python-agent && uvicorn main:app --reload --port 8000`
- Nuxt: `cd web-front && pnpm dev`
- Vben Admin: `cd web-admin && pnpm dev`

## 测试命令
- SpringBoot: `cd backend && mvn test`
- Python: `cd python-agent && pytest`
- 前端: `cd web-front && pnpm test`

## 数据库连接
- MySQL: root@192.168.229.149:3306, 密码 root123!
- Redis: 192.168.229.149:6379
- RabbitMQ: admin/rabbit123!@192.168.229.149:15672
- ES: 192.168.229.149:9200
- Qdrant: 192.168.229.149:6333
- MinIO Console: 192.168.229.149:9001 (admin/minio123456!)

## 编码约定
- Java: 使用 Lombok, 遵循阿里规约
- Python: 使用 Pydantic 模型, 类型注解完整
- Commits: 中文描述, 格式 `{module}: {描述}`
```

---

## 三、settings.json 配置

`.claude/settings.local.json` 用于配置权限、环境变量和自动行为。

```json
{
  "permissions": {
    "allow": [
      "Bash(mvn *)",
      "Bash(python *)",
      "Bash(pip *)",
      "Bash(npm *)",
      "Bash(pnpm *)",
      "Bash(node *)",
      "Bash(docker *)",
      "Bash(ssh *)",
      "Bash(scp *)",
      "Bash(gh *)",
      "Bash(redis-cli *)",
      "Bash(mysql *)",
      "Bash(curl *)",
      "Bash(git *)",
      "Bash(find *)",
      "Bash(ls *)",
      "Bash(which *)",
      "Bash(cat *)",
      "WebSearch",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:pypi.org)",
      "WebFetch(domain:mvnrepository.com)"
    ]
  },
  "hooks": {
    "pre-tool-call": []
  },
  "env": {
    "MYSQL_HOST": "192.168.229.149",
    "MYSQL_PORT": "3306",
    "REDIS_HOST": "192.168.229.149",
    "REDIS_PORT": "6379",
    "RABBITMQ_HOST": "192.168.229.149",
    "RABBITMQ_PORT": "5672",
    "RABBITMQ_USER": "xhs_admin",
    "RABBITMQ_PASSWORD": "rabbit123!"
  }
}
```

---

## 四、开发工作流

### 总流程图

```
┌─────────────┐
│  接收需求    │  ← Issue / PR / 口头需求
└──────┬──────┘
       ▼
┌─────────────┐
│  需求分析    │  ← 明确范围、影响模块
└──────┬──────┘
       ▼
┌─────────────────┐
│  方案设计         │  ← 架构变更用 Plan Mode
│  (EnterPlanMode) │
└──────┬──────────┘
       ▼
┌─────────────┐
│  任务拆解     │  ← TodoWrite 创建任务列表
└──────┬──────┘
       ▼
┌─────────────┐
│  逐步实现     │  ← 按任务列表逐个完成
└──────┬──────┘
       ▼
┌─────────────┐
│  测试验证     │  ← 单元/集成/手动测试
└──────┬──────┘
       ▼
┌─────────────┐
│  代码审查     │  ← Claude Code Review / 自查
└──────┬──────┘
       ▼
┌─────────────┐
│  提交 PR     │  ← git commit + gh pr create
└─────────────┘
```

### 步骤详解

#### 步骤 1: 需求分析

```
用户输入 → 确认:
  - 模块 (backend/python-agent/web-front/web-admin)
  - 功能描述
  - 验收标准
  - 影响范围

输出: 清晰的需求陈述
```

**对话模板**:
```
用户: "在后台加一个凭据过期提醒"
→ 确认: 哪个后台？Vben Admin。什么触发？定时扫描 MySQL 过期凭据。怎么提醒？站内通知 + Webhook。
→ 影响范围: backend/crawler + backend/notification + web-admin
```

#### 步骤 2: 方案设计（变更较大时）

```bash
# 架构变更 / 多文件修改 / 新增功能
# → 使用 EnterPlanMode 进入计划模式
# → 输出设计方案到 plan 文件
# → 用户审批通过后执行
```

**需要 Plan Mode 的场景**:
- 新增数据库表
- 修改模块间接口
- 新增 Python Skill
- 新增前端页面路由
- 重构现有代码

**不需要 Plan Mode 的场景**:
- 修改单个 Controller/Service 方法
- Bug 修复
- 配置文件修改
- 简单的 CRUD 接口

#### 步骤 3: 任务拆解

```
确认需求后 → 创建 TaskList

Task 1: backend/system 模块新增通知配置表
Task 2: backend/crawler 凭据过期扫描定时任务
Task 3: backend/notification 站内通知服务
Task 4: web-admin 通知列表页面
Task 5: 测试验证
```

#### 步骤 4: 编码

```bash
# 1. 先读取相关代码
Read backend/crawler/src/main/java/...
Read backend/crawler/src/main/resources/mapper/...

# 2. 理解后逐步编写
# 先写 Entity → Mapper → Service → Controller
# 每完成一个文件编译验证
mvn compile -pl backend/crawler -am
```

#### 步骤 5: 提交

```bash
# 检查状态
git status
git diff

# 提交（中文描述，格式: {模块}: {动作} {描述}）
git add backend/crawler/src/main/java/...
git commit -m "crawler: 新增凭据过期扫描定时任务"
```

---

## 五、编码工作流

### SpringBoot 编码流程

```
1. 阅读现有代码 (Read Entity/Service/Mapper)
2. 检查数据库表结构 (如果涉及)
3. 按顺序创建/修改:
   Entity → DTO/Request → Mapper → Service → Controller
4. 编译验证:
   mvn compile -pl {module} -am
5. 单元测试:
   mvn test -pl {module} -Dtest={TestClass}
6. 启动验证:
   mvn spring-boot:run -pl {module}
```

**代码改动准则**:
- 单次修改不超过 3 个 Service 层文件
- Controller 只做参数校验和结果包装
- Service 中注入的 Mapper 不超过 3 个（否则应拆分 Service）

### Python 编码流程

```
1. 阅读现有代码 (Read router/service)
2. 确认 Pydantic 模型定义
3. 按顺序创建/修改:
   models/schemas → services → routers → main 注册
4. 语法检查:
   python -m py_compile file.py
5. 单元测试:
   pytest tests/ -k "test_name"
6. 接口测试:
   curl http://192.168.229.149:8000/api/v1/...
```

### 前端编码流程

```
1. 阅读现有页面组件
2. 确认 API 接口路径
3. 按顺序创建/修改:
   api/{module}.ts → views/{page}.vue → router 注册
4. 编译检查:
   pnpm type-check
   pnpm build
5. 开发预览:
   pnpm dev
```

---

## 六、测试工作流

### 测试金字塔

```
        ╱  E2E  ╲         ← 关键流程手动测
       ╱─────────╲
      ╱  集成测试  ╲       ← SpringBoot Test / FastAPI TestClient
     ╱──────────────╲
    ╱   单元测试      ╲    ← Service 层、工具类、纯算法
   ╱────────────────────╲
```

### SpringBoot 测试

```bash
# 运行全部测试
mvn test

# 运行单个模块测试
mvn test -pl backend/crawler

# 运行单个测试类
mvn test -pl backend/crawler -Dtest=TaskServiceTest

# 跳过测试编译
mvn clean install -DskipTests
```

**测试覆盖要求**:
- Service 层核心方法: 100%
- Controller 层: 只测参数校验异常路径
- Mapper: 不需要单元测试（集成测试覆盖）
- 工具/工具类: 100%

### FastAPI 测试

```bash
# 全部测试
cd python-agent && pytest

# 单个文件
pytest tests/test_hot_radar.py

# 带覆盖率
pytest --cov=application tests/
```

### 前端测试

```bash
# Vue 组件测试
cd web-admin && pnpm test

# 类型检查
pnpm type-check
```

### E2E 检测清单

```
注册 → 登录 → 创建凭据 → 创建采集任务 → 查看数据 → AI 分析 → 发布

每个步骤依次验证:
  - 前端页面是否正常渲染
  - 接口是否返回正确状态码
  - 数据是否正确入库
  - 错误情况是否有提示
```

---

## 七、Bug 修复工作流

```
┌──────────────┐
│  复现 Bug     │  ← 找重现步骤，截图/日志
└──────┬───────┘
       ▼
┌──────────────┐
│  定位根因     │  ← 从上到下逐层排查
└──────┬───────┘
       ▼
┌──────────────┐
│  修复代码     │  ← 最小改动原则
└──────┬───────┘
       ▼
┌──────────────┐
│  验证修复     │  ← 复现场景通过
└──────┬───────┘
       ▼
┌──────────────┐
│  回归测试     │  ← 确保不破坏其他功能
└──────┬───────┘
       ▼
┌──────────────┐
│  提交修复     │  ← commit 带 #issue 号
└──────────────┘
```

### Bug 定位方法

```bash
# 1. 看日志
docker logs xhs-mysql --tail=50
docker logs xhs-rabbitmq --tail=50
docker compose -f deploy/infra/docker-compose.yml logs --tail=50

# 2. 查 SpringBoot 日志
tail -f backend/logs/spring.log

# 3. 查 FastAPI 日志
tail -f python-agent/logs/app.log

# 4. 查数据库
mysql -uxhs_app -pxhs_app_2024! -h 192.168.229.149
> USE xhs_platform;
> SELECT * FROM task WHERE status='FAILED' \G

# 5. 查 Redis
redis-cli
> KEYS xhs:*
> GET xhs:task:123

# 6. 接口测试
curl -v http://192.168.229.149:8080/api/xhs/note/xxx
```

### 分层排查策略

```
SpringBoot Bug:
  前端报错 → Controller 入口 → Service 逻辑 → Mapper/SQL → Python API

Python Bug:
  HTTP 500 → Router 入参 → Service 逻辑 → Domain 算法 → Infrastructure 调用

前端 Bug:
  白屏/404 → Router 配置 → API 请求 → 组件渲染 → 数据绑定

数据 Bug:
  数据不对 → SQL 查询 → 缓存 → 异步任务 → 采集逻辑
```

### 修复原则

1. **最小改动**: 只修有问题的行，不重构周围的代码
2. **加测试**: 修复同时加一个测试用例防止回归
3. **提交信息**: `fix({module}): {问题描述} (close #{issue号})`

---

## 八、代码审查工作流

### 审查时机

- 每次提交前自查
- PR 创建后 review
- 每周定期 Code Review

### 审查 Checklist

```
□ 功能正确性
  - 是否符合需求
  - 边界条件是否处理
  - 异常路径是否有处理

□ 代码质量
  - 命名是否清晰
  - 是否有重复代码
  - 函数长度是否合理
  - 注释是否必要（不多不少）

□ 安全性
  - SQL 注入风险（MyBatis $ vs #）
  - XSS 防护
  - 敏感信息硬编码
  - JWT/Token 验证是否完整

□ 性能
  - N+1 查询问题
  - 索引是否合理
  - 循环内数据库调用
  - 大对象内存占用

□ 架构
  - 是否符合 DDD 分层
  - 是否依赖了不该依赖的层
  - 接口是否向后兼容
```

### Claude Code 审查方式

```bash
# 审查当前分支
gh pr create
gh pr review {pr_number} --approve

# 审查未提交的更改
git diff HEAD
# → 输出给 Claude 审查
```

---

## 九、调试技巧

### 后端调试

```bash
# SpringBoot 远程调试
mvn spring-boot:run -pl backend/gateway \
  -Dspring-boot.run.jvmArguments="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005"

# FastAPI 热重载
uvicorn main:app --reload --port 8000 --log-level debug

# MySQL 慢查询
docker exec xhs-mysql mysql -uroot -proot123! -e "SHOW FULL PROCESSLIST;"
docker exec xhs-mysql mysql -uroot -proot123! -e "SELECT * FROM mysql.slow_log;"
```

### 查看数据

```bash
# Redis 查看缓存
redis-cli -h 192.168.229.149 KEYS 'xhs:*'
redis-cli -h 192.168.229.149 GET 'xhs:note:123'

# RabbitMQ 查看队列
curl -s -u xhs_admin:rabbit123! http://192.168.229.149:15672/api/queues | python3 -m json.tool

# ES 查看索引
curl http://192.168.229.149:9200/_cat/indices?v

# MinIO 查看文件
curl http://192.168.229.149:9000/minio/health/live
```

### 常见问题快速定位

| 现象 | 排查步骤 |
|------|---------|
| SpringBoot 启动失败 | 看日志第一行 `ERROR`，检查端口冲突 |
| FastAPI 无法连接 | `curl http://192.168.229.149:8000/health` |
| 数据库连接失败 | `docker logs xhs-mysql --tail=20` |
| RabbitMQ 消息堆积 | 看管理后台队列积压数量 |
| Redis 连接超时 | `redis-cli ping` |
| ES 查询慢 | `curl http://192.168.229.149:9200/_cat/indices?v` 看分片 |
| 前端白屏 | 浏览器 F12 → Console 看报错 → Network 看 API 状态 |
| Python import 错误 | `python -c "from apis.xhs_pc_apis import XHS_Apis"` |

---

## 十、项目专用命令速查

### 基础设施

```bash
# 启动全部
docker compose -f deploy/infra/docker-compose.yml up -d

# 启动核心（MySQL + Redis + RabbitMQ）
docker compose -f deploy/infra/docker-compose.yml up -d mysql redis rabbitmq

# 查看状态
docker compose -f deploy/infra/docker-compose.yml ps

# 查看日志
docker compose -f deploy/infra/docker-compose.yml logs -f mysql

# 停止
docker compose -f deploy/infra/docker-compose.yml down
```

### SpringBoot

```bash
# 编译指定模块
mvn compile -pl backend/crawler -am

# 运行指定模块
mvn spring-boot:run -pl backend/gateway

# 测试
mvn test -pl backend/crawler -Dtest=TaskServiceTest

# 打包
mvn clean package -DskipTests
```

### Python FastAPI

```bash
# 开发模式
cd python-agent && uvicorn main:app --reload --port 8000

# 测试
cd python-agent && pytest -v

# 检查语法
python -m py_compile python-agent/main.py
```

### 前端

```bash
# Vben Admin
cd web-admin && pnpm dev

# Nuxt 前台
cd web-front && pnpm dev

# 构建
cd web-admin && pnpm build
```

### Git

```bash
# 查看当前状态
git status

# 查看最近提交
git log --oneline -10

# 暂存修改
git stash
git stash pop

# 分支操作
git checkout -b feature/{module}-{description}
git checkout master
```
