package com.xhs.aiclient;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication
@ComponentScan(basePackages = {"com.xhs.aiclient", "com.xhs.common"})
public class AiClientApplication {

    public static void main(String[] args) {
        SpringApplication.run(AiClientApplication.class, args);
    }
}
