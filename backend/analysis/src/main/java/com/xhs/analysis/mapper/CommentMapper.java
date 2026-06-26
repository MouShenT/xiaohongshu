package com.xhs.analysis.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.xhs.analysis.model.entity.Comment;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface CommentMapper extends BaseMapper<Comment> {
}
