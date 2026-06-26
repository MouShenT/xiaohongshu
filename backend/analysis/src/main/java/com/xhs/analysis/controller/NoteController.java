package com.xhs.analysis.controller;

import com.xhs.common.result.Result;
import com.xhs.analysis.model.entity.Note;
import com.xhs.analysis.service.NoteQueryService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/note")
public class NoteController {

    private final NoteQueryService noteQueryService;

    public NoteController(NoteQueryService noteQueryService) {
        this.noteQueryService = noteQueryService;
    }

    @GetMapping("/search")
    public Result<List<Note>> search(@AuthenticationPrincipal Long userId,
                                     @RequestParam String keyword,
                                     @RequestParam(defaultValue = "20") int limit) {
        return Result.success(noteQueryService.search(userId, keyword, limit));
    }

    @GetMapping("/{id}")
    public Result<Note> detail(@AuthenticationPrincipal Long userId,
                               @PathVariable Long id) {
        return Result.success(noteQueryService.getById(id));
    }
}
