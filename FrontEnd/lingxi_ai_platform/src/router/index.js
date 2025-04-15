import { createRouter, createWebHistory } from 'vue-router'

const routes = [
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 