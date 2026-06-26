package com.xhs.system.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.xhs.system.model.entity.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
}
