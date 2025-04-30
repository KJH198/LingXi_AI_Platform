<template>
  <div class="my-agent-container">
    <el-container>
      <el-header class="header">
        <h2>我的智能体</h2>
        <el-button type="primary" @click="router.push('/agent-editor')">创建新智能体</el-button>
      </el-header>

      <el-main>
        <div class="agent-grid">
          <el-card v-for="agent in agents" :key="agent.id" class="agent-card">
            <template #header>
              <div class="agent-header">
                <h3>{{ agent.name }}</h3>
                <el-dropdown>
                  <el-button type="text">
                    <el-icon><More /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="editAgent(agent)">编辑</el-dropdown-item>
                      <el-dropdown-item @click="deleteAgent(agent)">删除</el-dropdown-item>
                      <el-dropdown-item @click="shareAgent(agent)">分享</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
            <div class="agent-content">
              <el-image 
                :src="agent.coverImage" 
                fit="cover" 
                class="agent-cover"
              />
              <p class="agent-description">{{ agent.description }}</p>
              <div class="agent-stats">
                <span>
                  <el-icon><View /></el-icon>
                  {{ agent.views }}
                </span>
                <span>
                  <el-icon><Star /></el-icon>
                  {{ agent.likes }}
                </span>
                <span>
                  <el-icon><ChatDotRound /></el-icon>
                  {{ agent.comments }}
                </span>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[12, 24, 36, 48]"
            layout="total, sizes, prev, pager, next"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { More, View, Star, ChatDotRound } from '@element-plus/icons-vue'

const router = useRouter()
const agents = ref([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

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
      // API返回的coverImage可能位于不同路径，需要适配
      coverImage: item.avatar || 'https://picsum.photos/300/200',
      // 统计数据适配
      views: item.viewCount || item.views || 0,
      likes: item.likeCount || item.likes || 0,
      comments: item.commentCount || item.comments || 0
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
        comments: 200
      },
      {
        id: 2,
        name: '代码专家',
        description: '专业的编程助手，能够帮助解决各种编程问题，提供代码优化建议',
        coverImage: 'https://picsum.photos/300/200',
        views: 2500,
        likes: 1200,
        comments: 450
      },
      {
        id: 3,
        name: '语言翻译官',
        description: '支持多语言实时翻译，准确理解上下文，提供自然流畅的翻译结果',
        coverImage: 'https://picsum.photos/300/200',
        views: 1800,
        likes: 800,
        comments: 300
      },
      {
        id: 4,
        name: '数据分析师',
        description: '强大的数据分析能力，帮助用户理解和处理复杂的数据集',
        coverImage: 'https://picsum.photos/300/200',
        views: 1500,
        likes: 700,
        comments: 250
      },
      {
        id: 5,
        name: '创意写作助手',
        description: '激发创作灵感，帮助撰写各种类型的文章，从诗歌到商业文案',
        coverImage: 'https://picsum.photos/300/200',
        views: 2000,
        likes: 900,
        comments: 350
      },
      {
        id: 6,
        name: '学习导师',
        description: '个性化的学习助手，根据用户的学习进度和需求提供定制化的学习建议',
        coverImage: 'https://picsum.photos/300/200',
        views: 3000,
        likes: 1500,
        comments: 600
      }
    ]
    total.value = agents.value.length
  }
}

// 编辑智能体
const editAgent = (agent) => {
  router.push(`/agent-editor/${agent.id}`)
}

// 删除智能体
const deleteAgent = (agent) => {
  ElMessageBox.confirm(
    '确定要删除该智能体吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      // TODO: 调用后端API删除智能体
      ElMessage.success('删除成功')
      fetchAgents()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 分享智能体
const shareAgent = (agent) => {
  // TODO: 实现分享功能
  ElMessage.success('分享链接已复制到剪贴板')
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

onMounted(() => {
  fetchAgents()
})
</script>

<style scoped>
.my-agent-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.agent-card {
  height: 100%;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.agent-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.agent-cover {
  width: 100%;
  height: 200px;
  border-radius: 4px;
}

.agent-description {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  display: -moz-box;
  -moz-line-clamp: 2;
  -moz-box-orient: vertical;
  display: box;
  line-clamp: 2;
  box-orient: vertical;
}

.agent-stats {
  display: flex;
  gap: 20px;
  color: #666;
  font-size: 14px;
}

.agent-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
