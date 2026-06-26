package com.xhs.analysis.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.xhs.analysis.mapper.NoteMapper;
import com.xhs.analysis.model.entity.Note;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class NoteQueryService extends ServiceImpl<NoteMapper, Note> {

    public List<Note> search(Long userId, String keyword, int limit) {
        LambdaQueryWrapper<Note> wrapper = new LambdaQueryWrapper<Note>()
                .eq(Note::getUserId, userId)
                .like(Note::getTitle, keyword)
                .or()
                .like(Note::getContent, keyword)
                .orderByDesc(Note::getLikes)
                .last("LIMIT " + limit);
        return baseMapper.selectList(wrapper);
    }
}
