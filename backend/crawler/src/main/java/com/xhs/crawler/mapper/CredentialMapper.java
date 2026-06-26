package com.xhs.crawler.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.xhs.crawler.model.entity.XhsCredential;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface CredentialMapper extends BaseMapper<XhsCredential> {
}
