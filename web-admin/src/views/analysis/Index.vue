<template>
  <n-space vertical>
    <n-h2>数据分析</n-h2>
    <n-grid :cols="2" x-gap="16">
      <n-grid-item>
        <n-card title="热点雷达">
          <n-space>
            <n-input v-model:value="keyword" placeholder="输入关键词" />
            <n-button type="success" :loading="analyzing" @click="handleAnalyze">分析</n-button>
          </n-space>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="爆文拆解">
          <n-space>
            <n-input v-model:value="noteId" placeholder="输入笔记ID" />
            <n-button type="primary">拆解</n-button>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>
  </n-space>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import { hotRadarApi } from '@/api/analysis'

const message = useMessage()
const keyword = ref('')
const noteId = ref('')
const analyzing = ref(false)

async function handleAnalyze() {
  if (!keyword.value) { message.warning('请输入关键词'); return }
  analyzing.value = true
  try {
    const res: any = await hotRadarApi.analyze(keyword.value)
    message.success(`分析任务已创建: ID=${res.data}`)
  } finally {
    analyzing.value = false
  }
}
</script>
