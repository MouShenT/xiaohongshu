package com.xhs.analysis.controller;

import com.xhs.common.result.Result;
import com.xhs.analysis.service.HotRadarService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/analysis/hot-radar")
public class HotRadarController {

    private final HotRadarService hotRadarService;

    public HotRadarController(HotRadarService hotRadarService) {
        this.hotRadarService = hotRadarService;
    }

    @GetMapping("/trending")
    public Result<List<Map<String, Object>>> getTrending(@AuthenticationPrincipal Long userId,
                                                          @RequestParam(defaultValue = "20") int limit) {
        return Result.success(hotRadarService.getTrending(userId, limit));
    }

    @PostMapping("/analyze")
    public Result<Long> analyze(@AuthenticationPrincipal Long userId,
                                @RequestBody Map<String, String> body) {
        String keyword = body.get("keyword");
        return Result.success(hotRadarService.createAnalysisTask(userId, keyword));
    }
}
