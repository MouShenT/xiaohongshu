package com.xhs.analysis.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.xhs.crawler.mapper.TaskMapper;
import com.xhs.crawler.model.entity.Task;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
public class HotRadarServiceImpl implements HotRadarService {

    private final StringRedisTemplate redisTemplate;
    private final TaskMapper taskMapper;
    private final ObjectMapper objectMapper;

    // 缓存 key
    private static final String REDIS_HOT_TRENDING = "xhs:hot:trending";

    public HotRadarServiceImpl(StringRedisTemplate redisTemplate,
                               TaskMapper taskMapper,
                               ObjectMapper objectMapper) {
        this.redisTemplate = redisTemplate;
        this.taskMapper = taskMapper;
        this.objectMapper = objectMapper;
    }

    @Override
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getTrending(Long userId, int limit) {
        // 1. 查缓存
        String cached = redisTemplate.opsForValue().get(REDIS_HOT_TRENDING);
        if (cached != null) {
            try {
                return objectMapper.readValue(cached, List.class);
            } catch (Exception e) {
                // 缓存解析失败，忽略
            }
        }
        return new ArrayList<>();
    }

    @Override
    public Long createAnalysisTask(Long userId, String keyword) {
        Task task = new Task();
        task.setUserId(userId);
        task.setType("HOT_RADAR");
        task.setStatus("PENDING");
        task.setProgress(0);
        try {
            task.setParams(objectMapper.writeValueAsString(Map.of("keyword", keyword)));
        } catch (Exception e) {
            task.setParams("{\"keyword\":\"" + keyword + "\"}");
        }
        taskMapper.insert(task);

        // 写入 Redis Stream 通知 Python 消费
        try {
            String message = objectMapper.writeValueAsString(Map.of(
                    "taskId", task.getId(),
                    "type", "HOT_RADAR",
                    "keyword", keyword
            ));
            redisTemplate.opsForStream().add("xhs:task:queue", Map.of("payload", message));
        } catch (Exception e) {
            // Redis 不可用时不影响主流程
        }

        return task.getId();
    }
}
