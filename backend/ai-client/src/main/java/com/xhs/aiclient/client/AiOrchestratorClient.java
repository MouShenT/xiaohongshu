package com.xhs.aiclient.client;

import com.xhs.common.result.Result;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.Map;

@Component
public class AiOrchestratorClient {

    private final WebClient webClient;

    public AiOrchestratorClient() {
        this.webClient = WebClient.builder()
                .baseUrl("http://localhost:8000")
                .build();
    }

    public String health() {
        return webClient.get()
                .uri("/health")
                .retrieve()
                .bodyToMono(String.class)
                .block();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> searchNotes(String keyword, int limit, String sort) {
        return webClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/api/v1/xhs/search")
                        .queryParam("keyword", keyword)
                        .queryParam("limit", limit)
                        .queryParam("sort", sort)
                        .build())
                .retrieve()
                .bodyToMono(Map.class)
                .block();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> getNoteDetail(String noteId) {
        return webClient.get()
                .uri("/api/v1/xhs/note/{noteId}", noteId)
                .retrieve()
                .bodyToMono(Map.class)
                .block();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> getComments(String noteId, int limit) {
        return webClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/api/v1/xhs/note/{noteId}/comments")
                        .queryParam("limit", limit)
                        .build(noteId))
                .retrieve()
                .bodyToMono(Map.class)
                .block();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> getHotTopics(int limit) {
        return webClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/api/v1/xhs/hot-topics")
                        .queryParam("limit", limit)
                        .build())
                .retrieve()
                .bodyToMono(Map.class)
                .block();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> analyzeTrend(String keyword) {
        return webClient.post()
                .uri("/api/v1/analysis/hot-radar/analyze")
                .bodyValue(Map.of("keyword", keyword))
                .retrieve()
                .bodyToMono(Map.class)
                .block();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> analyzeArticle(String noteId) {
        return webClient.post()
                .uri("/api/v1/analysis/article/analyze")
                .bodyValue(Map.of("noteId", noteId))
                .retrieve()
                .bodyToMono(Map.class)
                .block();
    }
}
