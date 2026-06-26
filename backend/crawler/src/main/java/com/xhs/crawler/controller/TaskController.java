package com.xhs.crawler.controller;

import com.xhs.common.result.Result;
import com.xhs.crawler.model.dto.TaskCreateRequest;
import com.xhs.crawler.model.entity.Task;
import com.xhs.crawler.service.TaskService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/task")
public class TaskController {

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    @PostMapping
    public Result<Long> createTask(@AuthenticationPrincipal Long userId,
                                   @RequestBody TaskCreateRequest request) {
        return Result.success(taskService.createTask(userId, request));
    }

    @GetMapping("/{taskId}")
    public Result<Task> getTask(@AuthenticationPrincipal Long userId,
                                @PathVariable Long taskId) {
        return Result.success(taskService.getTask(userId, taskId));
    }

    @GetMapping
    public Result<List<Task>> listTasks(@AuthenticationPrincipal Long userId,
                                         @RequestParam(defaultValue = "1") int page,
                                         @RequestParam(defaultValue = "20") int size,
                                         @RequestParam(required = false) String status) {
        return Result.success(taskService.listTasks(userId, page, size, status));
    }
}
