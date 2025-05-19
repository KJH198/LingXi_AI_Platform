<template>
  <div class="user-profile-detail">
    <!-- 顶部导航 -->
    <div class="nav-bar">
      <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
      <h2>用户主页</h2>
      <div></div>
    </div>

    <el-container>
      <el-main>
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="3" animated />
          <el-skeleton :rows="5" animated style="margin-top: 20px" />
        </div>

        <!-- 用户基本信息 -->
        <div v-else-if="userInfo" class="user-info-container">
          <el-card class="user-info-card">
            <div class="user-header">
              <div class="avatar-container">
                <el-avatar :size="100" :src="userInfo.avatar" />
              </div>
              <div class="user-details">
                <h2>{{ userInfo.username }}</h2>
                <p class="user-bio">{{ userInfo.bio || '这个人很懒，什么都没留下...' }}</p>
                <div class="user-stats">
                  <div class="stat-item">
                    <div class="stat-count">{{ userInfo.followersCount }}</div>
                    <div class="stat-label">粉丝</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-count">{{ userInfo.followingCount }}</div>
                    <div class="stat-label">关注</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-count">{{ userInfo.postsCount }}</div>
                    <div class="stat-label">帖子</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-count">{{ userInfo.agentsCount }}</div>
                    <div class="stat-label">智能体</div>
                  </div>
                </div>
              </div>
              <div class="user-actions">
                <el-button 
                  type="primary" 
                  :plain="!userInfo.isFollowed"
                  @click="toggleFollow"
                  class="follow-button"
                >
                  {{ userInfo.isFollowed ? '已关注' : '关注' }}
                </el-button>
                <el-button @click="copyUserLink">
                  <el-icon><Share /></el-icon> 分享
                </el-button>
              </div>
            </div>
          </el-card>

          <!-- 内容选项卡 -->
          <div class="content-tabs">
            <el-tabs v-model="activeTab">
              <el-tab-pane label="帖子" name="posts">
                <div v-if="userPosts.length === 0" class="empty-content">
                  <el-empty description="暂无帖子" />
                </div>
                <div v-else class="post-list">
                  <el-card v-for="post in userPosts" :key="post.id" class="post-card">
                    <div class="post-header">
                      <div class="post-title">
                        <h3>{{ post.title }}</h3>
                        <span class="post-time">{{ post.time }}</span>
                      </div>
                    </div>
                    <div class="post-content">
                      <p>{{ post.content }}</p>
                      
                      <!-- 图片展示 -->
                      <div class="post-images" v-if="post.images && post.images.length">
                        <el-image 
                          v-for="(img, index) in post.images" 
                          :key="index"
                          :src="img"
                          :preview-src-list="post.images"
                          fit="cover"
                          class="post-image"
                        />
                      </div>
                    </div>
                    <div class="post-footer">
                      <div class="post-actions">
                        <el-button 
                          :type="post.isLiked ? 'primary' : 'text'" 
                          @click="toggleLike(post)"
                        >
                          <el-icon><Star /></el-icon>
                          {{ post.likes }}
                        </el-button>
                        <el-button type="text">
                          <el-icon><ChatDotRound /></el-icon>
                          {{ post.comments.length }}
                        </el-button>
                        <el-button type="text" @click="sharePost(post)">
                          <el-icon><Share /></el-icon>
                          分享
                        </el-button>
                      </div>
                    </div>
                  </el-card>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="智能体" name="agents">
                <div v-if="userAgents.length === 0" class="empty-content">
                  <el-empty description="暂无智能体" />
                </div>
                <div v-else class="agent-list">
                  <el-card v-for="agent in userAgents" :key="agent.id" class="agent-card" @click="viewAgentDetail(agent.id)">
                    <div class="agent-header">
                      <div class="agent-icon">AI</div>
                      <div class="agent-info">
                        <h3>{{ agent.name }}</h3>
                        <p>{{ agent.description }}</p>
                      </div>
                      <div class="agent-actions" @click.stop>
                        <el-button 
                          size="small" 
                          :type="agent.isFollowed ? 'success' : 'primary'"
                          @click="toggleAgentFollow(agent)"
                        >
                          {{ agent.isFollowed ? '已关注' : '关注' }}
                        </el-button>
                      </div>
                    </div>
                    <div class="agent-footer">
                      <div class="agent-stats">
                        <span>{{ agent.followCount }} 关注</span>
                        <span>{{ agent.usageCount }} 使用</span>
                      </div>
                      <el-button type="primary" size="small" @click.stop="useAgent(agent)">使用</el-button>
                    </div>
                  </el-card>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="知识库" name="knowledgeBases">
                <div v-if="userKnowledgeBases.length === 0" class="empty-content">
                  <el-empty description="暂无知识库" />
                </div>
                <div v-else class="kb-list">
                  <el-card v-for="kb in userKnowledgeBases" :key="kb.id" class="kb-card" @click="viewKnowledgeBaseDetail(kb.id)">
                    <div class="kb-header">
                      <div class="kb-icon">KB</div>
                      <div class="kb-info">
                        <h3>{{ kb.name }}</h3>
                        <p>{{ kb.description }}</p>
                      </div>
                      <div class="kb-actions" @click.stop>
                        <el-button 
                          size="small" 
                          :type="kb.isFollowed ? 'success' : 'primary'"
                          @click="toggleKnowledgeBaseFollow(kb)"
                        >
                          {{ kb.isFollowed ? '已关注' : '关注' }}
                        </el-button>
                      </div>
                    </div>
                    <div class="kb-footer">
                      <div class="kb-stats">
                        <span>{{ kb.followCount }} 关注</span>
                        <span>{{ kb.fileCount }} 文件</span>
                      </div>
                      <el-tag size="small">{{ kb.type }}</el-tag>
                    </div>
                  </el-card>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>

        <!-- 用户不存在 -->
        <el-empty v-else description="用户不存在或已被删除" />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Star, 
  ChatDotRound, 
  Share, 
  ArrowLeft,
  Warning
} from '@element-plus/icons-vue'

// 路由相关
const route = useRoute()
const router = useRouter()
const userId = ref(route.params.id as string)

// 基础数据
const loading = ref(true)
const activeTab = ref('posts')
const userInfo = ref(null)
const userPosts = ref([])
const userAgents = ref([])
const userKnowledgeBases = ref([])

// 返回上一页
const goBack = () => {
  router.back()
}

// 监听路由变化，重新加载数据
watch(() => route.params.id, (newId) => {
  if (newId) {
    userId.value = newId as string
    fetchUserData()
  }
})

// 获取用户数据
const fetchUserData = async () => {
  loading.value = true
  
  try {
    const token = localStorage.getItem('token')
    
    // 获取用户基本信息
    const response = await fetch(`/user/${userId.value}/profile/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    })
    
    if (!response.ok) {
      throw new Error('获取用户信息失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      userInfo.value = result.data
      
      // 加载用户的帖子、智能体和知识库数据
      Promise.all([
        fetchUserPosts(),
        fetchUserAgents(),
        fetchUserKnowledgeBases()
      ])
    } else {
      throw new Error(result.message || '获取用户信息失败')
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    
    // 模拟数据（开发阶段使用）
    setTimeout(() => {
      userInfo.value = {
        id: userId.value,
        username: '示例用户',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        bio: '这是一个示例用户的个人简介，展示在用户资料页面。',
        followersCount: 128,
        followingCount: 56,
        postsCount: 23,
        agentsCount: 5,
        isFollowed: false
      }
      
      // 加载示例数据
      loadMockData()
    }, 500)
  } finally {
    loading.value = false
  }
}

// 获取用户帖子
const fetchUserPosts = async () => {
  try {
    const token = localStorage.getItem('token')
    
    const response = await fetch(`/user/${userId.value}/posts/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    })
    
    if (!response.ok) {
      throw new Error('获取用户帖子失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      userPosts.value = result.data
    } else {
      throw new Error(result.message || '获取用户帖子失败')
    }
  } catch (error) {
    console.error('获取用户帖子失败:', error)
  }
}

// 获取用户智能体
const fetchUserAgents = async () => {
  try {
    const token = localStorage.getItem('token')
    
    const response = await fetch(`/user/${userId.value}/agents/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    })
    
    if (!response.ok) {
      throw new Error('获取用户智能体失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      userAgents.value = result.data
    } else {
      throw new Error(result.message || '获取用户智能体失败')
    }
  } catch (error) {
    console.error('获取用户智能体失败:', error)
  }
}

// 获取用户知识库
const fetchUserKnowledgeBases = async () => {
  try {
    const token = localStorage.getItem('token')
    
    const response = await fetch(`/user/${userId.value}/knowledge-bases/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    })
    
    if (!response.ok) {
      throw new Error('获取用户知识库失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      userKnowledgeBases.value = result.data
    } else {
      throw new Error(result.message || '获取用户知识库失败')
    }
  } catch (error) {
    console.error('获取用户知识库失败:', error)
  }
}

// 加载模拟数据（开发阶段使用）
const loadMockData = () => {
  // 模拟帖子数据
  userPosts.value = [
    {
      id: 1,
      title: '分享一个AI写作技巧',
      content: '最近发现一个很有用的AI写作技巧，可以让生成的内容更加自然流畅...',
      time: '2025-04-28 15:20',
      likes: 45,
      isLiked: false,
      comments: [
        { id: 1, content: '非常实用，谢谢分享！', username: '用户A' }
      ],
      images: [
        'https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg'
      ]
    },
    {
      id: 2,
      title: '我的智能助手使用心得',
      content: '使用智能助手已经一个月了，分享一下我的使用心得和技巧...',
      time: '2025-04-25 09:15',
      likes: 32,
      isLiked: true,
      comments: [
        { id: 2, content: '学到了很多，感谢！', username: '用户B' },
        { id: 3, content: '我也有类似的体验', username: '用户C' }
      ]
    }
  ]
  
  // 模拟智能体数据
  userAgents.value = [
    {
      id: 'agent1',
      name: '学习助手',
      description: '帮助整理笔记和学习资料的智能体',
      followCount: 128,
      usageCount: 1024,
      isFollowed: false
    },
    {
      id: 'agent2',
      name: '编程教练',
      description: '辅助编程学习和解决问题的智能体',
      followCount: 256,
      usageCount: 2048,
      isFollowed: true
    },
    {
      id: 'agent3',
      name: '创意写作助手',
      description: '帮助创意写作和灵感激发的智能体',
      followCount: 96,
      usageCount: 768,
      isFollowed: false
    }
  ]
  
  // 模拟知识库数据
  userKnowledgeBases.value = [
    {
      id: 'kb1',
      name: '机器学习基础',
      description: '包含机器学习基础理论和实践案例的知识库',
      followCount: 156,
      fileCount: 25,
      type: '技术文档',
      isFollowed: true
    },
    {
      id: 'kb2',
      name: '产品设计资料',
      description: '产品设计相关的方法论和实践案例',
      followCount: 89,
      fileCount: 18,
      type: '设计文档',
      isFollowed: false
    }
  ]
}

// 关注/取关用户
const toggleFollow = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const isFollowed = userInfo.value.isFollowed
    
    // 关注/取消关注请求
    const response = await fetch(`/user/follow/${userId.value}/`, {
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
      userInfo.value.isFollowed = !isFollowed
      userInfo.value.followersCount = isFollowed 
        ? userInfo.value.followersCount - 1 
        : userInfo.value.followersCount + 1
      
      ElMessage.success(isFollowed ? '已取消关注' : '关注成功')
    } else {
      throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
    }
  } catch (error) {
    console.error('关注用户操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
    
    // 开发阶段模拟
    userInfo.value.isFollowed = !userInfo.value.isFollowed
    userInfo.value.followersCount = userInfo.value.isFollowed 
      ? userInfo.value.followersCount + 1 
      : userInfo.value.followersCount - 1
    
    ElMessage.success(userInfo.value.isFollowed ? '关注成功' : '已取消关注')
  }
}

// 点赞/取消点赞帖子
const toggleLike = async (post) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const isLiked = post.isLiked
    
    // 点赞/取消点赞请求
    const response = await fetch(`/post/like/${post.id}/`, {
      method: isLiked ? 'DELETE' : 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(isLiked ? '取消点赞失败' : '点赞失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      // 更新状态
      post.isLiked = !isLiked
      post.likes = isLiked ? post.likes - 1 : post.likes + 1
      
      ElMessage.success(isLiked ? '已取消点赞' : '点赞成功')
    } else {
      throw new Error(result.message || (isLiked ? '取消点赞失败' : '点赞失败'))
    }
  } catch (error) {
    console.error('点赞帖子操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
    
    // 开发阶段模拟
    post.isLiked = !post.isLiked
    post.likes = post.isLiked ? post.likes + 1 : post.likes - 1
    
    ElMessage.success(post.isLiked ? '点赞成功' : '已取消点赞')
  }
}

// 关注/取消关注智能体
const toggleAgentFollow = async (agent) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const isFollowed = agent.isFollowed
    
    // 关注/取消关注请求
    const response = await fetch(`/agent/follow/${agent.id}/`, {
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
      agent.followCount = isFollowed ? agent.followCount - 1 : agent.followCount + 1
      
      ElMessage.success(isFollowed ? '已取消关注智能体' : '关注智能体成功')
    } else {
      throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
    }
  } catch (error) {
    console.error('关注智能体操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
    
    // 开发阶段模拟
    agent.isFollowed = !agent.isFollowed
    agent.followCount = agent.isFollowed ? agent.followCount + 1 : agent.followCount - 1
    
    ElMessage.success(agent.isFollowed ? '关注智能体成功' : '已取消关注智能体')
  }
}

// 关注/取消关注知识库
const toggleKnowledgeBaseFollow = async (kb) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const isFollowed = kb.isFollowed
    
    // 关注/取消关注请求
    const response = await fetch(`/knowledge-base/follow/${kb.id}/`, {
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
      kb.isFollowed = !isFollowed
      kb.followCount = isFollowed ? kb.followCount - 1 : kb.followCount + 1
      
      ElMessage.success(isFollowed ? '已取消关注知识库' : '关注知识库成功')
    } else {
      throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
    }
  } catch (error) {
    console.error('关注知识库操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
    
    // 开发阶段模拟
    kb.isFollowed = !kb.isFollowed
    kb.followCount = kb.isFollowed ? kb.followCount + 1 : kb.followCount - 1
    
    ElMessage.success(kb.isFollowed ? '关注知识库成功' : '已取消关注知识库')
  }
}

// 使用智能体
const useAgent = (agent) => {
  // 跳转到智能体使用页面
  router.push('/chat/' + agent.id)
}

// 查看智能体详情
const viewAgentDetail = (agentId) => {
  router.push(`/agent-detail/${agentId}`)
}

// 查看知识库详情
const viewKnowledgeBaseDetail = (kbId) => {
  router.push(`/knowledge-base/${kbId}`)
}

// 分享帖子
const sharePost = (post) => {
  const shareUrl = `${window.location.origin}/#/post/${post.id}`
  
  // 复制链接到剪贴板
  navigator.clipboard.writeText(shareUrl).then(() => {
    ElMessage.success('链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('链接复制失败，请手动复制')
    // 显示分享链接
    ElMessageBox.alert(shareUrl, '分享链接', {
      confirmButtonText: '关闭'
    })
  })
}

// 复制用户主页链接
const copyUserLink = () => {
  const userLink = `${window.location.origin}/#/user-profile/${userId.value}`
  
  navigator.clipboard.writeText(userLink).then(() => {
    ElMessage.success('用户主页链接已复制')
  }).catch(() => {
    ElMessage.error('链接复制失败')
    ElMessageBox.alert(userLink, '用户主页链接', {
      confirmButtonText: '关闭'
    })
  })
}

// 举报用户
const reportUser = () => {
  ElMessageBox.prompt('请输入举报原因', '举报用户', {
    confirmButtonText: '提交',
    cancelButtonText: '取消',
    inputPlaceholder: '请简要说明您举报的原因'
  }).then(({ value }) => {
    if (value.trim()) {
      // 提交举报
      ElMessage.success('举报已提交，感谢您的反馈')
    } else {
      ElMessage.warning('请输入举报原因')
    }
  }).catch(() => {})
}

// 组件挂载时获取数据
onMounted(() => {
  if (userId.value) {
    fetchUserData()
  }
})
</script>

<style scoped>
.user-profile-detail {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.loading-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.user-info-container {
  max-width: 800px;
  margin: 20px auto;
}

.user-info-card {
  margin-bottom: 20px;
}

.user-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 10px;
}

.avatar-container {
  flex-shrink: 0;
}

.user-details {
  flex: 1;
}

.user-bio {
  color: #606266;
  margin: 10px 0;
}

.user-stats {
  display: flex;
  gap: 20px;
  margin-top: 15px;
}

.stat-item {
  text-align: center;
}

.stat-count {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.user-actions {
  display: flex;
  gap: 10px;
}

.follow-button {
  min-width: 80px;
}

.content-tabs {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.empty-content {
  padding: 40px 0;
}

.post-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.post-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.post-title {
  flex: 1;
}

.post-time {
  font-size: 12px;
  color: #909399;
}

.post-content {
  margin: 10px 0;
}

.post-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  margin: 10px 0;
}

.post-image {
  width: 100%;
  height: 150px;
  border-radius: 4px;
  object-fit: cover;
  cursor: pointer;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  border-top: 1px solid #ebeef5;
  padding-top: 10px;
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.agent-card, .kb-card {
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.agent-card:hover, .kb-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.agent-header, .kb-header {
  display: flex;
  align-items: center;
  gap: 15px;
}

.agent-icon, .kb-icon {
  width: 50px;
  height: 50px;
  background-color: #ecf5ff;
  color: #409eff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  flex-shrink: 0;
}

.agent-info, .kb-info {
  flex: 1;
  min-width: 0;
}

.agent-info h3, .kb-info h3 {
  margin: 0 0 5px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.agent-info p, .kb-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.agent-actions, .kb-actions {
  flex-shrink: 0;
}

.agent-footer, .kb-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  border-top: 1px solid #ebeef5;
  padding-top: 10px;
}

.agent-stats, .kb-stats {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #606266;
}
</style>
