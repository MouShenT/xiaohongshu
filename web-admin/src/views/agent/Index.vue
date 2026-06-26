<template>
  <n-space vertical style="height: calc(100vh - 120px);">
    <n-h2>AI 智能体</n-h2>
    <n-layout has-sider style="height: 100%;" position="absolute">
      <!-- 对话列表 -->
      <n-layout-sider bordered width="240" style="padding: 12px;">
        <n-space vertical>
          <n-button type="primary" @click="currentConversation = null; messages = []; input = ''">新对话</n-button>
          <n-menu :options="conversationMenu" @update:value="loadConversation" />
        </n-space>
      </n-layout-sider>

      <!-- 聊天区域 -->
      <n-layout>
        <!-- 消息列表 -->
        <div ref="chatContainer" style="flex: 1; overflow-y: auto; padding: 16px;">
          <n-empty v-if="messages.length === 0" description="开始与 AI 智能体对话" style="margin-top: 80px;" />
          <n-space vertical v-else>
            <div v-for="(msg, i) in messages" :key="i" :style="{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start', marginBottom: '16px' }">
              <n-card v-if="msg.type === 'note'" size="small" style="max-width: 80%; cursor: pointer;" @click="openNote(msg.content.note_id)">
                <n-text strong>{{ msg.content.title }}</n-text>
                <n-text depth="3" style="display: block;">作者: {{ msg.content.author }}</n-text>
                <n-space style="margin-top: 4px;">
                  <n-tag size="tiny">❤️ {{ msg.content.likes }}</n-tag>
                  <n-tag size="tiny">⭐ {{ msg.content.collects }}</n-tag>
                  <n-tag size="tiny">💬 {{ msg.content.comments }}</n-tag>
                </n-space>
              </n-card>
              <n-card v-else :style="{ maxWidth: '80%', background: msg.role === 'user' ? '#18a05810' : '#f5f5f5' }">
                <div style="white-space: pre-wrap;">{{ msg.content }}</div>
              </n-card>
            </div>
            <n-spin v-if="loading" size="small" />
          </n-space>
        </div>

        <!-- 输入区域 -->
        <n-layout-footer bordered style="padding: 12px;">
          <n-space>
            <n-input v-model:value="input" type="textarea" :rows="2" placeholder="输入消息..." @keyup.enter="sendMessage" />
            <n-button type="primary" :loading="loading" @click="sendMessage" style="align-self: flex-end;">发送</n-button>
          </n-space>
        </n-layout-footer>
      </n-layout>
    </n-layout>
  </n-space>
</template>

<script setup lang="ts">
import { ref, nextTick, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'
import http from '@/utils/http'

const message = useMessage()
const router = useRouter()
const input = ref('')
const messages = ref<Array<{ role: string; content: string | any; type?: string }>>([])
const loading = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
const conversations = ref<Array<{ id: string; title: string }>>([])
const currentConversation = ref<string | null>(null)

const conversationMenu = computed(() => {
  return conversations.value.map(c => ({
    label: c.title,
    key: c.id,
  }))
})

async function sendMessage() {
  const text = input.value.trim()
  if (!text) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  loading.value = true
  scrollToBottom()

  try {
    const res = await fetch('http://localhost:8000/api/v1/agent/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        conversation_id: currentConversation.value,
        history: messages.value.filter(m => m.type !== 'note').map(m => ({ role: m.role, content: m.content })),
      }),
    })

    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim()
          if (data === '[DONE]') continue
          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'intent') continue

            if (parsed.type === 'note') {
              messages.value.push({ role: 'assistant', content: parsed.content, type: 'note' })
            } else {
              const last = messages.value[messages.value.length - 1]
              if (last?.role === 'assistant' && last.type !== 'note') {
                last.content += parsed.content
              } else {
                messages.value.push({ role: 'assistant', content: parsed.content })
              }
            }
            scrollToBottom()
          } catch { /* skip partial */ }
        }
      }
    }
  } catch (e: any) {
    message.error('连接失败: ' + (e.message || '无法连接到 AI 服务'))
    messages.value.push({ role: 'assistant', content: '抱歉，连接 AI 服务失败，请确认 Python 服务已启动 (python-agent/main.py)' })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

function openNote(noteId: string) {
  router.push({ name: 'Notes' })
  message.info(`笔记ID: ${noteId}，请在笔记浏览页面查看`)
}

function loadConversation(key: string) {
  currentConversation.value = key
  messages.value = [
    { role: 'assistant', content: '继续之前的对话...' },
  ]
}
</script>
