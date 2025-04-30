import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import Editor from '../views/Editor.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/community',
    name: 'Community',
    component: () => import('../views/Community.vue')
  },
  {
    path: '/my-posts',
    name: 'MyPost',
    component: () => import('../views/MyPost.vue')
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: () => import('../views/UserProfile.vue')
  },
  {
    path: '/my-agents',
    name: 'MyAgent',
    component: () => import('../views/MyAgent.vue')
  },
  {
    path: '/agent-editor',
    name: 'AgentEditor',
    component: () => import('../views/AgentEditor.vue')
  },
  {
    path: '/create-ai',
    name: 'CreateAI',
    component: () => import('../views/CreateAI.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/user-profile/:id',
    name: 'UserProfileDetail',
    component: () => import('../views/UserProfileDetail.vue')
  },
  {
    path: '/agent-detail/:id',
    name: 'AgentDetail',
    component: () => import('../views/AgentDetail.vue')
  },
  {
    path: '/knowledge-base/:id',
    name: 'KnowledgeBaseDetail',
    component: () => import('../views/KnowledgeBaseDetail.vue')
  },
  {
    path: '/admin',
    name: 'AdminLogin',
    component: () => import('../views/AdminLogin.vue')
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('../views/AdminDashboard.vue')
  },
  {
    path: '/code-editor',
    name: 'CodeEditor',
    component: () => import('../views/CodeEditor.vue')
  },
  {
    path: '/editor',
    name: 'Editor',
    component: Editor
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/Chat.vue')
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue'),
    meta: {
      title: '搜索结果 - 灵犀AI社区'
    }
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router