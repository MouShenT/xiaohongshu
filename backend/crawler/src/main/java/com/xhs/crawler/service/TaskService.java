package com.xhs.crawler.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.xhs.crawler.model.dto.TaskCreateRequest;
import com.xhs.crawler.model.entity.Task;

public interface TaskService extends IService<Task> {

    Long createTask(Long userId, TaskCreateRequest request);

    Task getTask(Long userId, Long taskId);
}
