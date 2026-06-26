<template>
  <n-space vertical>
    <n-h2>数据看板</n-h2>
    <n-grid :cols="4" x-gap="16">
      <n-grid-item>
        <n-card title="笔记总数">
          <n-h1 style="color: #18a058;">--</n-h1>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="今日采集">
          <n-h1 style="color: #2080f0;">--</n-h1>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="进行中任务">
          <n-h1 style="color: #f0a020;">--</n-h1>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="待发布草稿">
          <n-h1 style="color: #d03050;">--</n-h1>
        </n-card>
      </n-grid-item>
    </n-grid>
  </n-space>
</template>
