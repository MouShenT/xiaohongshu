<template>
  <n-layout position="absolute">
    <n-layout-header bordered>
      <n-space align="center" style="height: 48px; padding: 0 20px;">
        <n-gradient-text type="success" :size="18">小红书 AI 运营平台</n-gradient-text>
        <div style="flex:1" />
        <n-menu v-model:value="activeKey" mode="horizontal" :options="menuOptions" />
        <n-button quaternary @click="handleLogout">退出</n-button>
      </n-space>
    </n-layout-header>
    <n-layout position="absolute" style="top: 48px; bottom: 0;">
      <n-layout-sider bordered content-style="padding: 16px;" width="200">
        <n-menu v-model:value="activeKey" :options="sidebarOptions" />
      </n-layout-sider>
      <n-layout content-style="padding: 20px; overflow-y: auto;">
        <router-view />
      </n-layout>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { h, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import { DashboardOutline, KeyOutline, TaskOutline, AnalyticsOutline } from '@vicons/ionicons5'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const activeKey = ref(route.name as string)

function renderIcon(icon: any) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuOptions = [
  { label: '数据看板', key: 'Dashboard', icon: renderIcon(DashboardOutline) },
  { label: '凭据管理', key: 'Credential', icon: renderIcon(KeyOutline) },
  { label: '任务管理', key: 'Task', icon: renderIcon(TaskOutline) },
  { label: '数据分析', key: 'Analysis', icon: renderIcon(AnalyticsOutline) },
]

const sidebarOptions = computed(() => menuOptions)

function handleLogout() {
  authStore.logout()
  router.push({ name: 'Login' })
}
</script>
