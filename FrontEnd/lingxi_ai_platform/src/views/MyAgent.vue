<template>
  <div class="my-agent-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-button 
            @click="router.push('/community')" 
            type="primary" 
            plain
            size="medium"
            :icon="ArrowLeft"
          >
            返回社区
          </el-button>
          <h2 class="page-title">我的智能体</h2>
        </div>
        <el-button type="primary" @click="router.push('/agent-editor')" :icon="Plus">
          创建新智能体
        </el-button>
      </el-header>

      <!-- 在 el-header 下方添加标签页 -->
      <el-tabs v-model="activeTab" class="agent-tabs">
        <el-tab-pane label="我创建的" name="created"></el-tab-pane>
        <el-tab-pane label="我关注的" name="followed"></el-tab-pane>
      </el-tabs>

      <!-- 修改 el-main 部分，根据标签页显示不同内容 -->
      <el-main>
        <!-- 我创建的智能体 -->
        <template v-if="activeTab === 'created'">
          <el-skeleton :rows="3" animated v-if="loading" />
          
          <div v-else class="agent-grid">
            <!-- 保持原有的智能体卡片内容不变 -->
            <el-card v-for="agent in agents" :key="agent.id" class="agent-card" shadow="hover">
              <div class="agent-content">
                <!-- 智能体封面图 -->
                <div class="agent-cover-wrapper" @click="viewAgentDetails(agent)">
                  <el-image 
                    :src="agent.coverImage" 
                    fit="cover" 
                    class="agent-cover"
                    :preview-src-list="[agent.coverImage]"
                  >
                    <template #error>
                      <div class="image-placeholder">
                        <el-icon :size="40"><Picture /></el-icon>
                      </div>
                    </template>
                  </el-image>
                  <div class="agent-stats-overlay">
                    <div class="stat-item">
                      <el-icon><View /></el-icon>
                      <span>{{ agent.views }}</span>
                    </div>
                    <div class="stat-item">
                      <el-icon><Star /></el-icon>
                      <span>{{ agent.likes }}</span>
                    </div>
                    <div class="stat-item">
                      <el-icon><ChatDotRound /></el-icon>
                      <span>{{ agent.comments }}</span>
                    </div>
                  </div>
                </div>
                
                <!-- 智能体名称和描述 -->
                <div class="agent-info">
                  <h3 class="agent-name" @click="viewAgentDetails(agent)">{{ agent.name }}</h3>
                  <p class="agent-description">{{ agent.description }}</p>
                </div>
                
                <!-- 操作按钮 -->
                <div class="agent-actions">
                  <el-button type="primary" size="small" @click="router.push(`/chat/${agent.id}`)">
                    <el-icon class="el-icon--left"><ChatDotRound /></el-icon>对话
                  </el-button>
                  <el-button type="warning" size="small" @click="editAgent(agent)">
                    <el-icon class="el-icon--left"><Edit /></el-icon>编辑
                  </el-button>
                  <el-button type="danger" size="small" @click="deleteAgent(agent)">
                    <el-icon class="el-icon--left"><Delete /></el-icon>删除
                  </el-button>
                  <el-button type="info" size="small" @click="shareAgent(agent)">
                    <el-icon class="el-icon--left"><Share /></el-icon>分享
                  </el-button>
                  <el-button 
                    :type="agent.isOpenSource ? 'success' : 'default'" 
                    size="small" 
                    @click="toggleOpenSource(agent)"
                  >
                    <el-icon class="el-icon--left"><Link /></el-icon>
                    {{ agent.isOpenSource ? '已开源' : '未开源' }}
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 原有的空状态展示 -->
          <el-empty 
            v-if="!loading && agents.length === 0" 
            description="暂无智能体" 
            :image-size="200"
          >
            <el-button type="primary" @click="router.push('/agent-editor')" :icon="Plus">
              创建第一个智能体
            </el-button>
          </el-empty>

          <!-- 原有的分页 -->
          <div class="pagination" v-if="agents.length > 0">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[12, 24, 36, 48]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              background
            />
          </div>
        </template>

        <!-- 我关注的智能体 -->
        <template v-else>
          <el-skeleton :rows="3" animated v-if="loadingFollowed" />
          
          <div v-else class="agent-grid">
            <el-card v-for="agent in followedAgents" :key="agent.id" class="agent-card" shadow="hover">
              <div class="agent-content">
                <!-- 智能体封面图 -->
                <div class="agent-cover-wrapper" @click="viewAgentDetails(agent)">
                  <el-image 
                    :src="agent.coverImage" 
                    fit="cover" 
                    class="agent-cover"
                    :preview-src-list="[agent.coverImage]"
                  >
                    <template #error>
                      <div class="image-placeholder">
                        <el-icon :size="40"><Picture /></el-icon>
                      </div>
                    </template>
                  </el-image>
                  <div class="agent-stats-overlay">
                    <div class="stat-item">
                      <el-icon><View /></el-icon>
                      <span>{{ agent.views }}</span>
                    </div>
                    <div class="stat-item">
                      <el-icon><Star /></el-icon>
                      <span>{{ agent.likes }}</span>
                    </div>
                    <div class="stat-item">
                      <el-icon><ChatDotRound /></el-icon>
                      <span>{{ agent.comments }}</span>
                    </div>
                  </div>
                </div>
                
                <!-- 智能体名称和描述 -->
                <div class="agent-info">
                  <h3 class="agent-name" @click="viewAgentDetails(agent)">{{ agent.name }}</h3>
                  <p class="agent-description">{{ agent.description }}</p>
                </div>
                
                <!-- 操作按钮 -->
                <div class="agent-actions">
                  <el-button type="primary" size="small" @click="router.push(`/chat/${agent.id}`)">
                    <el-icon class="el-icon--left"><ChatDotRound /></el-icon>对话
                  </el-button>
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="unfollowAgent(agent)"
                  >
                    <el-icon class="el-icon--left"><Star /></el-icon>取消关注
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 空状态展示 -->
          <el-empty 
            v-if="!loadingFollowed && followedAgents.length === 0" 
            description="暂无关注的智能体" 
            :image-size="200"
          >
            <el-button type="primary" @click="router.push('/community')">
              去社区发现智能体
            </el-button>
          </el-empty>

          <!-- 分页 -->
          <div class="pagination" v-if="followedAgents.length > 0">
            <el-pagination
              v-model:current-page="followedCurrentPage"
              v-model:page-size="followedPageSize"
              :page-sizes="[12, 24, 36, 48]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="followedTotal"
              @size-change="handleFollowedSizeChange"
              @current-change="handleFollowedCurrentChange"
              background
            />
          </div>
        </template>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  More, 
  View, 
  Star, 
  ChatDotRound, 
  ArrowLeft, 
  Edit, 
  Delete, 
  Share, 
  Plus,
  Picture,
  Link
} from '@element-plus/icons-vue'

const router = useRouter()
const agents = ref([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const loading = ref(true)
const activeTab = ref('created')
const followedAgents = ref([])
const followedCurrentPage = ref(1)
const followedPageSize = ref(12)
const followedTotal = ref(0)
const loadingFollowed = ref(false)

// 获取用户智能体列表
const fetchAgents = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }

    // 构建请求参数
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      size: pageSize.value.toString()
    })
    
    // 发送请求 - 使用与Community.vue相同的API路径
    const response = await fetch(`/user/agents/list`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error('获取智能体列表失败')
    }
    
    const result = await response.json()
    console.log('获取智能体列表成功:', result)
    
    if (result.code === 200) {
      agents.value = (result.data || []).map(item => ({
        id: item.id,
        name: item.name || '未命名智能体',
        description: item.description || '暂无描述',
        coverImage: item.avatar || 'https://picsum.photos/300/200',
        views: item.viewCount || item.views || 0,
        likes: item.likeCount || item.likes || 0,
        comments: item.commentCount || item.comments || 0,
        isOpenSource: item.is_OpenSource || false
      }))
      console.log('智能体列表:', agents.value)
      total.value = Math.ceil(agents.value.length / pageSize.value) || 0
    } else {
      throw new Error(result.message || '获取智能体列表失败')
    }
  } catch (error) {
    console.error('获取智能体列表失败:', error)
    ElMessage.error('获取智能体列表失败，请稍后重试')
    
    // 模拟数据（开发阶段使用）
    agents.value = [
      {
        id: 1,
        name: '智能助手',
        description: '一个多功能的AI助手，可以帮助你处理各种任务',
        coverImage: 'https://picsum.photos/300/200',
        views: 1000,
        likes: 500,
        comments: 200,
        isOpenSource: false
      },
      {
        id: 2,
        name: '代码专家',
        description: '专业的编程助手，能够帮助解决各种编程问题，提供代码优化建议',
        coverImage: 'https://picsum.photos/300/200',
        views: 2500,
        likes: 1200,
        comments: 450,
        isOpenSource: false
      },
      {
        id: 3,
        name: '语言翻译官',
        description: '支持多语言实时翻译，准确理解上下文，提供自然流畅的翻译结果',
        coverImage: 'https://picsum.photos/300/200',
        views: 1800,
        likes: 800,
        comments: 300,
        isOpenSource: false
      },
      {
        id: 4,
        name: '数据分析师',
        description: '强大的数据分析能力，帮助用户理解和处理复杂的数据集',
        coverImage: 'https://picsum.photos/300/200',
        views: 1500,
        likes: 700,
        comments: 250,
        isOpenSource: false
      },
      {
        id: 5,
        name: '创意写作助手',
        description: '激发创作灵感，帮助撰写各种类型的文章，从诗歌到商业文案',
        coverImage: 'https://picsum.photos/300/200',
        views: 2000,
        likes: 900,
        comments: 350,
        isOpenSource: false
      },
      {
        id: 6,
        name: '学习导师',
        description: '个性化的学习助手，根据用户的学习进度和需求提供定制化的学习建议',
        coverImage: 'https://picsum.photos/300/200',
        views: 3000,
        likes: 1500,
        comments: 600,
        isOpenSource: false
      }
    ]
    total.value = agents.value.length
  } finally {
    loading.value = false
  }
}

// 获取关注的智能体列表
const fetchFollowedAgents = async () => {
  try {
    loadingFollowed.value = true
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }

    // 构建请求参数
    const params = new URLSearchParams({
      page: followedCurrentPage.value.toString(),
      size: followedPageSize.value.toString()
    })
    
    // 发送请求
    const response = await fetch(`/user/followed/agents`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error('获取关注的智能体列表失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      followedAgents.value = (result.data || []).map(item => ({
        id: item.id,
        name: item.name || '未命名智能体',
        description: item.description || '暂无描述',
        coverImage: item.avatar || 'https://picsum.photos/300/200',
        views: item.viewCount || item.views || 0,
        likes: item.likeCount || item.likes || 0,
        comments: item.commentCount || item.comments || 0
      }))
      followedTotal.value = result.total || followedAgents.value.length
    } else {
      throw new Error(result.message || '获取关注的智能体列表失败')
    }
  } catch (error) {
    console.error('获取关注的智能体列表失败:', error)
    ElMessage.error('获取关注的智能体列表失败，请稍后重试')
    
    // 开发阶段模拟数据
    followedAgents.value = [
      {
        id: 7,
        name: '金融顾问',
        description: '专业的金融分析和投资建议助手',
        coverImage: 'https://picsum.photos/300/200',
        views: 2800,
        likes: 1400,
        comments: 550
      },
      {
        id: 8,
        name: '健康顾问',
        description: '提供健康生活方式和饮食建议的智能助手',
        coverImage: 'https://picsum.photos/300/200',
        views: 3200,
        likes: 1600,
        comments: 700
      }
    ]
    followedTotal.value = followedAgents.value.length
  } finally {
    loadingFollowed.value = false
  }
}

// 编辑智能体
const editAgent = async (agent) => {
  try {
    // 清除本地可能存在的旧数据
    localStorage.removeItem('agentData')
    localStorage.removeItem('selectedKnowledgeBases')
    localStorage.removeItem('selectedWorkflowId')
    
    // 设置编辑模式标记
    localStorage.setItem('agentEditMode', 'true')
    localStorage.setItem('agentEditId', agent.id)
    
    // 跳转到编辑页面
    router.push(`/agent-editor/${agent.id}`)
  } catch (error) {
    console.error('准备编辑数据失败:', error)
    ElMessage.error('启动编辑失败，请重试')
  }
}

// 删除智能体
const deleteAgent = (agent) => {
  ElMessageBox.confirm(
    `确定要删除智能体 "${agent.name}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      distinguishCancelAndClose: true,
      closeOnClickModal: false
    }
  ).then(async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        router.push('/login')
        return
      }

      // 调用后端API删除智能体
      const response = await fetch(`/user/agent/${agent.id}/delete`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || '删除智能体失败')
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        ElMessage.success(result.message || '智能体删除成功')
        // 重新加载智能体列表
        fetchAgents()
      } else {
        throw new Error(result.message || '删除智能体失败')
      }
    } catch (error) {
      console.error('删除智能体失败:', error)
      ElMessage.error(`删除失败: ${error.message || '请稍后重试'}`)
    }
  }).catch(action => {
    if (action !== 'cancel') {
      console.error('删除对话框出错:', action)
    }
  })
}

// 分享智能体
const shareAgent = (agent) => {
  // 实现分享功能
  try {
    // 构建分享链接
    const shareUrl = `${window.location.origin}/agent/${agent.id}`
    
    // 尝试使用 Navigator Clipboard API
    navigator.clipboard.writeText(shareUrl)
      .then(() => {
        ElMessage.success('分享链接已复制到剪贴板')
      })
      .catch(() => {
        // 回退方法（用于不支持 clipboard API 的浏览器）
        const textarea = document.createElement('textarea')
        textarea.value = shareUrl
        textarea.style.position = 'fixed'
        document.body.appendChild(textarea)
        textarea.focus()
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
        ElMessage.success('分享链接已复制到剪贴板')
      })
  } catch (error) {
    console.error('分享失败:', error)
    ElMessage.error('分享失败，请手动复制链接')
  }
}

// 切换开源状态
const toggleOpenSource = async (agent) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }

    const response = await fetch(`/user/OpenAgent/${agent.id}/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        isOpen: !agent.isOpenSource
      })
    })

    if (!response.ok) {
      throw new Error('更新开源状态失败')
    }

    const result = await response.json()
    
    if (result.code === 200) {
      ElMessage.success(result.message || '开源状态更新成功')
      // 更新本地状态
      agent.isOpenSource = result.is_OpenSource
    } else {
      throw new Error(result.message || '更新开源状态失败')
    }
  } catch (error) {
    console.error('更新开源状态失败:', error)
    ElMessage.error(`更新失败: ${error.message || '请稍后重试'}`)
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchAgents()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchAgents()
}

const handleFollowedSizeChange = (val) => {
  followedPageSize.value = val
  fetchFollowedAgents()
}

const handleFollowedCurrentChange = (val) => {
  followedCurrentPage.value = val
  fetchFollowedAgents()
}

// 标签页切换处理
watch(() => activeTab.value, (newVal) => {
  if (newVal === 'followed') {
    fetchFollowedAgents()
  } else {
    fetchAgents()
  }
})

onMounted(() => {
  fetchAgents()
  fetchFollowedAgents() // 初始加载时获取关注的智能体
})
</script>

<style scoped>
.my-agent-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.agent-tabs {
  margin-bottom: 24px;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.agent-card {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 8px;
  overflow: hidden;
}

.agent-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
}

.agent-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.agent-cover-wrapper {
  position: relative;
  width: 100%;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
}

.agent-cover {
  width: 100%;
  height: 100%;
  transition: transform 0.3s ease;
}

.agent-cover-wrapper:hover .agent-cover {
  transform: scale(1.05);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  color: #909399;
}

.agent-stats-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  display: flex;
  justify-content: space-around;
  color: white;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.agent-info {
  padding: 0 4px;
}

.agent-name {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  cursor: pointer;
  transition: color 0.3s ease;
}

.agent-name:hover {
  color: #409EFF;
}

.agent-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.agent-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  width: 100%;
}

.agent-actions .el-button {
  width: 100%;
  justify-content: center;
  margin: 0;
  padding: 8px 15px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

@media screen and (max-width: 768px) {
  .my-agent-container {
    padding: 16px;
  }
  
  .agent-grid {
    grid-template-columns: 1fr;
  }
  
  .agent-actions {
    grid-template-columns: 1fr;
  }
}

.agent-tabs {
  margin-bottom: 20px;
}
</style>
