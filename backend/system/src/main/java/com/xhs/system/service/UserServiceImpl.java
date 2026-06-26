package com.xhs.system.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.xhs.common.constant.ApiConstant;
import com.xhs.common.exception.BusinessException;
import com.xhs.system.mapper.UserMapper;
import com.xhs.system.model.dto.LoginRequest;
import com.xhs.system.model.dto.RegisterRequest;
import com.xhs.system.model.entity.User;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.util.Date;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {

    private final PasswordEncoder passwordEncoder;
    private final StringRedisTemplate redisTemplate;
    private final SecretKey key;

    public UserServiceImpl(PasswordEncoder passwordEncoder,
                           StringRedisTemplate redisTemplate) {
        this.passwordEncoder = passwordEncoder;
        this.redisTemplate = redisTemplate;
        this.key = Keys.hmacShaKeyFor(
                "xhs-platform-secret-key-2024-spring-boot-3-jwt-hs256".getBytes(StandardCharsets.UTF_8)
        );
    }

    @Override
    public Map<String, Object> login(LoginRequest request) {
        User user = baseMapper.selectOne(
                new LambdaQueryWrapper<User>().eq(User::getUsername, request.getUsername())
        );

        if (user == null) {
            throw new BusinessException("用户不存在");
        }

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BusinessException("密码错误");
        }

        if (user.getStatus() == 0) {
            throw new BusinessException("账号已被禁用");
        }

        String token = Jwts.builder()
                .subject(user.getId().toString())
                .claim("username", user.getUsername())
                .claim("role", user.getRole())
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + 86400000))
                .signWith(key)
                .compact();

        user.setLastLoginAt(LocalDateTime.now());
        baseMapper.updateById(user);

        return Map.of(
                "token", token,
                "userId", user.getId(),
                "username", user.getUsername(),
                "nickname", user.getNickname() != null ? user.getNickname() : "",
                "role", user.getRole()
        );
    }

    @Override
    public void register(RegisterRequest request) {
        Long count = baseMapper.selectCount(
                new LambdaQueryWrapper<User>().eq(User::getUsername, request.getUsername())
        );

        if (count > 0) {
            throw new BusinessException("用户名已存在");
        }

        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setNickname(request.getNickname());
        user.setEmail(request.getEmail());
        user.setRole("USER");
        user.setStatus(1);

        baseMapper.insert(user);
    }

    @Override
    public User getCurrentUser(Long userId) {
        User user = baseMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        user.setPassword(null);
        return user;
    }

    @Override
    public void logout(String token) {
        String blacklistKey = ApiConstant.REDIS_TOKEN_BLACKLIST + token;
        redisTemplate.opsForValue().set(blacklistKey, "1", 24, TimeUnit.HOURS);
    }
}
