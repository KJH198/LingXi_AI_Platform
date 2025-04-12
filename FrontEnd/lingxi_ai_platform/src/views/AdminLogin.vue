<template>
  <div class="admin-login-container">
    <div class="admin-login-box">
      <div class="admin-login-title">
        <h2>管理员登录</h2>
        <p>灵犀AI平台管理系统</p>
      </div>
      
      <el-form
        ref="adminLoginFormRef"
        :model="adminLoginForm"
        :rules="adminLoginRules"
        class="admin-login-form"
        @keyup.enter="handleAdminLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="adminLoginForm.username"
            placeholder="管理员用户名"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="adminLoginForm.password"
            type="password"
            placeholder="管理员密码"
            :prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <div class="admin-login-options">
          <el-checkbox v-model="adminLoginForm.remember">记住登录状态</el-checkbox>
        </div>

        <el-button
          :loading="loading"
          type="primary"
          class="admin-login-button"
          @click="handleAdminLogin"
        >
          {{ loading ? '登录中...' : '管理员登录' }}
        </el-button>

        <div class="back-to-user-login">
          <el-link type="info" @click="goToUserLogin">返回用户登录</el-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const adminLoginFormRef = ref(null)
const loading = ref(false)

const adminLoginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const adminLoginRules = {
  username: [
    { required: true, message: '请输入管理员用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入管理员密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ]
}

const handleAdminLogin = async () => {
  if (!adminLoginFormRef.value) return
  
  try {
    await adminLoginFormRef.value.validate()
    loading.value = true

    const response = await fetch('/user/adminLogin', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone_number: adminLoginForm.username,
        password: adminLoginForm.password
      })
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    if (data.success) {
      ElMessage.success('管理员登录成功')
      localStorage.setItem('adminToken', data.token)
      localStorage.setItem('userRole', data.role)
      router.push('/admin/dashboard')
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('管理员登录失败，请检查输入信息')
  } finally {
    loading.value = false
  }
}

const goToUserLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.admin-login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #303aad 0%, #3370ca 100%);
}

.admin-login-box {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  transform: translateY(0);
  transition: transform 0.3s ease;
}

.admin-login-box:hover {
  transform: translateY(-5px);
}

.admin-login-title {
  text-align: center;
  margin-bottom: 40px;
}

.admin-login-title h2 {
  font-size: 28px;
  color: #1a237e;
  margin-bottom: 8px;
}

.admin-login-title p {
  font-size: 16px;
  color: #666;
}

.admin-login-form {
  margin-top: 20px;
}

.admin-login-options {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 20px;
}

.admin-login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 22px;
  background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
  border: none;
  transition: all 0.3s ease;
}

.admin-login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.admin-login-button:active {
  transform: translateY(0);
}

.back-to-user-login {
  text-align: center;
  margin-top: 20px;
}

:deep(.el-input__wrapper) {
  border-radius: 22px;
  padding: 0 20px;
}

:deep(.el-input__inner) {
  height: 44px;
  line-height: 44px;
}

:deep(.el-form-item__error) {
  padding-left: 20px;
  font-size: 12px;
}

@media (max-width: 480px) {
  .admin-login-box {
    margin: 20px;
    padding: 30px 20px;
  }
}
</style> 