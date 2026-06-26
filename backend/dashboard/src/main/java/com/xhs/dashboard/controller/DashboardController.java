package com.xhs.dashboard.controller;

import com.xhs.common.result.Result;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    @GetMapping("/health")
    public Result<String> health() {
        return Result.success("dashboard service ok");
    }
}
