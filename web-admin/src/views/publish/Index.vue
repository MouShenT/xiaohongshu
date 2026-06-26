<template>
  <n-space vertical>
    <n-h2>笔记发布</n-h2>

    <!-- 状态切换 -->
    <n-tabs v-model:value="tab" type="line" @update:value="fetchDrafts">
      <n-tab name="DRAFT" tab="草稿" />
      <n-tab name="REVIEWING" tab="待审核" />
      <n-tab name="APPROVED" tab="已通过" />
      <n-tab name="SCHEDULED" tab="定时发布" />
      <n-tab name="PUBLISHED" tab="已发布" />
      <n-tab name="FAILED" tab="失败" />
    </n-tabs>

    <!-- 新建草稿 -->
    <n-button type="primary" @click="showCreate = true">新建草稿</n-button>

    <!-- 草稿列表 -->
    <n-data-table :columns="columns" :data="drafts" :loading="loading" />

    <!-- 新建/编辑草稿弹窗 -->
    <n-modal v-model:show="showCreate" title="编辑草稿" preset="card" style="width: 700px;" :mask-closable="false">
      <n-form>
        <n-form-item label="标题"><n-input v-model:value="form.title" placeholder="笔记标题" /></n-form-item>
        <n-form-item label="内容"><n-input v-model:value="form.content" type="textarea" rows="8" placeholder="正文内容" /></n-form-item>
        <n-form-item label="标签"><n-input v-model:value="form.tags" placeholder="用逗号分隔标签" /></n-form-item>
        <n-form-item label="图片URLs"><n-input v-model:value="form.images" type="textarea" rows="3" placeholder="每行一个图片URL" /></n-form-item>
      </n-form>
      <n-space justify="end">
        <n-button @click="showCreate = false">取消</n-button>
        <n-button type="primary" :loading="saving" @click="handleSave">保存草稿</n-button>
      </n-space>
    </n-modal>
  </n-space>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, h } from 'vue'
import { useMessage } from 'naive-ui'
import { NButton, NSpace, NTag, NPopconfirm } from 'naive-ui'
import type { DataTableColumn } from 'naive-ui'
import http from '@/utils/http'

const message = useMessage()
const tab = ref('DRAFT')
const drafts = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)

const form = reactive({ title: '', content: '', tags: '', images: '' })

const statusMap: Record<string, { label: string; type: 'default' | 'info' | 'success' | 'warning' | 'error' }> = {
  DRAFT: { label: '草稿', type: 'default' },
  REVIEWING: { label: '审核中', type: 'info' },
  APPROVED: { label: '已通过', type: 'success' },
  SCHEDULED: { label: '定时发布', type: 'warning' },
  PUBLISHED: { label: '已发布', type: 'success' },
  PUBLISHING: { label: '发布中', type: 'info' },
  FAILED: { label: '失败', type: 'error' },
  REJECTED: { label: '已驳回', type: 'error' },
}

const columns: DataTableColumn[] = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '标题', key: 'title', ellipsis: { tooltip: true } },
  {
    title: '状态', key: 'status', width: 100,
    render: (r: any) => {
      const s = statusMap[r.status] || { label: r.status, type: 'default' }
      return h(NTag, { type: s.type as any, size: 'small' }, { default: () => s.label })
    },
  },
  { title: '标签', key: 'tags', ellipsis: { tooltip: true } },
  {
    title: '创建时间', key: 'createdAt', width: 170,
    render: (r: any) => r.createdAt?.replace('T', ' ') || '',
  },
  {
    title: '操作', key: 'actions', width: 220,
    render: (r: any) => h(NSpace, null, {
      default: () => [
        r.status === 'DRAFT' && h(NButton, { size: 'tiny', onClick: () => editDraft(r) }, { default: () => '编辑' }),
        r.status === 'DRAFT' && h(NButton, { size: 'tiny', onClick: () => submitDraft(r.id) }, { default: () => '提交审核' }),
        r.status === 'APPROVED' && h(NButton, { size: 'tiny', type: 'primary', onClick: () => publishDraft(r.id) }, { default: () => '发布' }),
        r.status === 'FAILED' && h(NButton, { size: 'tiny', onClick: () => retryPublish(r.id) }, { default: () => '重试' }),
        h(NPopconfirm, { onPositiveClick: () => deleteDraft(r.id) }, { default: () => '确定删除?', trigger: () => h(NButton, { size: 'tiny', type: 'error' }, { default: () => '删除' }) }),
      ]
    }),
  },
]

async function fetchDrafts() {
  loading.value = true
  try {
    const res: any = await http.get('/publish/draft', { params: { status: tab.value } })
    drafts.value = res.data || []
  } finally {
    loading.value = false
  }
}

function editDraft(draft: any) {
  editingId.value = draft.id
  form.title = draft.title || ''
  form.content = draft.content || ''
  form.tags = draft.tags || ''
  form.images = (draft.images || '').split(',').join('\n')
  showCreate.value = true
}

async function handleSave() {
  saving.value = true
  try {
    const images = form.images.split('\n').filter(Boolean).join(',')
    if (editingId.value) {
      await http.put(`/publish/draft/${editingId.value}`, { ...form, images })
      message.success('草稿已更新')
    } else {
      await http.post('/publish/draft', { ...form, images })
      message.success('草稿已创建')
    }
    showCreate.value = false
    editingId.value = null
    resetForm()
    fetchDrafts()
  } finally {
    saving.value = false
  }
}

function resetForm() {
  form.title = ''
  form.content = ''
  form.tags = ''
  form.images = ''
}

async function submitDraft(id: number) {
  await http.post(`/publish/draft/${id}/submit`)
  message.success('已提交审核')
  fetchDrafts()
}

async function publishDraft(id: number) {
  await http.post(`/publish/draft/${id}/publish`, {})
  message.success('发布成功')
  fetchDrafts()
}

async function retryPublish(id: number) {
  await http.post(`/publish/draft/${id}/publish`, {})
  message.success('已重试')
  fetchDrafts()
}

async function deleteDraft(id: number) {
  await http.delete(`/publish/draft/${id}`)
  message.success('已删除')
  fetchDrafts()
}

onMounted(fetchDrafts)
</script>
