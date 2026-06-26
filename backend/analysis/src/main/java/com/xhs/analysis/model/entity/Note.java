package com.xhs.analysis.model.entity;

import com.baomidou.mybatisplus.annotation.*;
import java.time.LocalDateTime;

@TableName("note")
public class Note {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private String noteId;

    private String title;

    private String content;

    private String author;

    private String authorId;

    private Integer likes;

    private Integer collects;

    private Integer commentsCnt;

    private Integer shares;

    private String images;

    private String video;

    private String tags;

    private String category;

    private String url;

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

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public String getAuthorId() { return authorId; }
    public void setAuthorId(String authorId) { this.authorId = authorId; }

    public Integer getLikes() { return likes; }
    public void setLikes(Integer likes) { this.likes = likes; }

    public Integer getCollects() { return collects; }
    public void setCollects(Integer collects) { this.collects = collects; }

    public Integer getCommentsCnt() { return commentsCnt; }
    public void setCommentsCnt(Integer commentsCnt) { this.commentsCnt = commentsCnt; }

    public Integer getShares() { return shares; }
    public void setShares(Integer shares) { this.shares = shares; }

    public String getImages() { return images; }
    public void setImages(String images) { this.images = images; }

    public String getVideo() { return video; }
    public void setVideo(String video) { this.video = video; }

    public String getTags() { return tags; }
    public void setTags(String tags) { this.tags = tags; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }

    public LocalDateTime getCollectedAt() { return collectedAt; }
    public void setCollectedAt(LocalDateTime collectedAt) { this.collectedAt = collectedAt; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
