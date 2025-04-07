<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-title">
        <h2>欢迎登录</h2>
        <p>灵犀AI平台</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="phone_number">
          <el-input
            v-model="loginForm.phone_number"
            placeholder="请输入手机号码"
            :prefix-icon="Phone"
            :show-word-limit="true"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <div class="login-options">
          <el-checkbox v-model="loginForm.remember">记住密码</el-checkbox>
          <el-link type="primary" :underline="false">忘记密码？</el-link>
        </div>

        <el-button
          :loading="loading"
          type="primary"
          class="login-button"
          @click="handleLogin"
        >
          {{ loading ? '登录中...' : '登录' }}
        </el-button>

        <div class="login-actions">
          <el-link type="primary" @click="handleRegister">没有账号？立即注册</el-link>
          <el-link type="info" @click="goToAdminLogin">管理员登录</el-link>
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
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({  // 响应式对象
  phone_number: '',
  password: '',
  remember: false
})

const loginRules = {
  phone_number: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return // 防止表单引用为空
  
  try {
    // 校验表单
    await loginFormRef.value.validate()
    loading.value = true
    
    // 发送登录请求
    const response = await fetch('/user/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone_number: loginForm.phone_number,
        password: loginForm.password
      })
    })
    
    const data = await response.json()
    
    // 处理登录成功
    if (data.success) {
      ElMessage.success('登录成功')
      localStorage.setItem('token', data.token)  // 保存 token 到本地存储
      router.push('/community') // 跳转到其他页面
    } else {   // 登录失败提示
      ElMessage.error(data.message || '登录失败，请检查用户名和密码') // 使用服务器返回的错误信息
    }
    
  } catch (error) {
    // console.error('登录失败:', error)          // 控制台输出错误信息
    ElMessage.error('登录失败，请检查用户名和密码') // 顶部弹出登录失败提示
  } finally {
    loading.value = false
  }
}

const goToAdminLogin = () => {
  router.push('/adminLogin')
}
const handleRegister = () => {
  router.push('/register') // 跳转到注册页面
}

</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transform: translateY(0);
  transition: transform 0.3s ease;
}

.login-box:hover {
  transform: translateY(-5px);
}

.login-title {
  text-align: center;
  margin-bottom: 40px;
}

.login-title h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.login-title p {
  font-size: 16px;
  color: #666;
}

.login-form {
  margin-top: 20px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 22px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.login-button:active {
  transform: translateY(0);
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
  .login-box {
    margin: 20px;
    padding: 30px 20px;
  }
}

.login-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding: 0 10px;
}
</style> 