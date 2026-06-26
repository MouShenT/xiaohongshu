# 基础设施 Docker 部署方案

> 适用于 Ubuntu / CentOS 服务器，Docker Compose 一键部署。

---

## 目录结构

在服务器上任意位置创建 `infra/` 目录：

```
infra/
├── docker-compose.yml          # 主编排文件
├── .env                        # 环境变量（密码、版本等）
├── mysql/
│   ├── init/                   # 初始化 SQL
│   │   └── 01-schema.sql       # 建表脚本
│   └── my.cnf                  # MySQL 配置
├── redis/
│   └── redis.conf              # Redis 配置
├── rabbitmq/
│   └── defs.json               # RabbitMQ 定义（可选）
├── elasticsearch/
│   ├── elasticsearch.yml       # ES 配置
│   └── plugins/                # 插件目录
├── qdrant/
│   └── config.yaml             # Qdrant 配置
└── minio/
    └── config.env              # MinIO 环境
```

---

## 一、docker-compose.yml

```yaml
version: "3.9"

networks:
  xhs-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  mysql-data:
  redis-data:
  rabbitmq-data:
  elasticsearch-data:
  qdrant-data:
  minio-data:

services:
  # ============================================================
  # MySQL 8 — 主业务数据库
  # ============================================================
  mysql:
    image: mysql:8.0
    container_name: xhs-mysql
    restart: unless-stopped
    networks:
      xhs-network:
        ip: 172.20.0.10
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
      - ./mysql/init:/docker-entrypoint-initdb.d
      - ./mysql/my.cnf:/etc/mysql/conf.d/my.cnf
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: xhs_platform
      MYSQL_USER: xhs_app
      MYSQL_PASSWORD: ${MYSQL_APP_PASSWORD}
      TZ: Asia/Shanghai
    command: >
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --max_connections=300
      --default-time-zone=+8:00
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ============================================================
  # Redis 7 — 缓存/限流/Token黑名单/任务队列
  # ============================================================
  redis:
    image: redis:7-alpine
    container_name: xhs-redis
    restart: unless-stopped
    networks:
      xhs-network:
        ip: 172.20.0.11
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
      - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # ============================================================
  # RabbitMQ 3 — 消息队列（异步 AI 分析解耦）
  # ============================================================
  rabbitmq:
    image: rabbitmq:3.13-management-alpine
    container_name: xhs-rabbitmq
    restart: unless-stopped
    networks:
      xhs-network:
        ip: 172.20.0.12
    ports:
      - "5672:5672"      # AMQP 协议
      - "15672:15672"    # 管理后台
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
      RABBITMQ_DEFAULT_VHOST: /
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_port_connectivity"]
      interval: 15s
      timeout: 5s
      retries: 5

  # ============================================================
  # Elasticsearch 8 — 全文搜索（Phase 2 启用）
  # ============================================================
  elasticsearch:
    image: elasticsearch:8.12.0
    container_name: xhs-elasticsearch
    restart: unless-stopped
    networks:
      xhs-network:
        ip: 172.20.0.13
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
      - ./elasticsearch/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms1g -Xmx1g
      - xpack.security.enabled=false
      - TZ=Asia/Shanghai
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536
        hard: 65536
    deploy:
      resources:
        limits:
          memory: 2g

  # ============================================================
  # Qdrant — 向量数据库（Phase 2 启用，RAG/知识库）
  # ============================================================
  qdrant:
    image: qdrant/qdrant:v1.9.0
    container_name: xhs-qdrant
    restart: unless-stopped
    networks:
      xhs-network:
        ip: 172.20.0.14
    ports:
      - "6333:6333"     # REST API
      - "6334:6334"     # gRPC
    volumes:
      - qdrant-data:/qdrant/storage
      - ./qdrant/config.yaml:/qdrant/config/config.yaml
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334
      TZ: Asia/Shanghai

  # ============================================================
  # MinIO — 对象存储（Phase 2 启用，图片/视频/文件）
  # ============================================================
  minio:
    image: minio/minio:latest
    container_name: xhs-minio
    restart: unless-stopped
    networks:
      xhs-network:
        ip: 172.20.0.15
    ports:
      - "9000:9000"     # API
      - "9001:9001"     # Console
    volumes:
      - minio-data:/data
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
      MINIO_REGION: cn-east-1
      TZ: Asia/Shanghai
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 15s
      timeout: 5s
      retries: 5

  # ============================================================
  # 可选: Adminer — 数据库管理工具
  # ============================================================
  adminer:
    image: adminer:latest
    container_name: xhs-adminer
    restart: unless-stopped
    networks:
      xhs-network:
        ip: 172.20.0.20
    ports:
      - "18080:8080"
    depends_on:
      - mysql

  # ============================================================
  # 可选: RedisInsight — Redis 管理工具
  # ============================================================
  redis-insight:
    image: redis/redisinsight:latest
    container_name: xhs-redis-insight
    restart: unless-stopped
    networks:
      xhs-network:
        ip: 172.20.0.21
    ports:
      - "15540:5540"
    volumes:
      - redis-insight-data:/data
  # ============================================================
  # 可选: Cerebro — ES 管理工具
  # ============================================================
  cerebro:
    image: lmenezes/cerebro:latest
    container_name: xhs-cerebro
    restart: unless-stopped
    networks:
      xhs-network:
        ip: 172.20.0.22
    ports:
      - "19000:9000"
```

---

## 二、.env 环境变量

```bash
# ===== MySQL =====
MYSQL_ROOT_PASSWORD=root123!
MYSQL_APP_PASSWORD=xhs_app_2024!

# ===== Redis =====
# 无密码模式（内网使用）
# 如需密码取消注释下面:
# REDIS_PASSWORD=redis123!

# ===== RabbitMQ =====
RABBITMQ_USER=xhs_admin
RABBITMQ_PASSWORD=rabbit123!

# ===== MinIO =====
MINIO_ROOT_USER=xhs_admin
MINIO_ROOT_PASSWORD=minio123456!

# ===== 服务端口映射前缀（避免冲突） =====
# MySQL: 3306
# Redis: 6379
# RabbitMQ: 5672 / 15672
# ES: 9200
# Qdrant: 6333
# MinIO: 9000 / 9001
# Adminer: 18080
# RedisInsight: 15540
# Cerebro: 19000
```

---

## 三、配置文件

### mysql/my.cnf

```ini
[mysqld]
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
default-time-zone = +8:00

# 连接数
max_connections = 300

# 日志
slow_query_log = 1
slow_query_log_file = /var/lib/mysql/slow.log
long_query_time = 2

# InnoDB
innodb_buffer_pool_size = 2G
innodb_log_file_size = 512M
innodb_flush_log_at_trx_commit = 2
innodb_file_per_table = 1

[client]
default-character-set = utf8mb4
```

### redis/redis.conf

```conf
# 绑定内网 IP
bind 0.0.0.0
port 6379

# 守护进程（容器内设为 no）
daemonize no

# 持久化
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfilename "appendonly.aof"

# 密码
# requirepass ${REDIS_PASSWORD}

# 最大内存（5GB 服务器可设 2G）
maxmemory 2gb
maxmemory-policy allkeys-lru

# 连接
tcp-keepalive 300
timeout 0

# 慢查询
slowlog-log-slower-than 10000
slowlog-max-len 128
```

### elasticsearch/elasticsearch.yml

```yaml
cluster.name: xhs-es-cluster
node.name: xhs-es-node-1

path.data: /usr/share/elasticsearch/data
path.logs: /usr/share/elasticsearch/logs

network.host: 0.0.0.0
http.port: 9200

discovery.type: single-node

# 中文分词
analysis:
  analyzer:
    ik_smart:
      type: ik_smart
    ik_max_word:
      type: ik_max_word

# 关闭安全认证（内网环境）
xpack.security.enabled: false
xpack.security.enrollment.enabled: false

# 跨域
http.cors.enabled: true
http.cors.allow-origin: "*"
```

### qdrant/config.yaml

```yaml
log_level: INFO

storage:
  storage_path: /qdrant/storage
  optimizers:
    default_segment_number: 2
    memmap_threshold_kb: 20000

service:
  http_port: 6333
  grpc_port: 6334
  max_request_size_mb: 64
```

---

## 四、MySQL 初始化脚本

### mysql/init/01-schema.sql

```sql
-- 创建数据库（Compose 已自动创建，此脚本确保初始化）
CREATE DATABASE IF NOT EXISTS `xhs_platform` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `xhs_platform`;

-- 用户表
CREATE TABLE IF NOT EXISTS `user` (
  `id`          BIGINT AUTO_INCREMENT PRIMARY KEY,
  `username`    VARCHAR(50) NOT NULL UNIQUE,
  `password`    VARCHAR(255) NOT NULL COMMENT 'BCrypt 加密',
  `nickname`    VARCHAR(50),
  `avatar`      VARCHAR(500),
  `email`       VARCHAR(100),
  `role`        VARCHAR(20) DEFAULT 'USER' COMMENT 'USER / ADMIN / API',
  `status`      TINYINT DEFAULT 1 COMMENT '1=正常 0=禁用',
  `last_login_at` DATETIME,
  `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 小红书凭据表
CREATE TABLE IF NOT EXISTS `xhs_credential` (
  `id`          BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`     BIGINT NOT NULL,
  `name`        VARCHAR(50) NOT NULL COMMENT '凭据名称',
  `cookies`     TEXT NOT NULL COMMENT 'AES 加密存储',
  `is_valid`    TINYINT DEFAULT 1,
  `expires_at`  DATETIME,
  `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_id (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小红书凭据';

-- 异步任务表
CREATE TABLE IF NOT EXISTS `task` (
  `id`            BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`       BIGINT NOT NULL,
  `type`          VARCHAR(30) NOT NULL COMMENT 'NOTE_COLLECT / ANALYZE / PIPELINE / DATA_CLEAN',
  `status`        VARCHAR(20) DEFAULT 'PENDING' COMMENT 'PENDING/RUNNING/SUCCESS/FAILED/CANCELLED',
  `params`        JSON,
  `result`        JSON,
  `progress`      INT DEFAULT 0 COMMENT '0-100',
  `error_message` TEXT,
  `credential_id` BIGINT,
  `started_at`    DATETIME,
  `finished_at`   DATETIME,
  `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_status (`user_id`, `status`),
  INDEX idx_type_status (`type`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='异步任务';

-- AI 对话记录表
CREATE TABLE IF NOT EXISTS `agent_conversation` (
  `id`          BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`     BIGINT NOT NULL,
  `title`       VARCHAR(200),
  `messages`    JSON NOT NULL,
  `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_id (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI 对话记录';

-- 知识库文档表
CREATE TABLE IF NOT EXISTS `knowledge_doc` (
  `id`          BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`     BIGINT NOT NULL,
  `title`       VARCHAR(200),
  `content`     TEXT,
  `tags`        JSON,
  `source_url`  VARCHAR(500),
  `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_tags (`user_id`),
  FULLTEXT INDEX ft_content (`title`, `content`) WITH PARSER ngram
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库文档';

-- 插入默认管理员
INSERT INTO `user` (`username`, `password`, `nickname`, `role`, `status`)
VALUES ('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '管理员', 'ADMIN', 1)
ON DUPLICATE KEY UPDATE `nickname` = VALUES(`nickname`);
-- 密码: admin123（BCrypt 占位，首次启动需改）
```

---

## 五、部署步骤

### 1. 服务器安装 Docker

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y docker.io docker-compose-v2

# 启动 Docker
sudo systemctl enable docker && sudo systemctl start docker

# 验证
docker --version && docker compose version
```

### 2. 上传部署文件

```bash
# 在服务器创建目录
mkdir -p /opt/xhs-infra
cd /opt/xhs-infra

# 创建配置文件目录
mkdir -p mysql/init redis rabbitmq elasticsearch qdrant minio

# 将上面的文件上传到对应目录
# 方法: scp / rsync / 或直接 git clone 后复制
```

### 3. 设置 vm.max_map_count（ES 需要）

```bash
# 永久生效
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 4. 启动服务

```bash
cd /opt/xhs-infra

# 先启动核心服务（MySQL + Redis + RabbitMQ）
docker compose up -d mysql redis rabbitmq

# 验证核心服务健康
docker compose ps

# 查看日志
docker compose logs mysql | tail -20

# 确认 MySQL 可连接
docker exec xhs-mysql mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "SHOW DATABASES;"

# 启动全部服务（含 ES / Qdrant / MinIO）
docker compose up -d
```

### 5. 验证所有服务

```bash
# 查看所有服务状态
docker compose ps

# 测试连接
docker exec xhs-mysql mysql -uxhs_app -p"${MYSQL_APP_PASSWORD}" -e "USE xhs_platform; SHOW TABLES;"
docker exec xhs-redis redis-cli ping
docker exec xhs-rabbitmq rabbitmqctl status | head -5
curl http://localhost:9200
curl http://localhost:6333
curl http://localhost:9000/minio/health/live
```

### 6. 常用管理命令

```bash
# 查看所有日志
docker compose logs -f

# 查看单个服务日志
docker compose logs -f mysql

# 重启单个服务
docker compose restart rabbitmq

# 停止所有
docker compose down

# 停止并删除数据卷（谨慎！会清数据）
docker compose down -v

# 更新镜像
docker compose pull
docker compose up -d
```

---

## 六、服务连接信息

应用通过以下信息连接基础设施：

| 服务 | 主机地址 | 端口 | 说明 |
|------|---------|------|------|
| MySQL | `172.20.0.10` | 3306 | 内网固定 IP，或 `xhs-mysql` 容器名 |
| Redis | `172.20.0.11` | 6379 | 内网固定 IP，或 `xhs-redis` 容器名 |
| RabbitMQ | `172.20.0.12` | 5672 | AMQP 端口 |
| RabbitMQ 管理 | 服务器 IP | 15672 | Web 管理后台 |
| Elasticsearch | `172.20.0.13` | 9200 | REST API |
| Qdrant | `172.20.0.14` | 6333 | REST API |
| MinIO API | `172.20.0.15` | 9000 | S3 兼容 API |
| MinIO Console | 服务器 IP | 9001 | Web 管理后台 |

### 注意事项

1. **SpringBoot 连接**：使用 Docker 内网 IP `172.20.0.x` 或容器名（`xhs-mysql` 等），前提是 SpringBoot 也在同一网络
2. **Python 连接**：同上
3. **开发环境连接**：使用服务器公网 IP + 映射端口
4. **安全**: `.env` 文件不要提交到 git，建议加入 `.gitignore`
5. **资源**：5GB 内存服务器建议只启动 mysql + redis + rabbitmq，ES/Qdrant 在 Phase 2 再开
