<template>
    <div class="register-container">
      <div class="register-box">
        <div class="register-title">
          <h2>用户注册</h2>
          <p>灵犀AI平台</p>
        </div>
        
        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          class="register-form"
          @keyup.enter="handleRegister"
        >
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="用户名"
              :prefix-icon="User"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="密码"
              :prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>
  
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="确认密码"
              :prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>
  
          <el-form-item prop="phone_number">
            <el-input
              v-model="registerForm.phone_number"
              placeholder="手机号码"
              :prefix-icon="Phone"
              clearable
            />
          </el-form-item>
  
          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              placeholder="邮箱(选填)"
              :prefix-icon="Message"
              clearable
            />
          </el-form-item>
  
          <el-button
            :loading="loading"
            type="primary"
            class="register-button"
            @click="handleRegister"
          >
            {{ loading ? '注册中...' : '注册' }}
          </el-button>
  
          <div class="login-link">
            已有账号？<el-link type="primary" @click="goToLogin">立即登录</el-link>
          </div>
        </el-form>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { User, Lock, Phone, Message } from '@element-plus/icons-vue'
  
  const router = useRouter()
  const registerFormRef = ref(null)
  const loading = ref(false)
  
  const registerForm = reactive({
    username: '',
    password: '',
    confirmPassword: '',
    phone_number: '',
    email: ''
  })
  
  // 自定义校验密码确认
  const validateConfirmPassword = (rule, value, callback) => {
    if (value === '') {
      callback(new Error('请再次输入密码'))
    } else if (value !== registerForm.password) {
      callback(new Error('两次输入密码不一致'))
    } else {
      callback()
    }
  }
  
  const registerRules = {
    username: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
    ],
    confirmPassword: [
      { required: true, validator: validateConfirmPassword, trigger: 'blur' }
    ],
    phone_number: [
      { required: true, message: '请输入手机号码', trigger: 'blur' },
      { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
    ],
    email: [
      { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
    ]
  }
  
  const handleRegister = async () => {
    if (!registerFormRef.value) return
  
    try {
      await registerFormRef.value.validate()
      loading.value = true
      
      // 发送注册请求
    //   const response = await fetch('/api/register', {
    //     method: 'POST',
    //     headers: {
    //       'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify({
    //       username: registerForm.username,
    //       password: registerForm.password,
    //       phone_number: registerForm.phone_number,
    //       email: registerForm.email || undefined
    //     })
    //   })
  
    //   const data = await response.json()

      // 模拟后端响应
      const response = {
        status: 201,
          json: async () => ({
          message: '注册成功'
        })
      }
  
      const data = await response.json()
      
      if (response.status === 201) {
        ElMessage.success('注册成功')
        router.push('/login')
      } else {
        ElMessage.error(data.error || '注册失败')
      }
    } catch (error) {
      ElMessage.error('注册失败，请检查输入信息')
    } finally {
      loading.value = false
    }
  }
  
  const goToLogin = () => {
    router.push('/login')
  }
  </script>
  
  <style scoped>
  .register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .register-box {
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
  
  .register-box:hover {
    transform: translateY(-5px);
  }
  
  .register-title {
    text-align: center;
    margin-bottom: 40px;
  }
  
  .register-title h2 {
    font-size: 28px;
    color: #333;
    margin-bottom: 8px;
  }
  
  .register-title p {
    font-size: 16px;
    color: #666;
  }
  
  .register-form {
    margin-top: 20px;
  }
  
  .register-button {
    width: 100%;
    height: 44px;
    font-size: 16px;
    border-radius: 22px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    transition: all 0.3s ease;
    margin-bottom: 20px;
  }
  
  .register-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .register-button:active {
    transform: translateY(0);
  }
  
  .login-link {
    text-align: center;
    font-size: 14px;
    color: #666;
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
    .register-box {
      margin: 20px;
      padding: 30px 20px;
    }
  }
  </style>