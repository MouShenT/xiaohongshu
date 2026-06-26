package com.xhs.dashboard.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.xhs.analysis.mapper.NoteMapper;
import com.xhs.analysis.mapper.CommentMapper;
import com.xhs.analysis.model.entity.Note;
import com.xhs.analysis.model.entity.Comment;
import com.xhs.crawler.mapper.TaskMapper;
import com.xhs.crawler.model.entity.Task;
import com.xhs.publish.mapper.DraftMapper;
import com.xhs.publish.model.entity.Draft;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.TimeUnit;

@Service
public class DashboardService {

    private final NoteMapper noteMapper;
    private final CommentMapper commentMapper;
    private final TaskMapper taskMapper;
    private final DraftMapper draftMapper;
    private final StringRedisTemplate redisTemplate;

    public DashboardService(NoteMapper noteMapper,
                            CommentMapper commentMapper,
                            TaskMapper taskMapper,
                            DraftMapper draftMapper,
                            StringRedisTemplate redisTemplate) {
        this.noteMapper = noteMapper;
        this.commentMapper = commentMapper;
        this.taskMapper = taskMapper;
        this.draftMapper = draftMapper;
        this.redisTemplate = redisTemplate;
    }

    public Map<String, Object> getStats(Long userId) {
        String cacheKey = "xhs:dashboard:stats:" + userId;
        String cached = redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {
            try {
                return new com.fasterxml.jackson.databind.ObjectMapper().readValue(cached, Map.class);
            } catch (Exception ignored) {}
        }

        // 笔记总数
        Long noteCount = noteMapper.selectCount(
                new LambdaQueryWrapper<Note>().eq(Note::getUserId, userId)
        );

        // 今日采集
        LocalDateTime todayStart = LocalDateTime.now().withHour(0).withMinute(0).withSecond(0);
        Long todayCollect = noteMapper.selectCount(
                new LambdaQueryWrapper<Note>()
                        .eq(Note::getUserId, userId)
                        .ge(Note::getCreatedAt, todayStart)
        );

        // 进行中任务
        Long runningTasks = taskMapper.selectCount(
                new LambdaQueryWrapper<Task>()
                        .eq(Task::getUserId, userId)
                        .in(Task::getStatus, "PENDING", "RUNNING")
        );

        // 待发布草稿
        Long pendingDrafts = draftMapper.selectCount(
                new LambdaQueryWrapper<Draft>()
                        .eq(Draft::getUserId, userId)
                        .in(Draft::getStatus, "DRAFT", "REVIEWING", "APPROVED", "SCHEDULED")
        );

        Map<String, Object> stats = new LinkedHashMap<>();
        stats.put("noteCount", noteCount);
        stats.put("todayCollect", todayCollect);
        stats.put("runningTasks", runningTasks);
        stats.put("pendingDrafts", pendingDrafts);

        // 缓存 5 分钟
        try {
            redisTemplate.opsForValue().set(cacheKey,
                    new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(stats),
                    Duration.ofMinutes(5));
        } catch (Exception ignored) {}

        return stats;
    }

    public List<Map<String, Object>> getTaskTrend(Long userId, int days) {
        LocalDateTime since = LocalDateTime.now().minusDays(days);
        List<Task> tasks = taskMapper.selectList(
                new LambdaQueryWrapper<Task>()
                        .eq(Task::getUserId, userId)
                        .ge(Task::getCreatedAt, since)
                        .orderByAsc(Task::getCreatedAt)
        );

        Map<String, Map<String, Object>> daily = new LinkedHashMap<>();
        for (int i = 0; i < days; i++) {
            String day = LocalDateTime.now().minusDays(days - 1 - i).toLocalDate().toString();
            Map<String, Object> d = new LinkedHashMap<>();
            d.put("date", day);
            d.put("total", 0);
            d.put("success", 0);
            d.put("failed", 0);
            daily.put(day, d);
        }

        for (Task t : tasks) {
            String day = t.getCreatedAt().toLocalDate().toString();
            Map<String, Object> d = daily.get(day);
            if (d != null) {
                d.put("total", (int) d.get("total") + 1);
                if ("SUCCESS".equals(t.getStatus())) {
                    d.put("success", (int) d.get("success") + 1);
                } else if ("FAILED".equals(t.getStatus())) {
                    d.put("failed", (int) d.get("failed") + 1);
                }
            }
        }

        return new ArrayList<>(daily.values());
    }

    public List<Map<String, Object>> getTopNotes(Long userId, int limit) {
        List<Note> notes = noteMapper.selectList(
                new LambdaQueryWrapper<Note>()
                        .eq(Note::getUserId, userId)
                        .orderByDesc(Note::getLikes)
                        .last("LIMIT " + limit)
        );

        List<Map<String, Object>> result = new ArrayList<>();
        for (Note n : notes) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("id", n.getId());
            item.put("noteId", n.getNoteId());
            item.put("title", n.getTitle());
            item.put("likes", n.getLikes());
            item.put("collects", n.getCollects());
            item.put("comments", n.getCommentsCnt());
            result.add(item);
        }
        return result;
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> getTaskDistributions(Long userId) {
        List<Task> tasks = taskMapper.selectList(
                new LambdaQueryWrapper<Task>().eq(Task::getUserId, userId)
        );

        Map<String, Integer> byStatus = new LinkedHashMap<>();
        Map<String, Integer> byType = new LinkedHashMap<>();
        for (Task t : tasks) {
            byStatus.merge(t.getStatus(), 1, Integer::sum);
            byType.merge(t.getType(), 1, Integer::sum);
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("byStatus", byStatus);
        result.put("byType", byType);
        return result;
    }
}
