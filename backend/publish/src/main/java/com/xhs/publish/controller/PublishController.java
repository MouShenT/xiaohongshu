package com.xhs.publish.controller;

import com.xhs.common.result.Result;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/publish")
public class PublishController {

    @GetMapping("/health")
    public Result<String> health() {
        return Result.success("publish service ok");
    }
}
