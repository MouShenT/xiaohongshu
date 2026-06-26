package com.xhs.publish.model.entity;

import com.baomidou.mybatisplus.annotation.*;
import java.time.LocalDateTime;

@TableName("draft")
public class Draft {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private String title;

    private String content;

    private String images;

    private String tags;

    private String status;

    private LocalDateTime publishAt;

    private LocalDateTime publishedAt;

    private Long credentialId;

    private String errorMessage;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public String getImages() { return images; }
    public void setImages(String images) { this.images = images; }

    public String getTags() { return tags; }
    public void setTags(String tags) { this.tags = tags; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public LocalDateTime getPublishAt() { return publishAt; }
    public void setPublishAt(LocalDateTime publishAt) { this.publishAt = publishAt; }

    public LocalDateTime getPublishedAt() { return publishedAt; }
    public void setPublishedAt(LocalDateTime publishedAt) { this.publishedAt = publishedAt; }

    public Long getCredentialId() { return credentialId; }
    public void setCredentialId(Long credentialId) { this.credentialId = credentialId; }

    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
