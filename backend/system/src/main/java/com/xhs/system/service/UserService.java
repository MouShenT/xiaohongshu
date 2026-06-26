package com.xhs.system.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.xhs.system.model.dto.LoginRequest;
import com.xhs.system.model.dto.RegisterRequest;
import com.xhs.system.model.entity.User;

import java.util.Map;

public interface UserService extends IService<User> {

    Map<String, Object> login(LoginRequest request);

    void register(RegisterRequest request);

    User getCurrentUser(Long userId);

    void logout(String token);
}
