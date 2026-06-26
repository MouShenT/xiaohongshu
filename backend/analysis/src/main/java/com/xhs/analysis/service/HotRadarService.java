package com.xhs.analysis.service;

import java.util.List;
import java.util.Map;

public interface HotRadarService {

    List<Map<String, Object>> getTrending(Long userId, int limit);

    Long createAnalysisTask(Long userId, String keyword);
}
