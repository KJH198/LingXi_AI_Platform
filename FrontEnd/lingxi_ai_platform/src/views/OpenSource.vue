<template>
    <div class="hot-agents-container">
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>
      
      <!-- 空状态 -->
      <el-empty v-else-if="agents.length === 0" description="暂无开源智能体" />
      
      <!-- 智能体列表 -->
      <div v-else class="agent-list">
        <div 
          v-for="agent in agents" 
          :key="agent.id" 
          class="agent-item"
          @click="viewAgentDetail(agent.id)"
        >
          <div class="agent-avatar">
            <img v-if="agent.avatar" :src="agent.avatar" alt="头像" />
            <div v-else class="avatar-placeholder">AI</div>
          </div>
          <div class="agent-info">
            <div class="agent-name">{{ agent.name }}</div>
            <div class="agent-description">{{ agent.description }}</div>
            <div class="agent-stats">
              <span class="stat-item">
                <el-icon><View /></el-icon> {{ agent.views || 0 }}
              </span>
              <span class="stat-item">
                <el-icon><Star /></el-icon> {{ agent.followerCount || 0 }} 人关注
              </span>
              <span class="stat-item">
                <el-icon><User /></el-icon> {{ agent.creator ? agent.creator.username : '未知' }}
              </span>
            </div>
          </div>
          <el-button 
            :type="agent.isFollowed ? 'success' : 'primary'" 
            size="small"
            @click.stop="followAgent(agent)"
          >
            {{ agent.isFollowed ? '已关注' : '关注' }}
          </el-button>
        </div>
      </div>
      
      <!-- 分页 -->
      <div class="pagination" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { View, Star, User } from '@element-plus/icons-vue'
  
  const router = useRouter()
  const loading = ref(true)
  const agents = ref([])
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)
  
  // 获取热门智能体
  const fetchHotAgents = async () => {
    loading.value = true
    try {
      const token = localStorage.getItem('token')
      const params = new URLSearchParams({
        page: currentPage.value.toString(),
        size: pageSize.value.toString()
      })
      
      const response = await fetch(`/community/agents/open/?${params.toString()}`, {
        method: 'GET',
        headers: token ? {
          'Authorization': `Bearer ${token}`,
        } : {}
      })
      
      if (!response.ok) {
        throw new Error('获取热门智能体失败')
      }
      
      const result = await response.json()
      if (result.code === 200) {
        agents.value = result.data.items || []
        total.value = result.data.total || 0
      } else {
        throw new Error(result.message || '获取热门智能体失败')
      }
    } catch (error) {
      console.error('获取热门智能体失败:', error)
      ElMessage.error('获取热门智能体失败，请稍后重试')
    } finally {
      loading.value = false
    }
  }
  
  // 查看智能体详情
  const viewAgentDetail = (agentId) => {
    router.push(`/agent-editor/${agentId}`)
  }
  
  // 关注/取消关注智能体
  const followAgent = async (agent) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        return
      }
      
      const isFollowed = agent.isFollowed
      
      // 关注/取消关注请求
      const response = await fetch(`/user/follow/agent/${agent.id}/`, {
        method: isFollowed ? 'DELETE' : 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error(isFollowed ? '取消关注失败' : '关注失败')
      }
      
      const result = await response.json()
      if (result.code === 200) {
        // 更新状态
        agent.isFollowed = !isFollowed
        agent.followerCount = isFollowed ? 
          (agent.followerCount - 1) : 
          (agent.followerCount + 1)
        
        ElMessage.success(isFollowed ? '已取消关注智能体' : '关注智能体成功')
      } else {
        throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
      }
    } catch (error) {
      console.error('关注智能体操作失败:', error)
      ElMessage.error('操作失败，请稍后重试')
    }
  }
  
  // 分页处理
  const handleSizeChange = (val) => {
    pageSize.value = val
    currentPage.value = 1
    fetchHotAgents()
  }
  
  const handleCurrentChange = (val) => {
    currentPage.value = val
    fetchHotAgents()
  }
  
  // 初始加载
  onMounted(() => {
    fetchHotAgents()
  })
  </script>
  
  <style scoped>
  .hot-agents-container {
    padding: 20px;
  }
  
  .section-title {
    margin-bottom: 20px;
    font-size: 18px;
    font-weight: 600;
  }
  
  .agent-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .agent-item {
    display: flex;
    align-items: center;
    padding: 15px;
    border: 1px solid #ebeef5;
    border-radius: 8px;
    background-color: #fff;
    transition: all 0.3s;
    cursor: pointer;
  }
  
  .agent-item:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .agent-avatar {
    width: 48px;
    height: 48px;
    border-radius: 24px;
    margin-right: 15px;
    overflow: hidden;
  }
  
  .agent-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .avatar-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #409eff;
    color: white;
    font-weight: bold;
  }
  
  .agent-info {
    flex: 1;
    min-width: 0;
  }
  
  .agent-name {
    font-weight: 600;
    font-size: 16px;
    margin-bottom: 5px;
  }
  
  .agent-description {
    font-size: 14px;
    color: #606266;
    margin-bottom: 8px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .agent-stats {
    display: flex;
    gap: 15px;
    font-size: 12px;
    color: #909399;
  }
  
  .stat-item {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  
  .loading-container {
    padding: 20px 0;
  }
  
  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
  </style>