package com.xhs.analysis.model.entity;

import com.baomidou.mybatisplus.annotation.*;
import java.time.LocalDateTime;

@TableName("comment")
public class Comment {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private String noteId;

    private String commentId;

    private String parentId;

    private String content;

    private String author;

    private String authorId;

    private Integer likes;

    private LocalDateTime collectedAt;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getNoteId() { return noteId; }
    public void setNoteId(String noteId) { this.noteId = noteId; }

    public String getCommentId() { return commentId; }
    public void setCommentId(String commentId) { this.commentId = commentId; }

    public String getParentId() { return parentId; }
    public void setParentId(String parentId) { this.parentId = parentId; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public String getAuthorId() { return authorId; }
    public void setAuthorId(String authorId) { this.authorId = authorId; }

    public Integer getLikes() { return likes; }
    public void setLikes(Integer likes) { this.likes = likes; }

    public LocalDateTime getCollectedAt() { return collectedAt; }
    public void setCollectedAt(LocalDateTime collectedAt) { this.collectedAt = collectedAt; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
