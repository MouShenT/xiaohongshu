package com.xhs.analysis.controller;

import com.xhs.common.result.Result;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/analysis")
public class AnalysisController {

    @GetMapping("/health")
    public Result<String> health() {
        return Result.success("analysis service ok");
    }
}
