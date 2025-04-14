import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import AdminLogin from '../views/AdminLogin.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import Community from '../views/Community.vue'
import Register from '../views/Register.vue'  
import UserProfile from '../views/UserProfile.vue'
import Followers from '../views/Followers.vue'
import Following from '../views/Followings.vue'
import CreateAI from '../views/CreateAI.vue'
import AgentEditor from '../views/AgentEditor.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/adminLogin',
      name: 'AdminLogin',
      component: AdminLogin
    },
    {
      path: '/admin/dashboard',
      name: 'AdminDashboard',
      component: AdminDashboard
    },
    {  
      path: '/register',  
      name: 'Register',
      component: Register
    },
    {
      path: '/profile',
      name: 'UserProfile',
      component: UserProfile
    },
    {
      path: '/followers',
      name: 'Followers',
      component: Followers
    },
    {
      path: '/following',
      name: 'Following',
      component: () => import('../views/Followings.vue')
    },
    {
      path: '/community',
      name: 'Community',
      component: Community
    },
    {
      path: '/create-ai',
      name: 'CreatAI',
      component: CreateAI
    },
    {
      path: '/agent-editor',
      name: 'AgentEditor',
      component: AgentEditor
    },
    {
      path: '/',
      redirect: '/login'
    }
  ]
})

export default router 