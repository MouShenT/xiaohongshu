package com.xhs.crawler.model.dto;

import java.util.Map;

public class TaskCreateRequest {

    private String type;
    private Map<String, Object> params;
    private Long credentialId;

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public Map<String, Object> getParams() { return params; }
    public void setParams(Map<String, Object> params) { this.params = params; }

    public Long getCredentialId() { return credentialId; }
    public void setCredentialId(Long credentialId) { this.credentialId = credentialId; }
}
