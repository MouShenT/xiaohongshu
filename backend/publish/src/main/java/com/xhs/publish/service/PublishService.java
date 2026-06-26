package com.xhs.publish.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.xhs.common.exception.BusinessException;
import com.xhs.publish.mapper.DraftMapper;
import com.xhs.publish.model.entity.Draft;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class PublishService extends ServiceImpl<DraftMapper, Draft> {

    public Draft createDraft(Long userId, String title, String content, String images, String tags) {
        Draft draft = new Draft();
        draft.setUserId(userId);
        draft.setTitle(title);
        draft.setContent(content);
        draft.setImages(images);
        draft.setTags(tags);
        draft.setStatus("DRAFT");
        baseMapper.insert(draft);
        return draft;
    }

    public Draft updateDraft(Long userId, Long id, String title, String content, String images, String tags) {
        Draft draft = baseMapper.selectOne(
                new LambdaQueryWrapper<Draft>()
                        .eq(Draft::getId, id)
                        .eq(Draft::getUserId, userId)
        );
        if (draft == null) throw new BusinessException("草稿不存在");
        if (!"DRAFT".equals(draft.getStatus())) throw new BusinessException("只能编辑草稿状态的笔记");

        if (title != null) draft.setTitle(title);
        if (content != null) draft.setContent(content);
        if (images != null) draft.setImages(images);
        if (tags != null) draft.setTags(tags);
        baseMapper.updateById(draft);
        return draft;
    }

    public void deleteDraft(Long userId, Long id) {
        Draft draft = baseMapper.selectOne(
                new LambdaQueryWrapper<Draft>()
                        .eq(Draft::getId, id)
                        .eq(Draft::getUserId, userId)
        );
        if (draft == null) throw new BusinessException("草稿不存在");
        baseMapper.deleteById(id);
    }

    public Draft getDraft(Long userId, Long id) {
        Draft draft = baseMapper.selectOne(
                new LambdaQueryWrapper<Draft>()
                        .eq(Draft::getId, id)
                        .eq(Draft::getUserId, userId)
        );
        if (draft == null) throw new BusinessException("草稿不存在");
        return draft;
    }

    public List<Draft> listDrafts(Long userId, String status, int page, int size) {
        LambdaQueryWrapper<Draft> wrapper = new LambdaQueryWrapper<Draft>()
                .eq(Draft::getUserId, userId);
        if (status != null && !status.isEmpty()) {
            wrapper.eq(Draft::getStatus, status);
        }
        wrapper.orderByDesc(Draft::getId);
        Page<Draft> p = baseMapper.selectPage(new Page<>(page, size), wrapper);
        return p.getRecords();
    }

    public void submitForReview(Long userId, Long id) {
        Draft draft = getDraft(userId, id);
        if (!"DRAFT".equals(draft.getStatus())) throw new BusinessException("只能提交草稿状态的笔记");
        draft.setStatus("REVIEWING");
        baseMapper.updateById(draft);
    }

    public void approve(Long userId, Long id) {
        Draft draft = getDraftForAdmin(userId, id);
        if (!"REVIEWING".equals(draft.getStatus())) throw new BusinessException("只能审核待审核的笔记");
        draft.setStatus("APPROVED");
        baseMapper.updateById(draft);
    }

    public void reject(Long userId, Long id, String reason) {
        Draft draft = getDraftForAdmin(userId, id);
        if (!"REVIEWING".equals(draft.getStatus())) throw new BusinessException("只能审核待审核的笔记");
        draft.setStatus("REJECTED");
        draft.setErrorMessage(reason);
        baseMapper.updateById(draft);
    }

    public void schedulePublish(Long userId, Long id, LocalDateTime publishAt) {
        Draft draft = getDraft(userId, id);
        draft.setStatus("SCHEDULED");
        draft.setPublishAt(publishAt);
        baseMapper.updateById(draft);
    }

    public void publish(Long userId, Long id, Long credentialId) {
        Draft draft = getDraft(userId, id);
        if ("PUBLISHED".equals(draft.getStatus())) throw new BusinessException("笔记已发布");

        draft.setStatus("PUBLISHING");
        draft.setCredentialId(credentialId);
        baseMapper.updateById(draft);

        // 调用 Python 微服务发布 (TODO: async via Redis Stream)
        try {
            draft.setStatus("PUBLISHED");
            draft.setPublishedAt(LocalDateTime.now());
        } catch (Exception e) {
            draft.setStatus("FAILED");
            draft.setErrorMessage(e.getMessage());
        }
        baseMapper.updateById(draft);
    }

    private Draft getDraftForAdmin(Long userId, Long draftId) {
        Draft draft = baseMapper.selectById(draftId);
        if (draft == null) throw new BusinessException("草稿不存在");

        Long adminId = 1L; // TODO: 从 SecurityContext 获取真实管理员 ID
        if (!userId.equals(adminId) && !draft.getUserId().equals(userId)) {
            throw new BusinessException("无权操作");
        }
        return draft;
    }
}
