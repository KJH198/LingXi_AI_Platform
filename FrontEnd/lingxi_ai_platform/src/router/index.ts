import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Community from '../views/Community.vue'
import Register from '../views/Register.vue'  
import UserProfile from '../views/UserProfile.vue'
import Followers from '../views/Followers.vue'
import Following from '../views/Followings.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/register',  // 添加注册路由
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
      path: '/',
      redirect: '/login'
    }
  ]
})

export default router 