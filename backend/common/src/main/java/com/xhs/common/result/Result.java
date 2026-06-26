package com.xhs.common.result;

import lombok.Getter;

@Getter
public class Result<T> {

    private final int code;
    private final String message;
    private final T data;

    private Result(int code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
    }

    public static <R> Result<R> success(R data) {
        return new Result<>(200, "success", data);
    }

    @SuppressWarnings("unchecked")
    public static <R> Result<R> success() {
        return (Result<R>) new Result<>(200, "success", null);
    }

    @SuppressWarnings("unchecked")
    public static <R> Result<R> error(int code, String message) {
        return (Result<R>) new Result<>(code, message, null);
    }

    @SuppressWarnings("unchecked")
    public static <R> Result<R> error(String message) {
        return (Result<R>) new Result<>(500, message, null);
    }

    @SuppressWarnings("unchecked")
    public static <R> Result<R> unauthorized(String message) {
        return (Result<R>) new Result<>(401, message, null);
    }

    @SuppressWarnings("unchecked")
    public static <R> Result<R> forbidden(String message) {
        return (Result<R>) new Result<>(403, message, null);
    }
}
