import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import Editor from '../views/Editor.vue'
import AgentDrafts from '@/views/AgentDrafts.vue'
import AgentEditor from '@/views/AgentEditor.vue'

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
    path: '/agent-look',
    name: 'AgentLook',
    component: () => import('../views/AgentLook.vue')
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
    path: '/chat/:id',
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
  {
    path: '/agent-editor/:id',
    name: 'AgentEditorWithId',
    component: () => import('../views/AgentEditor.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/agent-look/:id',
    name: 'AgentLookWithId',
    component: () => import('../views/AgentLook.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/my-knowledgebases',
    name: 'MyKnowledgebases',
    component: () => import('../views/MyKnowledgeBase.vue'),
  },
  {
    path: '/agent-drafts',
    name: 'AgentDrafts',
    component: AgentDrafts,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-agent/draft/:id',
    name: 'EditAgentDraft',
    component: AgentEditor,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-agent/publish/:id',
    name: 'PublishAgentDraft',
    component: AgentEditor,
    meta: { requiresAuth: true }
  },
  {
    path: '/post/:id',
    name: 'PostDetail',
    component: () => import('../views/PostDetail.vue')
  },
  {
    path: '/usable-agent-list',
    name: 'UsableAgentList',
    component: () => import('../views/UseableAgentList.vue')
  },
  {
    path: '/mypost/',
    name: 'MyPost',
    component: () => import('../views/MyPost.vue')
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router