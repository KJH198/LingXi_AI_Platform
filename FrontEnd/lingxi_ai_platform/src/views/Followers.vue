<template>
  <div class="followers-container">
    <div class="followers-box">
      <el-card class="followers-card">
        <!-- 顶部导航 -->
        <div class="top-bar">
          <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
          <h2>我的粉丝</h2>
          <div style="width: 70px"></div>
        </div>

        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input
            v-model="searchQuery"
            placeholder="搜索粉丝"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </div>

        <!-- 粉丝列表 -->
        <div class="followers-list">
          <el-empty 
            v-if="!loading && followers.length === 0" 
            description="暂无粉丝" 
          />
          
          <el-skeleton 
            :loading="loading" 
            animated 
            :count="3" 
            v-if="loading"
          >
            <template #template>
              <div class="follower-card-skeleton">
                <el-skeleton-item variant="h3" style="width: 50%" />
                <el-skeleton-item variant="text" style="width: 40%" />
                <el-skeleton-item variant="p" style="width: 80%" />
              </div>
            </template>
          </el-skeleton>

          <el-card
            v-else
            v-for="follower in followers"
            :key="follower.id"
            class="follower-card"
          >
            <div class="follower-info">
              <h3 class="follower-name">{{ follower.username }}</h3>
              <p class="follower-phone">{{ maskPhoneNumber(follower.phone_number) }}</p>
              <p class="follower-bio">{{ follower.bio || '这个人很懒，什么都没有留下' }}</p>
            </div>
          </el-card>
        </div>

        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 30, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Search } from '@element-plus/icons-vue'

// 粉丝接口
interface Follower {
  id: number
  username: string
  phone_number: string
  bio: string
}

const router = useRouter()
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const followers = ref<Follower[]>([])

// 获取粉丝列表
const fetchFollowers = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }

    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    const mockFollowers = [
      {
        id: 1,
        username: '张三',
        phone_number: '13812345678',
        bio: '热爱AI技术开发，专注大模型应用'
      },
      {
        id: 2,
        username: '李四',
        phone_number: '13987654321',
        bio: '前端工程师，喜欢研究新技术'
      },
      {
        id: 3,
        username: '王五',
        phone_number: '13511112222',
        bio: '产品经理，关注用户体验'
      }
    ]
    
    // 根据搜索关键词过滤
    if (searchQuery.value) {
      followers.value = mockFollowers.filter(f => 
        f.username.includes(searchQuery.value) || 
        f.phone_number.includes(searchQuery.value) ||
        f.bio.includes(searchQuery.value)
      )
    } else {
      followers.value = mockFollowers
    }
    
    total.value = followers.value.length

    // 实际API请求代码（暂时注释）
    /*
    const response = await fetch(
      `/api/user/followers?page=${currentPage.value}&pageSize=${pageSize.value}&search=${searchQuery.value}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )

    if (!response.ok) {
      throw new Error('获取粉丝列表失败')
    }

    const result = await response.json()
    if (result.code === 200) {
      followers.value = result.data.items
      total.value = result.data.total
    } else {
      throw new Error(result.message)
    }
    */
  } catch (error) {
    ElMessage.error('获取粉丝列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 手机号码脱敏处理
const maskPhoneNumber = (phone: string): string => {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  fetchFollowers()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchFollowers()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchFollowers()
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchFollowers()
})
</script>

<style scoped>
.followers-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.followers-box {
  max-width: 800px;
  margin: 0 auto;
}

.followers-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  padding: 20px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.top-bar h2 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.search-bar {
  margin-bottom: 20px;
}

.followers-list {
  margin-bottom: 20px;
}

.follower-card {
  margin-bottom: 15px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.follower-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.follower-card-skeleton {
  padding: 20px;
  margin-bottom: 15px;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.follower-info {
  padding: 10px;
}

.follower-name {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}

.follower-phone {
  margin: 5px 0;
  font-size: 14px;
  color: #666;
}

.follower-bio {
  margin: 10px 0 0 0;
  font-size: 14px;
  color: #888;
  line-height: 1.5;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

@media (max-width: 768px) {
  .followers-container {
    padding: 20px 10px;
  }
  
  .followers-box {
    margin: 0;
  }

  .followers-card {
    padding: 15px;
    border-radius: 12px;
  }
  
  .follower-name {
    font-size: 16px;
  }
}
</style>