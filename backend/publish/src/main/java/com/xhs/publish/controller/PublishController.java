package com.xhs.publish.controller;

import com.xhs.common.result.Result;
import com.xhs.publish.model.entity.Draft;
import com.xhs.publish.service.PublishService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/publish")
public class PublishController {

    private final PublishService publishService;

    public PublishController(PublishService publishService) {
        this.publishService = publishService;
    }

    @PostMapping("/draft")
    public Result<Draft> createDraft(@AuthenticationPrincipal Long userId,
                                     @RequestBody Map<String, String> body) {
        return Result.success(publishService.createDraft(
                userId,
                body.get("title"),
                body.get("content"),
                body.get("images"),
                body.get("tags")
        ));
    }

    @PutMapping("/draft/{id}")
    public Result<Draft> updateDraft(@AuthenticationPrincipal Long userId,
                                     @PathVariable Long id,
                                     @RequestBody Map<String, String> body) {
        return Result.success(publishService.updateDraft(
                userId, id,
                body.get("title"),
                body.get("content"),
                body.get("images"),
                body.get("tags")
        ));
    }

    @DeleteMapping("/draft/{id}")
    public Result<Void> deleteDraft(@AuthenticationPrincipal Long userId,
                                    @PathVariable Long id) {
        publishService.deleteDraft(userId, id);
        return Result.success();
    }

    @GetMapping("/draft/{id}")
    public Result<Draft> getDraft(@AuthenticationPrincipal Long userId,
                                  @PathVariable Long id) {
        return Result.success(publishService.getDraft(userId, id));
    }

    @GetMapping("/draft")
    public Result<List<Draft>> listDrafts(@AuthenticationPrincipal Long userId,
                                           @RequestParam(required = false) String status,
                                           @RequestParam(defaultValue = "1") int page,
                                           @RequestParam(defaultValue = "20") int size) {
        return Result.success(publishService.listDrafts(userId, status, page, size));
    }

    @PostMapping("/draft/{id}/submit")
    public Result<Void> submit(@AuthenticationPrincipal Long userId,
                               @PathVariable Long id) {
        publishService.submitForReview(userId, id);
        return Result.success();
    }

    @PostMapping("/draft/{id}/publish")
    public Result<Void> publish(@AuthenticationPrincipal Long userId,
                                @PathVariable Long id,
                                @RequestBody Map<String, Object> body) {
        Long credentialId = body.get("credentialId") != null
                ? Long.valueOf(body.get("credentialId").toString()) : null;
        publishService.publish(userId, id, credentialId);
        return Result.success();
    }

    @PostMapping("/draft/{id}/schedule")
    public Result<Void> schedule(@AuthenticationPrincipal Long userId,
                                 @PathVariable Long id,
                                 @RequestBody Map<String, String> body) {
        publishService.schedulePublish(userId, id, LocalDateTime.parse(body.get("publishAt")));
        return Result.success();
    }

    @PostMapping("/draft/{id}/approve")
    public Result<Void> approve(@AuthenticationPrincipal Long userId,
                                @PathVariable Long id) {
        publishService.approve(userId, id);
        return Result.success();
    }

    @PostMapping("/draft/{id}/reject")
    public Result<Void> reject(@AuthenticationPrincipal Long userId,
                               @PathVariable Long id,
                               @RequestBody Map<String, String> body) {
        publishService.reject(userId, id, body.get("reason"));
        return Result.success();
    }
}
