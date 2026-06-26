package com.xhs.crawler.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.xhs.common.exception.BusinessException;
import com.xhs.crawler.mapper.CredentialMapper;
import com.xhs.crawler.model.entity.XhsCredential;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CredentialServiceImpl extends ServiceImpl<CredentialMapper, XhsCredential> implements CredentialService {

    @Override
    public List<XhsCredential> getUserCredentials(Long userId) {
        return baseMapper.selectList(
                new LambdaQueryWrapper<XhsCredential>()
                        .eq(XhsCredential::getUserId, userId)
                        .orderByDesc(XhsCredential::getCreatedAt)
        );
    }

    @Override
    public XhsCredential createCredential(Long userId, String name, String cookies) {
        XhsCredential credential = new XhsCredential();
        credential.setUserId(userId);
        credential.setName(name);
        credential.setCookies(cookies);
        credential.setIsValid(1);
        baseMapper.insert(credential);
        return credential;
    }

    @Override
    public void deleteCredential(Long userId, Long credentialId) {
        XhsCredential credential = baseMapper.selectOne(
                new LambdaQueryWrapper<XhsCredential>()
                        .eq(XhsCredential::getId, credentialId)
                        .eq(XhsCredential::getUserId, userId)
        );
        if (credential == null) {
            throw new BusinessException("凭据不存在");
        }
        baseMapper.deleteById(credentialId);
    }
}
