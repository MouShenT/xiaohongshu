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

-- 插入默认管理员 (密码: admin123)
INSERT INTO `user` (`username`, `password`, `nickname`, `role`, `status`)
VALUES ('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '管理员', 'ADMIN', 1)
ON DUPLICATE KEY UPDATE `nickname` = VALUES(`nickname`);
