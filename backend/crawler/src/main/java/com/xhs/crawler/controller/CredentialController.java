package com.xhs.crawler.controller;

import com.xhs.common.result.Result;
import com.xhs.crawler.model.entity.XhsCredential;
import com.xhs.crawler.service.CredentialService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/credential")
public class CredentialController {

    private final CredentialService credentialService;

    public CredentialController(CredentialService credentialService) {
        this.credentialService = credentialService;
    }

    @GetMapping
    public Result<List<XhsCredential>> list(@AuthenticationPrincipal Long userId) {
        return Result.success(credentialService.getUserCredentials(userId));
    }

    @PostMapping
    public Result<XhsCredential> create(@AuthenticationPrincipal Long userId,
                                        @RequestBody Map<String, String> body) {
        return Result.success(
                credentialService.createCredential(userId, body.get("name"), body.get("cookies"))
        );
    }

    @DeleteMapping("/{credentialId}")
    public Result<Void> delete(@AuthenticationPrincipal Long userId,
                               @PathVariable Long credentialId) {
        credentialService.deleteCredential(userId, credentialId);
        return Result.success();
    }
}
