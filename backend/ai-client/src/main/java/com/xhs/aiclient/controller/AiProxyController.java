package com.xhs.aiclient.controller;

import com.xhs.aiclient.client.AiOrchestratorClient;
import com.xhs.common.result.Result;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/ai")
public class AiProxyController {

    private final AiOrchestratorClient aiClient;

    public AiProxyController(AiOrchestratorClient aiClient) {
        this.aiClient = aiClient;
    }

    @GetMapping("/health")
    public Result<String> health() {
        return Result.success(aiClient.health());
    }

    @GetMapping("/xhs/search")
    public Result<Map<String, Object>> searchNotes(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "20") int limit,
            @RequestParam(defaultValue = "general") String sort) {
        return Result.success(aiClient.searchNotes(keyword, limit, sort));
    }

    @GetMapping("/xhs/note/{noteId}")
    public Result<Map<String, Object>> getNoteDetail(@PathVariable String noteId) {
        return Result.success(aiClient.getNoteDetail(noteId));
    }

    @GetMapping("/xhs/note/{noteId}/comments")
    public Result<Map<String, Object>> getComments(
            @PathVariable String noteId,
            @RequestParam(defaultValue = "50") int limit) {
        return Result.success(aiClient.getComments(noteId, limit));
    }

    @GetMapping("/xhs/hot-topics")
    public Result<Map<String, Object>> getHotTopics(@RequestParam(defaultValue = "20") int limit) {
        return Result.success(aiClient.getHotTopics(limit));
    }

    @PostMapping("/xhs/analyze-trend")
    public Result<Map<String, Object>> analyzeTrend(@RequestBody Map<String, String> body) {
        return Result.success(aiClient.analyzeTrend(body.get("keyword")));
    }

    @PostMapping("/xhs/analyze-article")
    public Result<Map<String, Object>> analyzeArticle(@RequestBody Map<String, String> body) {
        return Result.success(aiClient.analyzeArticle(body.get("noteId")));
    }
}
