<template>
  <n-space vertical>
    <n-h2>笔记浏览</n-h2>

    <!-- 搜索栏 -->
    <n-space>
      <n-input v-model:value="keyword" placeholder="搜索关键词" style="width: 300px" clearable @keyup.enter="handleSearch" />
      <n-select v-model:value="sort" :options="sortOptions" style="width: 140px" />
      <n-button type="primary" :loading="searching" @click="handleSearch">搜索</n-button>
    </n-space>

    <!-- 搜索结果统计 -->
    <n-text v-if="total > 0" depth="3">共找到 {{ total }} 条结果</n-text>

    <!-- 瀑布流布局 -->
    <n-skeleton v-if="searching" :sharp="false" size="medium" repeat="6" style="margin-top: 8px" />
    <n-empty v-else-if="!searching && notes.length === 0" description="暂无数据，输入关键词搜索" style="margin-top: 60px" />

    <n-grid v-else :cols="cols" x-gap="12" y-gap="16">
      <n-grid-item v-for="note in notes" :key="note.note_id">
        <n-card hoverable :title="note.title" size="small" @click="openDetail(note.note_id)" style="cursor: pointer; height: 100%;">
          <template #cover>
            <img v-if="note.images && note.images[0]" :src="note.images[0]" alt="cover" style="height: 180px; object-fit: cover; width: 100%;" />
            <div v-else style="height: 180px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #ccc;">
              暂无封面
            </div>
          </template>
          <n-ellipsis :line-clamp="2" style="max-width: 100%; font-size: 13px; margin-bottom: 8px;">
            {{ note.content || note.title }}
          </n-ellipsis>
          <n-space justify="space-between" style="font-size: 12px; color: #888;">
            <span>{{ note.author || '未知作者' }}</span>
            <n-space>
              <span>❤️ {{ note.likes }}</span>
              <span>⭐ {{ note.collects }}</span>
              <span>💬 {{ note.comments }}</span>
            </n-space>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 笔记详情抽屉 -->
    <n-drawer v-model:show="showDetail" :width="640" placement="right">
      <n-drawer-content :title="detailNote?.title || '笔记详情'" closable>
        <template v-if="detailLoading">
          <n-skeleton :sharp="false" repeat="8" />
        </template>
        <template v-else-if="detailNote">
          <n-descriptions label-placement="left" bordered :column="1" size="small">
            <n-descriptions-item label="作者">{{ detailNote.author }}</n-descriptions-item>
            <n-descriptions-item label="点赞">{{ detailNote.likes }}</n-descriptions-item>
            <n-descriptions-item label="收藏">{{ detailNote.collects }}</n-descriptions-item>
            <n-descriptions-item label="评论">{{ detailNote.comments }}</n-descriptions-item>
            <n-descriptions-item label="分享">{{ detailNote.shares }}</n-descriptions-item>
          </n-descriptions>

          <n-divider />

          <n-h4>正文内容</n-h4>
          <n-text>{{ detailNote.content || '暂无内容' }}</n-text>

          <n-divider v-if="comments.length > 0" />

          <n-h4>热门评论 ({{ comments.length }})</n-h4>
          <n-space vertical>
            <n-card v-for="c in comments.slice(0, 10)" :key="c.comment_id" size="small">
              <n-space justify="space-between">
                <n-text depth="3">{{ c.author }}</n-text>
                <n-text depth="3" style="font-size: 12px;">👍 {{ c.likes }}</n-text>
              </n-space>
              <n-text>{{ c.content }}</n-text>
            </n-card>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </n-space>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { noteApi } from '@/api/analysis'
import { useBreakpoint } from 'naive-ui'

const message = useMessage()
const bk = useBreakpoint()

const keyword = ref('')
const sort = ref('general')
const sortOptions = [
  { label: '综合排序', value: 'general' },
  { label: '最热', value: 'popularity_descending' },
  { label: '最新', value: 'time_descending' },
]
const notes = ref<any[]>([])
const searching = ref(false)
const total = ref(0)
const cols = computed(() => {
  const b = bk.value
  if (b === 'xs' || b === 's') return 1
  if (b === 'm') return 2
  if (b === 'l') return 3
  return 4
})

// 详情抽屉
const showDetail = ref(false)
const detailNote = ref<any>(null)
const detailLoading = ref(false)
const comments = ref<any[]>([])

async function handleSearch() {
  if (!keyword.value) { message.warning('请输入关键词'); return }
  searching.value = true
  try {
    const res: any = await noteApi.search({ keyword: keyword.value, sort: sort.value })
    notes.value = res.data || []
    total.value = res.total || notes.value.length
  } catch (e: any) {
    message.error(e?.message || '搜索失败')
  } finally {
    searching.value = false
  }
}

async function openDetail(noteId: string) {
  showDetail.value = true
  detailLoading.value = true
  detailNote.value = null
  comments.value = []
  try {
    const [detailRes, commentRes]: any = await Promise.all([
      noteApi.detail(noteId),
      noteApi.comments(noteId, 50),
    ])
    detailNote.value = detailRes.data
    comments.value = commentRes.data || []
  } catch (e: any) {
    message.error(e?.message || '获取详情失败')
  } finally {
    detailLoading.value = false
  }
}
</script>
