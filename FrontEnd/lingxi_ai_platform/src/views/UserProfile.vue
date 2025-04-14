<template>
  <div class="profile-container">
    <div class="profile-box">
      <!-- 个人信息卡片 -->
      <el-card class="profile-card">
        <div class="profile-header">
          <div class="avatar-wrapper">
            <el-avatar
              :size="100"
              :src="userInfo.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'"
            />
            <el-upload
              class="avatar-uploader"
              action="#"
              :http-request="uploadAvatar"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              accept="image/jpeg,image/png,image/gif"
            >
              <el-button class="change-avatar-btn" type="primary" size="small">
                更换头像
              </el-button>
            </el-upload>
          </div>
          <div class="basic-info">
            <h2>{{ userInfo.username }}</h2>
            <p>{{ userInfo.bio || '这个人很懒，什么都没有留下' }}</p>
          </div>
        </div>

        <!-- 个人信息表单 -->
        <el-form
          ref="profileFormRef"
          :model="userInfo"
          :rules="profileRules"
          label-width="100px"
          class="profile-form"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="userInfo.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item label="手机号码" prop="phone_number">
            <el-input
              v-model="userInfo.phone_number"
              placeholder="请输入手机号码"
              :prefix-icon="Phone"
            />
          </el-form-item>

          <el-form-item label="电子邮箱" prop="email">
            <el-input
              v-model="userInfo.email"
              placeholder="请输入电子邮箱"
              :prefix-icon="Message"
            />
          </el-form-item>

          <el-form-item label="个人简介" prop="bio">
            <el-input
              v-model="userInfo.bio"
              type="textarea"
              :rows="3"
              placeholder="介绍一下自己吧"
            />
          </el-form-item>

            <!-- 统计信息 -->
            <div class="statistics">
              <div class="stat-item" @click="router.push('/posts')">
              <h3>{{ userInfo.posts_count }}</h3>
              <p>发帖数</p>
              </div>
              <div class="stat-item" @click="router.push('/followers')">
              <h3>{{ userInfo.followers }}</h3>
              <p>粉丝</p>
              </div>
              <div class="stat-item" @click="router.push('/following')">
              <h3>{{ userInfo.following }}</h3>
              <p>已关注</p>
              </div>
            </div>

          <div class="form-actions">
            <el-button
              type="primary"
              :loading="loading"
              @click="handleUpdateProfile"
            >
              保存修改
            </el-button>
            <el-button @click="goBack">返回</el-button>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Phone, Message } from '@element-plus/icons-vue'
import type { UploadProps, UploadRequestOptions } from 'element-plus'

// 上传前的验证
const beforeAvatarUpload = (file: File) => {
  // 检查文件类型
  const isImage = ['image/jpeg', 'image/png', 'image/gif'].includes(file.type)
  if (!isImage) {
    ElMessage.error('头像必须是JPG/PNG/GIF格式的图片！')
    return false
  }
  
  // 检查文件大小（限制为2MB）
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('头像图片大小不能超过2MB！')
    return false
  }
  
  return true
}

// 自定义上传请求
const uploadAvatar = async (options: UploadRequestOptions) => {
  try {
    const { file } = options
    loading.value = true
    
    // 获取token
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }
    
    // 创建FormData对象
    const formData = new FormData()
    formData.append('avatar', file)
    
    // 实际API请求代码（暂时注释）
    const response = await fetch('/user/upload_avatar/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('头像上传失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      // 更新头像
      userInfo.avatar = result.data.avatar
      ElMessage.success('头像更新成功')
    } else {
      throw new Error(result.message || '头像上传失败')
    }
    
  } catch (error) {
    console.error('头像上传失败:', error)
    ElMessage.error('头像上传失败，请稍后重试')

  } finally {
    loading.value = false
  }
}

const router = useRouter()
import type { FormInstance } from 'element-plus'
import { Avatar } from '@element-plus/icons-vue'

const profileFormRef = ref<FormInstance | null>(null)
const loading = ref(false)

// 用户信息
const userInfo = reactive({
  username: '',
  phone_number: '',
  email: '',
  bio: '',
  avatar: '',
  posts_count: 0,
  followers: 0,
  following: 0
})

// 获取用户信息的函数中添加模拟数据
const fetchUserInfo = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }

    // 模拟API请求延迟
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 模拟返回的用户数据
    const mockUserData = {
      username: '未知',
      phone_number: '未知',
      email: '未知',
      bio: '未知',
      avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
      posts_count: 0,
      followers: 0,
      following: 0,
    }

    // 更新用户信息
    Object.assign(userInfo, mockUserData)

    // 实际API请求代码（暂时注释）
    const response = await fetch('/user/user_info/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error('获取用户信息失败')
    }

    const data = await response.json();
    if (data.code !== 200) {
      throw new Error(data.message || '获取用户信息失败');
    }

    // 更新用户信息
    Object.assign(userInfo, {
      username: data.username,
      phone_number: data.phone_number,
      email: data.email || '',
      bio: data.bio || '这个人很懒，什么都没有留下',
      avatar: data.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
      posts_count: data.posts_count || 0,
      followers: data.followers || 0,
      following: data.following || 0
    })
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败，请稍后重试')
  }
}

// 组件挂载时获取用户信息
onMounted(() => {
  fetchUserInfo()
})

// 表单验证规则
const profileRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度应在2-20个字符之间', trigger: 'blur' }
  ],
  phone_number: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 更新个人信息
const handleUpdateProfile = async () => {
  if (!profileFormRef.value) return

  try {
    await profileFormRef.value.validate()
    loading.value = true

    // TODO: 发送更新请求到后端
    const response = await fetch('/user/update_info/', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        username: userInfo.username,
        phone_number: userInfo.phone_number,
        email: userInfo.email,
        bio: userInfo.bio,
        avatar : userInfo.avatar
      })
    })

    if (!response.ok) {
      throw new Error('更新个人信息失败')
    }
    else {
      const result = await response.json()
      if (result.code !== 200 && response.status !== 200) { // Adjust condition based on actual response structure
        // console.log("code : ", result.code)
        // console.log("status : ", response.status)
        // console.log("message : ", result.message)
        throw new Error(result.message || '更新个人信息失败')
      }
      ElMessage.success('个人信息更新成功')
    }
    
  } catch (error) {
    ElMessage.error('更新失败，请检查输入信息')
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.profile-box {
  max-width: 800px;
  margin: 0 auto;
}

.profile-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 30px;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.avatar-wrapper {
  position: relative;
  text-align: center;
}

.change-avatar-btn {
  margin-top: 10px;
  width: 100px;
}

.basic-info {
  flex: 1;
}

.basic-info h2 {
  margin: 0 0 10px 0;
  color: #333;
}

.basic-info p {
  color: #666;
  margin: 0;
}

.profile-form {
  padding: 20px;
}

.statistics {
  display: flex;
  justify-content: space-around;
  margin: 30px 0;
  padding: 20px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
}

.stat-item {
  text-align: center;
}

.stat-item h3 {
  margin: 0;
  font-size: 24px;
  color: #409EFF;
}

.stat-item p {
  margin: 5px 0 0 0;
  color: #666;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-textarea__inner) {
  border-radius: 8px;
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .statistics {
    flex-wrap: wrap;
  }
  
  .stat-item {
    width: 50%;
    margin-bottom: 20px;
  }
}
</style>