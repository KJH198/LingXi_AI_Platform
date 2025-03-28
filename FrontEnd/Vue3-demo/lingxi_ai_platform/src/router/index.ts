import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Community from '../views/Community.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: Login
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