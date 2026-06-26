package com.xhs.system.controller;

import com.xhs.common.result.Result;
import com.xhs.system.model.entity.User;
import com.xhs.system.service.UserService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/user")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/me")
    public Result<User> getCurrentUser(@AuthenticationPrincipal Long userId) {
        return Result.success(userService.getCurrentUser(userId));
    }
}
