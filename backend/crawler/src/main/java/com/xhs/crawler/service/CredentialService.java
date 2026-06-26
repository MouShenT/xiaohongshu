package com.xhs.crawler.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.xhs.crawler.model.entity.XhsCredential;

import java.util.List;

public interface CredentialService extends IService<XhsCredential> {

    List<XhsCredential> getUserCredentials(Long userId);

    XhsCredential createCredential(Long userId, String name, String cookies);

    void deleteCredential(Long userId, Long credentialId);
}
