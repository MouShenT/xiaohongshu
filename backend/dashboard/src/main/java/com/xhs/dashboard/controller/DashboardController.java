package com.xhs.dashboard.controller;

import com.xhs.common.result.Result;
import com.xhs.dashboard.service.DashboardService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    private final DashboardService dashboardService;

    public DashboardController(DashboardService dashboardService) {
        this.dashboardService = dashboardService;
    }

    @GetMapping("/stats")
    public Result<Map<String, Object>> getStats(@AuthenticationPrincipal Long userId) {
        return Result.success(dashboardService.getStats(userId));
    }

    @GetMapping("/task-trend")
    public Result<List<Map<String, Object>>> getTaskTrend(
            @AuthenticationPrincipal Long userId,
            @RequestParam(defaultValue = "7") int days) {
        return Result.success(dashboardService.getTaskTrend(userId, days));
    }

    @GetMapping("/top-notes")
    public Result<List<Map<String, Object>>> getTopNotes(
            @AuthenticationPrincipal Long userId,
            @RequestParam(defaultValue = "10") int limit) {
        return null; // TODO: restore when note mapper is available
    }

    @GetMapping("/distributions")
    public Result<Map<String, Object>> getDistributions(@AuthenticationPrincipal Long userId) {
        return Result.success(dashboardService.getDistributions(userId));
    }
}
