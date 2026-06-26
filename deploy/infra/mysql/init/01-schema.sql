-- MySQL 初始化脚本
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

-- 笔记表
CREATE TABLE IF NOT EXISTS `note` (
  `id`            BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`       BIGINT NOT NULL COMMENT '所属用户',
  `note_id`       VARCHAR(50) NOT NULL COMMENT '小红书原始笔记ID',
  `title`         VARCHAR(500),
  `content`       TEXT,
  `author`        VARCHAR(100),
  `author_id`     VARCHAR(50),
  `likes`         INT DEFAULT 0,
  `collects`      INT DEFAULT 0,
  `comments_cnt`  INT DEFAULT 0,
  `shares`        INT DEFAULT 0,
  `images`        JSON COMMENT '图片URL列表',
  `video`         VARCHAR(500),
  `tags`          JSON,
  `category`      VARCHAR(50),
  `url`           VARCHAR(500),
  `collected_at`  DATETIME COMMENT '采集时间',
  `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_id (`user_id`),
  INDEX idx_note_id (`note_id`),
  INDEX idx_collected_at (`collected_at`),
  FULLTEXT INDEX ft_title_content (`title`, `content`) WITH PARSER ngram
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小红书笔记';

-- 评论表
CREATE TABLE IF NOT EXISTS `comment` (
  `id`            BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`       BIGINT NOT NULL COMMENT '所属用户',
  `note_id`       VARCHAR(50) NOT NULL COMMENT '所属笔记ID',
  `comment_id`    VARCHAR(50) NOT NULL COMMENT '小红书原始评论ID',
  `parent_id`     VARCHAR(50) COMMENT '父评论ID（楼中楼）',
  `content`       TEXT NOT NULL,
  `author`        VARCHAR(100),
  `author_id`     VARCHAR(50),
  `likes`         INT DEFAULT 0,
  `collected_at`  DATETIME COMMENT '采集时间',
  `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_note_id (`note_id`),
  INDEX idx_user_id (`user_id`),
  FULLTEXT INDEX ft_content (`content`) WITH PARSER ngram
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小红书评论';

-- 草稿/发布表
CREATE TABLE IF NOT EXISTS `draft` (
  `id`            BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`       BIGINT NOT NULL,
  `title`         VARCHAR(500),
  `content`       TEXT,
  `images`        JSON,
  `tags`          JSON,
  `status`        VARCHAR(20) DEFAULT 'DRAFT' COMMENT 'DRAFT / PENDING / PUBLISHED / FAILED',
  `publish_at`    DATETIME COMMENT '定时发布时间',
  `published_at`  DATETIME COMMENT '实际发布时间',
  `credential_id` BIGINT,
  `error_message` TEXT,
  `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_status (`user_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='发布草稿';

-- 项目表（Phase 2 多租户基础）
CREATE TABLE IF NOT EXISTS `project` (
  `id`          BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id`     BIGINT NOT NULL,
  `name`        VARCHAR(100) NOT NULL,
  `description` TEXT,
  `config`      JSON,
  `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_id (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目';

-- 插入默认管理员 (密码: admin123)
INSERT INTO `user` (`username`, `password`, `nickname`, `role`, `status`)
VALUES ('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '管理员', 'ADMIN', 1)
ON DUPLICATE KEY UPDATE `nickname` = VALUES(`nickname`);
