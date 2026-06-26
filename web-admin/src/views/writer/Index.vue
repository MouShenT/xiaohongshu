<template>
  <n-space vertical>
    <n-h2>AI 创作</n-h2>

    <n-grid :cols="2" x-gap="16">
      <!-- 标题生成 -->
      <n-grid-item>
        <n-card title="标题生成">
          <n-space vertical>
            <n-input v-model:value="titleTopic" placeholder="输入主题" />
            <n-button type="primary" :loading="loadingTitles" @click="handleGenerateTitles">生成标题</n-button>
            <n-list v-if="titles.length">
              <n-list-item v-for="(t, i) in titles" :key="i">
                <n-thing>
                  <n-text>{{ t }}</n-text>
                  <template #action>
                    <n-button size="tiny" @click="useTitle(t)">采用</n-button>
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>
          </n-space>
        </n-card>
      </n-grid-item>

      <!-- 正文生成 -->
      <n-grid-item>
        <n-card title="正文生成">
          <n-space vertical>
            <n-input v-model:value="contentTopic" placeholder="输入主题" />
            <n-select v-model:value="contentStyle" :options="styleOptions" />
            <n-button type="primary" :loading="loadingContent" @click="handleGenerateContent">生成正文</n-button>
            <n-card v-if="content" size="small">
              <div style="white-space: pre-wrap;">{{ content }}</div>
              <template #action>
                <n-button size="tiny" @click="useContent">保存为草稿</n-button>
              </template>
            </n-card>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 完整草稿生成 -->
    <n-card title="完整草稿生成">
      <n-space vertical>
        <n-input v-model:value="draftTitle" placeholder="输入标题" />
        <n-input v-model:value="draftOutline" type="textarea" rows="4" placeholder="输入大纲要点，每行一个..." />
        <n-button type="success" :loading="loadingDraft" @click="handleGenerateDraft">生成完整草稿</n-button>

        <n-spin :show="loadingDraft" v-if="draftResult">
          <n-h4>{{ draftResult.title }}</n-h4>
          <div style="white-space: pre-wrap;">{{ draftResult.content }}</div>
          <n-space v-if="draftResult.tags?.length" style="margin-top: 8px;">
            <n-tag v-for="tag in draftResult.tags" :key="tag">{{ tag }}</n-tag>
          </n-space>
          <template #action>
            <n-button type="primary" @click="saveDraftToPublish">保存到发布</n-button>
          </template>
        </n-spin>
      </n-space>
    </n-card>
  </n-space>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'
import http from '@/utils/http'

const message = useMessage()
const router = useRouter()

// 标题
const titleTopic = ref('')
const loadingTitles = ref(false)
const titles = ref<string[]>([])

// 正文
const contentTopic = ref('')
const contentStyle = ref('教程')
const styleOptions = [
  { label: '教程类', value: '教程' },
  { label: '测评类', value: '测评' },
  { label: '种草类', value: '种草' },
  { label: '干货分享', value: '干货' },
  { label: 'Vlog文案', value: 'Vlog' },
]
const loadingContent = ref(false)
const content = ref('')

// 完整草稿
const draftTitle = ref('')
const draftOutline = ref('')
const loadingDraft = ref(false)
const draftResult = ref<any>(null)

// 保存状态
const savedTitle = ref('')
const savedContent = ref('')

async function handleGenerateTitles() {
  if (!titleTopic.value) { message.warning('请输入主题'); return }
  loadingTitles.value = true
  try {
    const res: any = await http.post('/ai/writer/titles', { topic: titleTopic.value })
    titles.value = res.data || []
  } catch { message.error('生成失败，AI 服务未就绪') }
  finally { loadingTitles.value = false }
}

function useTitle(t: string) {
  savedTitle.value = t
  draftTitle.value = t
  message.success('已采用标题')
}

async function handleGenerateContent() {
  if (!contentTopic.value) { message.warning('请输入主题'); return }
  loadingContent.value = true
  try {
    const res: any = await http.post('/ai/writer/content', {
      topic: contentTopic.value,
      style: contentStyle.value,
    })
    content.value = res.data || ''
  } catch { message.error('生成失败，AI 服务未就绪') }
  finally { loadingContent.value = false }
}

function useContent() {
  savedContent.value = content.value
  draftContent.value = savedContent.value
  // navigates to publish page
  message.success('内容已保存，可前往发布页面继续编辑')
}

const draftContent = ref('')

async function handleGenerateDraft() {
  if (!draftTitle.value) { message.warning('请输入标题'); return }
  loadingDraft.value = true
  try {
    const res: any = await http.post('/ai/writer/draft', {
      title: draftTitle.value,
      outline: draftOutline.value,
    })
    draftResult.value = res.data
  } catch { message.error('生成失败，AI 服务未就绪') }
  finally { loadingDraft.value = false }
}

async function saveDraftToPublish() {
  if (!draftResult.value) return
  try {
    const tags = (draftResult.value.tags || []).map((t: string) => t.replace('#', '')).join(',')
    await http.post('/publish/draft', {
      title: draftResult.value.title,
      content: draftResult.value.content,
      tags,
    })
    message.success('草稿已保存到发布页面')
    router.push({ name: 'Publish' })
  } catch (e: any) {
    message.error(e?.message || '保存失败')
  }
}
</script>
