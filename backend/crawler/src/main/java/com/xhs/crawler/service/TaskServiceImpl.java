package com.xhs.crawler.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.xhs.common.exception.BusinessException;
import com.xhs.crawler.mapper.TaskMapper;
import com.xhs.crawler.model.dto.TaskCreateRequest;
import com.xhs.crawler.model.entity.Task;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;

@Service
public class TaskServiceImpl extends ServiceImpl<TaskMapper, Task> implements TaskService {

    private final ObjectMapper objectMapper;

    public TaskServiceImpl(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @Override
    public Long createTask(Long userId, TaskCreateRequest request) {
        Task task = new Task();
        task.setUserId(userId);
        task.setType(request.getType());
        task.setStatus("PENDING");
        task.setProgress(0);
        task.setCredentialId(request.getCredentialId());

        if (request.getParams() != null) {
            try {
                task.setParams(objectMapper.writeValueAsString(request.getParams()));
            } catch (Exception e) {
                throw new BusinessException("参数序列化失败");
            }
        }

        baseMapper.insert(task);
        return task.getId();
    }

    @Override
    public Task getTask(Long userId, Long taskId) {
        Task task = baseMapper.selectOne(
                new LambdaQueryWrapper<Task>()
                        .eq(Task::getId, taskId)
                        .eq(Task::getUserId, userId)
        );
        if (task == null) {
            throw new BusinessException("任务不存在");
        }
        return task;
    }
}
