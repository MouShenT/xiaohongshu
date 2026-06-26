package com.xhs.common.constant;

public interface ApiConstant {

    String HEADER_AUTHORIZATION = "Authorization";
    String TOKEN_PREFIX = "Bearer ";
    String REDIS_TOKEN_BLACKLIST = "xhs:token:blacklist:";
    String REDIS_TASK_QUEUE = "xhs:task:queue";
}
