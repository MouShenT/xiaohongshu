import { h } from 'vue'
import { NIcon } from 'naive-ui'
import { DashboardOutline, KeyOutline, TaskOutline, AnalyticsOutline, SearchOutline, PaperPlaneOutline, ChatboxEllipsesOutline } from '@vicons/ionicons5'
import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/dashboard/Index.vue'), meta: { title: '数据看板' } },
      { path: 'credential', name: 'Credential', component: () => import('@/views/credential/Index.vue'), meta: { title: '凭据管理' } },
      { path: 'task', name: 'Task', component: () => import('@/views/task/Index.vue'), meta: { title: '任务管理' } },
      { path: 'analysis', name: 'Analysis', component: () => import('@/views/analysis/Index.vue'), meta: { title: '数据分析' } },
      { path: 'notes', name: 'Notes', component: () => import('@/views/notes/Index.vue'), meta: { title: '笔记浏览' } },
      { path: 'publish', name: 'Publish', component: () => import('@/views/publish/Index.vue'), meta: { title: '笔记发布' } },
      { path: 'agent', name: 'Agent', component: () => import('@/views/agent/Index.vue'), meta: { title: 'AI 智能体' } },
    ],
  },
  {
    path: '/auth',
    component: () => import('@/layouts/BlankLayout.vue'),
    children: [
      { path: 'login', name: 'Login', component: () => import('@/views/auth/Login.vue'), meta: { title: '登录' } },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'Login' && !token) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
