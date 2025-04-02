<template>
  <div class="followings-container">
    <div class="followings-box">
      <el-card class="followings-card">
        <!-- 顶部导航 -->
        <div class="top-bar">
          <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
          <h2>我的关注</h2>
          <div style="width: 70px"></div>
        </div>

        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input
            v-model="searchQuery"
            placeholder="搜索关注"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </div>

        <!-- 关注列表 -->
        <div class="followings-list">
          <el-empty 
            v-if="!loading && followings.length === 0" 
            description="暂无关注的用户" 
          />
          
          <el-skeleton 
            :loading="loading" 
            animated 
            :count="3" 
            v-if="loading"
          >
            <template #template>
              <div class="following-card-skeleton">
                <el-skeleton-item variant="h3" style="width: 50%" />
                <el-skeleton-item variant="text" style="width: 40%" />
                <el-skeleton-item variant="p" style="width: 80%" />
              </div>
            </template>
          </el-skeleton>

          <el-card
            v-else
            v-for="following in followings"
            :key="following.id"
            class="following-card"
          >
            <div class="following-info">
              <h3 class="following-name">{{ following.username }}</h3>
              <p class="following-phone">{{ maskPhoneNumber(following.phone_number) }}</p>
              <p class="following-bio">{{ following.bio || '这个人很懒，什么都没有留下' }}</p>
              <div class="following-actions">
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="handleUnfollow(following.id)"
                >
                  取消关注
                </el-button>
              </div>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Search } from '@element-plus/icons-vue'

// 关注用户接口
interface Following {
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
const followings = ref<Following[]>([])

// 获取关注列表
const fetchFollowings = async () => {
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
    const mockFollowings = [
      {
        id: 1,
        username: '宋江',
        phone_number: '13512345678',
        bio: '人工智能研究员，专注大模型训练'
      },
      {
        id: 2,
        username: '吴用',
        phone_number: '13687654321',
        bio: '后端工程师，主攻分布式系统'
      },
      {
        id: 3,
        username: '卢俊义',
        phone_number: '13933333333',
        bio: 'UI设计师，擅长交互设计'
      }
    ]
    
    // 根据搜索关键词过滤
    if (searchQuery.value) {
      followings.value = mockFollowings.filter(f => 
        f.username.includes(searchQuery.value) || 
        f.phone_number.includes(searchQuery.value) ||
        f.bio.includes(searchQuery.value)
      )
    } else {
      followings.value = mockFollowings
    }
    
    total.value = followings.value.length

    // 实际API请求代码（暂时注释）
    /*
    const response = await fetch(
      `/api/user/followings?page=${currentPage.value}&pageSize=${pageSize.value}&search=${searchQuery.value}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )

    if (!response.ok) {
      throw new Error('获取关注列表失败')
    }

    const result = await response.json()
    if (result.code === 200) {
      followings.value = result.data.items
      total.value = result.data.total
    } else {
      throw new Error(result.message)
    }
    */
  } catch (error) {
    ElMessage.error('获取关注列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 取消关注
const handleUnfollow = (userId: number) => {
  ElMessageBox.confirm(
    '确定要取消关注该用户吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        router.push('/login')
        return
      }
      
      // 模拟取消关注请求
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 更新本地数据
      followings.value = followings.value.filter(f => f.id !== userId)
      total.value = followings.value.length
      
      ElMessage.success('已取消关注')
      
      // 实际API请求代码（暂时注释）
      /*
      const response = await fetch(`/api/user/unfollow/${userId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error('取消关注失败')
      }
      
      const result = await response.json()
      if (result.code === 200) {
        followings.value = followings.value.filter(f => f.id !== userId)
        total.value = followings.value.length
        ElMessage.success('已取消关注')
      } else {
        throw new Error(result.message)
      }
      */
    } catch (error) {
      ElMessage.error('取消关注失败，请稍后重试')
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 手机号码脱敏处理
const maskPhoneNumber = (phone: string): string => {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  fetchFollowings()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchFollowings()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchFollowings()
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchFollowings()
})
</script>

<style scoped>
.followings-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.followings-box {
  max-width: 800px;
  margin: 0 auto;
}

.followings-card {
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

.followings-list {
  margin-bottom: 20px;
}

.following-card {
  margin-bottom: 15px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.following-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.following-card-skeleton {
  padding: 20px;
  margin-bottom: 15px;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.following-info {
  padding: 10px;
  position: relative;
}

.following-name {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}

.following-phone {
  margin: 5px 0;
  font-size: 14px;
  color: #666;
}

.following-bio {
  margin: 10px 0 0 0;
  font-size: 14px;
  color: #888;
  line-height: 1.5;
}

.following-actions {
  margin-top: 15px;
  text-align: right;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

@media (max-width: 768px) {
  .followings-container {
    padding: 20px 10px;
  }
  
  .followings-box {
    margin: 0;
  }

  .followings-card {
    padding: 15px;
    border-radius: 12px;
  }
  
  .following-name {
    font-size: 16px;
  }
  
  .following-actions {
    text-align: center;
  }
}
</style>