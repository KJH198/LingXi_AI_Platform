import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import AdminLogin from '../views/AdminLogin.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import Community from '../views/Community.vue'
import Register from '../views/Register.vue'  

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/admin/login',
      name: 'AdminLogin',
      component: AdminLogin
    },
    {
      path: '/admin/dashboard',
      name: 'AdminDashboard',
      component: AdminDashboard
    },
    {  
      path: '/register',  // 添加注册路由
      name: 'Register',
      component: Register
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