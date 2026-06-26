<template>
  <n-space vertical>
    <n-h2>任务管理</n-h2>
    <n-button type="success" @click="showCreate = true">创建任务</n-button>
    <n-data-table :columns="columns" :data="list" :loading="loading" />
    <n-modal v-model:show="showCreate" title="创建任务" preset="card" style="width: 500px;">
      <n-form>
        <n-form-item label="任务类型">
          <n-select v-model:value="form.type" :options="[
            { label: '热点雷达', value: 'HOT_RADAR' },
            { label: '笔记采集', value: 'NOTE_COLLECT' },
            { label: '数据分析', value: 'ANALYZE' },
          ]" />
        </n-form-item>
        <n-form-item label="关键词"><n-input v-model:value="form.keyword" /></n-form-item>
        <n-button type="success" @click="handleCreate">创建</n-button>
      </n-form>
    </n-modal>
  </n-space>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useMessage } from 'naive-ui'
import { taskApi } from '@/api/analysis'
import type { DataTableColumn } from 'naive-ui'

const message = useMessage()
const list = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const form = reactive({ type: 'HOT_RADAR', keyword: '' })

const columns: DataTableColumn[] = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '类型', key: 'type' },
  { title: '状态', key: 'status' },
  { title: '进度', key: 'progress' },
  { title: '创建时间', key: 'createdAt' },
]

async function handleCreate() {
  await taskApi.create({
    type: form.type,
    params: { keyword: form.keyword },
  })
  message.success('任务已创建')
  showCreate.value = false
}

onMounted(() => {})
</script>
