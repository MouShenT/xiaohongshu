<template>
  <n-space vertical>
    <n-h2>凭据管理</n-h2>
    <n-button type="success" @click="showAdd = true">新增凭据</n-button>
    <n-data-table :columns="columns" :data="list" :loading="loading" />
    <n-modal v-model:show="showAdd" title="新增凭据" preset="card" style="width: 500px;">
      <n-form>
        <n-form-item label="名称"><n-input v-model:value="form.name" /></n-form-item>
        <n-form-item label="Cookies"><n-input v-model:value="form.cookies" type="textarea" rows="6" /></n-form-item>
        <n-button type="success" @click="handleAdd">保存</n-button>
      </n-form>
    </n-modal>
  </n-space>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useMessage } from 'naive-ui'
import { credentialApi } from '@/api/analysis'
import type { DataTableColumn } from 'naive-ui'

const message = useMessage()
const list = ref<any[]>([])
const loading = ref(false)
const showAdd = ref(false)
const form = reactive({ name: '', cookies: '' })

const columns: DataTableColumn[] = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name' },
  { title: '状态', key: 'isValid', render: (r: any) => r.isValid ? '有效' : '无效' },
  { title: '创建时间', key: 'createdAt' },
]

async function fetchList() {
  loading.value = true
  try {
    const res: any = await credentialApi.list()
    list.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function handleAdd() {
  await credentialApi.create(form.name, form.cookies)
  message.success('添加成功')
  showAdd.value = false
  fetchList()
}

onMounted(fetchList)
</script>
