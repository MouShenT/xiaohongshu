<template>
  <n-space vertical>
    <n-h2>数据看板</n-h2>

    <!-- 统计卡片 -->
    <n-grid :cols="4" x-gap="16">
      <n-grid-item>
        <n-card title="笔记总数">
          <n-h1 style="color: #18a058;">{{ stats.noteCount ?? '--' }}</n-h1>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="今日采集">
          <n-h1 style="color: #2080f0;">{{ stats.todayCollect ?? '--' }}</n-h1>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="进行中任务">
          <n-h1 style="color: #f0a020;">{{ stats.runningTasks ?? '--' }}</n-h1>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="待发布草稿">
          <n-h1 style="color: #d03050;">{{ stats.pendingDrafts ?? '--' }}</n-h1>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-grid :cols="2" x-gap="16">
      <!-- 任务趋势 -->
      <n-grid-item>
        <n-card title="任务趋势（近7天）">
          <n-data-table v-if="taskTrend.length" :columns="trendColumns" :data="taskTrend" size="small" :max-height="300" />
          <n-empty v-else description="暂无数据" style="padding: 40px" />
        </n-card>
      </n-grid-item>

      <!-- 热门笔记排行 -->
      <n-grid-item>
        <n-card title="热门笔记 TOP10">
          <n-data-table v-if="topNotes.length" :columns="topNoteColumns" :data="topNotes" size="small" :max-height="300" />
          <n-empty v-else description="暂无数据" style="padding: 40px" />
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-grid :cols="2" x-gap="16">
      <!-- 任务分布 -->
      <n-grid-item>
        <n-card title="任务状态分布">
          <n-empty v-if="!distributions.byStatus" description="暂无数据" style="padding: 40px" />
          <n-data-table v-else :columns="distStatusColumns" :data="distStatusData" size="small" />
        </n-card>
      </n-grid-item>

      <!-- 任务类型分布 -->
      <n-grid-item>
        <n-card title="任务类型分布">
          <n-empty v-if="!distributions.byType" description="暂无数据" style="padding: 40px" />
          <n-data-table v-else :columns="distTypeColumns" :data="distTypeData" size="small" />
        </n-card>
      </n-grid-item>
    </n-grid>
  </n-space>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, h } from 'vue'
import { NTag } from 'naive-ui'
import type { DataTableColumn } from 'naive-ui'
import http from '@/utils/http'

const stats = ref<Record<string, number>>({})
const taskTrend = ref<any[]>([])
const topNotes = ref<any[]>([])
const distributions = ref<Record<string, any>>({})

const trendColumns: DataTableColumn[] = [
  { title: '日期', key: 'date' },
  { title: '总数', key: 'total' },
  { title: '成功', key: 'success', render: (r: any) => h(NTag, { type: 'success', size: 'small' }, { default: () => r.success }) },
  { title: '失败', key: 'failed', render: (r: any) => h(NTag, { type: 'error', size: 'small' }, { default: () => r.failed }) },
]

const topNoteColumns: DataTableColumn[] = [
  { title: '标题', key: 'title', ellipsis: { tooltip: true } },
  { title: '点赞', key: 'likes' },
  { title: '收藏', key: 'collects' },
  { title: '评论', key: 'comments' },
]

const distStatusColumns: DataTableColumn[] = [
  { title: '状态', key: 'status' },
  { title: '数量', key: 'count' },
]

const distTypeColumns: DataTableColumn[] = [
  { title: '类型', key: 'type' },
  { title: '数量', key: 'count' },
]

const distStatusData = computed(() => {
  const m = distributions.value.byStatus || {}
  return Object.entries(m).map(([k, v]) => ({ status: k, count: v }))
})

const distTypeData = computed(() => {
  const m = distributions.value.byType || {}
  return Object.entries(m).map(([k, v]) => ({ type: k, count: v }))
})

async function fetchDashboard() {
  try {
    const [statsRes, trendRes, topRes, distRes]: any = await Promise.all([
      http.get('/dashboard/stats'),
      http.get('/dashboard/task-trend'),
      http.get('/dashboard/top-notes'),
      http.get('/dashboard/distributions'),
    ])
    stats.value = statsRes.data || {}
    taskTrend.value = trendRes.data || []
    topNotes.value = topRes.data || []
    distributions.value = distRes.data || {}
  } catch (e) {
    // Silently handle — services may not be fully wired
  }
}

onMounted(fetchDashboard)
</script>
