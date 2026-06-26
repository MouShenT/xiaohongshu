<template>
  <n-space vertical>
    <n-h2>数据分析</n-h2>
    <n-grid :cols="2" x-gap="16" y-gap="16">
      <!-- 热点雷达 -->
      <n-grid-item>
        <n-card title="热点雷达">
          <n-space vertical>
            <n-space>
              <n-input v-model:value="keyword" placeholder="输入关键词" />
              <n-button type="success" :loading="analyzing" @click="handleAnalyze">分析</n-button>
            </n-space>

            <!-- 分析结果 -->
            <n-spin :show="analyzing" v-if="trendResult">
              <n-descriptions label-placement="left" bordered :column="1" size="small">
                <n-descriptions-item label="关键词">{{ trendResult.keyword }}</n-descriptions-item>
                <n-descriptions-item label="热度分">{{ trendResult.score }}</n-descriptions-item>
                <n-descriptions-item label="趋势方向">
                  <n-tag v-if="trendResult.trend === 'rising'" type="success">上升</n-tag>
                  <n-tag v-else-if="trendResult.trend === 'falling'" type="warning">下降</n-tag>
                  <n-tag v-else>平稳</n-tag>
                </n-descriptions-item>
                <n-descriptions-item label="相关笔记">{{ trendResult.total_notes }}</n-descriptions-item>
                <n-descriptions-item label="平均点赞">{{ trendResult.avg_likes }}</n-descriptions-item>
                <n-descriptions-item label="平均收藏">{{ trendResult.avg_collects }}</n-descriptions-item>
                <n-descriptions-item label="平均评论">{{ trendResult.avg_comments }}</n-descriptions-item>
              </n-descriptions>

              <n-divider />
              <n-h4>运营建议</n-h4>
              <n-space vertical>
                <n-alert v-for="(s, i) in trendResult.suggestions" :key="i" :title="`建议 ${i + 1}`" type="info" closable>
                  {{ s }}
                </n-alert>
              </n-space>
            </n-spin>

            <!-- 热门排行 -->
            <n-divider />
            <n-space justify="space-between">
              <n-h4 style="margin: 0">热门笔记排行</n-h4>
              <n-button text type="primary" :loading="loadingTrending" @click="fetchTrending">刷新</n-button>
            </n-space>
            <n-data-table :columns="trendingColumns" :data="trendingList" :loading="loadingTrending" :max-height="400" size="small" />
          </n-space>
        </n-card>
      </n-grid-item>

      <!-- 爆文拆解 -->
      <n-grid-item>
        <n-card title="爆文拆解">
          <n-space vertical>
            <n-space>
              <n-input v-model:value="noteId" placeholder="输入笔记ID" />
              <n-button type="primary" :loading="analyzingArticle" @click="handleAnalyzeArticle">拆解</n-button>
            </n-space>

            <n-spin :show="analyzingArticle" v-if="articleResult && !articleResult.error">
              <n-descriptions label-placement="left" bordered :column="1" size="small">
                <n-descriptions-item label="标题">{{ articleResult.title }}</n-descriptions-item>
                <n-descriptions-item label="作者">{{ articleResult.author }}</n-descriptions-item>
                <n-descriptions-item label="综合评分">
                  <n-progress type="line" :percentage="articleResult.scores.overall" :height="20" />
                </n-descriptions-item>
                <n-descriptions-item label="标题评分">
                  <n-progress type="line" :percentage="articleResult.scores.title_score" :height="16" />
                </n-descriptions-item>
              </n-descriptions>

              <n-divider />
              <n-h4>互动数据</n-h4>
              <n-descriptions label-placement="left" bordered :column="2" size="small">
                <n-descriptions-item label="点赞">{{ articleResult.engagement.likes }}</n-descriptions-item>
                <n-descriptions-item label="收藏">{{ articleResult.engagement.collects }}</n-descriptions-item>
                <n-descriptions-item label="评论">{{ articleResult.engagement.comments }}</n-descriptions-item>
                <n-descriptions-item label="分享">{{ articleResult.engagement.shares }}</n-descriptions-item>
              </n-descriptions>

              <n-divider />
              <n-h4>标题分析</n-h4>
              <n-tag v-if="articleResult.title_analysis.has_number" type="info" style="margin-right: 4px;">含数字</n-tag>
              <n-tag v-if="articleResult.title_analysis.has_question" type="warning" style="margin-right: 4px;">疑问句式</n-tag>
              <n-tag v-if="articleResult.title_analysis.has_emoji" type="success">含表情</n-tag>
              <n-text depth="3" style="margin-left: 8px;">长度: {{ articleResult.title_analysis.length }}字</n-text>
            </n-spin>
          </n-space>
        </n-card>
      </n-grid-item>

      <!-- 评论洞察 -->
      <n-grid-item>
        <n-card title="评论洞察">
          <n-space>
            <n-input v-model:value="commentNoteId" placeholder="输入笔记ID" />
            <n-button type="warning" :loading="analyzingComments" @click="handleAnalyzeComments">分析</n-button>
          </n-space>
          <n-spin :show="analyzingComments" v-if="commentResult">
            <n-descriptions label-placement="left" bordered :column="1" size="small" style="margin-top: 12px;">
              <n-descriptions-item label="评论总数">{{ commentResult.total_comments }}</n-descriptions-item>
              <n-descriptions-item label="平均长度">{{ commentResult.avg_comment_length }}字</n-descriptions-item>
            </n-descriptions>
            <n-text v-if="commentResult.top_comment" depth="3" style="margin-top: 8px; display: block;">
              热门评论: {{ commentResult.top_comment }}
            </n-text>
          </n-spin>
        </n-card>
      </n-grid-item>

      <!-- 任务创建快捷入口 -->
      <n-grid-item>
        <n-card title="快捷操作">
          <n-space vertical>
            <n-button type="success" block @click="showCreateTask = true">创建采集任务</n-button>
            <n-button block @click="router.push({ name: 'Notes' })">浏览笔记</n-button>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 创建任务弹窗 -->
    <n-modal v-model:show="showCreateTask" title="创建采集任务" preset="card" style="width: 500px;">
      <n-form>
        <n-form-item label="关键词"><n-input v-model:value="taskKeyword" placeholder="输入采集关键词" /></n-form-item>
        <n-form-item label="任务类型">
          <n-select v-model:value="taskType" :options="[
            { label: '热点雷达', value: 'HOT_RADAR' },
            { label: '笔记采集', value: 'NOTE_COLLECT' },
            { label: '数据分析', value: 'ANALYZE' },
          ]" />
        </n-form-item>
        <n-button type="success" @click="handleCreateTask">创建</n-button>
      </n-form>
    </n-modal>
  </n-space>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { hotRadarApi, articleApi, taskApi } from '@/api/analysis'
import type { DataTableColumn } from 'naive-ui'

const router = useRouter()
const message = useMessage()

// 热点雷达
const keyword = ref('')
const analyzing = ref(false)
const trendResult = ref<any>(null)

// 热点排行
const loadingTrending = ref(false)
const trendingList = ref<any[]>([])
const trendingColumns: DataTableColumn[] = [
  { title: '标题', key: 'title', ellipsis: { tooltip: true } },
  { title: '赞', key: 'likes', width: 60, sorter: (a: any, b: any) => a.likes - b.likes },
  { title: '藏', key: 'collects', width: 60 },
  { title: '评', key: 'comments', width: 60 },
]

// 爆文拆解
const noteId = ref('')
const analyzingArticle = ref(false)
const articleResult = ref<any>(null)

// 评论洞察
const commentNoteId = ref('')
const analyzingComments = ref(false)
const commentResult = ref<any>(null)

// 创建任务
const showCreateTask = ref(false)
const taskKeyword = ref('')
const taskType = ref('HOT_RADAR')

async function handleAnalyze() {
  if (!keyword.value) { message.warning('请输入关键词'); return }
  analyzing.value = true
  trendResult.value = null
  try {
    const res: any = await hotRadarApi.analyze(keyword.value)
    // 如果返回的是 task ID，说明走的异步流程
    if (res.data && typeof res.data === 'object' && res.data.keyword) {
      trendResult.value = res.data
    } else {
      message.success(`分析任务已创建: ID=${res.data}`)
    }
  } finally {
    analyzing.value = false
  }
}

async function fetchTrending() {
  loadingTrending.value = true
  try {
    const res: any = await hotRadarApi.getTrending(20)
    trendingList.value = res.data || []
  } catch (e: any) {
    message.error(e?.message || '获取热门排行失败')
  } finally {
    loadingTrending.value = false
  }
}

async function handleAnalyzeArticle() {
  if (!noteId.value) { message.warning('请输入笔记ID'); return }
  analyzingArticle.value = true
  articleResult.value = null
  try {
    const res: any = await articleApi.analyze(noteId.value)
    articleResult.value = res.data
  } catch (e: any) {
    message.error(e?.message || '拆解失败')
  } finally {
    analyzingArticle.value = false
  }
}

async function handleAnalyzeComments() {
  if (!commentNoteId.value) { message.warning('请输入笔记ID'); return }
  analyzingComments.value = true
  commentResult.value = null
  try {
    const res: any = await taskApi.create({ type: 'COMMENT_INSIGHT', params: { noteId: commentNoteId.value } })
    message.success(`评论分析任务已创建: ID=${res.data}`)
  } catch (e: any) {
    message.error(e?.message || '创建任务失败')
  } finally {
    analyzingComments.value = false
  }
}

async function handleCreateTask() {
  if (!taskKeyword.value) { message.warning('请输入关键词'); return }
  await taskApi.create({ type: taskType.value, params: { keyword: taskKeyword.value } })
  message.success('任务已创建')
  showCreateTask.value = false
}
</script>
