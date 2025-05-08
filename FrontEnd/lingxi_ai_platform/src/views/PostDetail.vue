<template>
    <div class="post-detail-container">
      <!-- 导航栏 -->
      <div class="post-header">
        <el-button type="text" @click="goBack" class="back-btn">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <h1>帖子详情</h1>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton animated>
          <template #template>
            <el-skeleton-item variant="image" style="width: 100%; height: 240px" />
            <div style="padding: 14px">
              <el-skeleton-item variant="h3" style="width: 50%" />
              <div style="display: flex; align-items: center; margin-top: 16px">
                <el-skeleton-item variant="circle" style="margin-right: 16px; width: 40px; height: 40px" />
                <el-skeleton-item variant="text" style="width: 30%" />
              </div>
              <el-skeleton-item variant="text" style="margin-top: 16px; width: 100%" />
              <el-skeleton-item variant="text" style="width: 100%" />
              <el-skeleton-item variant="text" style="width: 100%" />
            </div>
          </template>
        </el-skeleton>
      </div>
      
      <!-- 帖子内容区域 -->
      <div v-else-if="postData" class="post-content">
        <!-- 标题 -->
        <div class="post-title">
          <h2>{{ postData.title }}</h2>
        </div>
        
        <!-- 作者信息 -->
        <div class="author-info">
          <el-avatar :src="postData.author.avatar" @click="viewUserProfile(postData.author.id)" class="author-avatar">
            {{ getAvatarFallback(postData.author.username) }}
          </el-avatar>
          <div class="author-meta">
            <div class="author-name" @click="viewUserProfile(postData.author.id)">
              {{ postData.author.username }}
            </div>
            <div class="post-time">{{ postData.time }}</div>
          </div>
          <el-button 
            v-if="isLoggedIn && userId !== postData.author.id"
            :type="postData.isAuthorFollowed ? 'success' : 'primary'"
            size="small"
            @click="toggleFollowAuthor"
          >
            {{ postData.isAuthorFollowed ? '已关注' : '关注' }}
          </el-button>
        </div>
        
        <!-- 帖子内容 -->
        <div class="post-body">
          <!-- 文本内容 -->
          <div class="post-text" v-html="formatContent(postData.content)"></div>
          
          <!-- 图片内容 -->
          <div v-if="postData.images && postData.images.length" class="post-images">
            <el-image
              v-for="(img, index) in postData.images"
              :key="index"
              :src="img"
              :preview-src-list="postData.images"
              fit="cover"
              class="post-image"
            />
          </div>
          
          <!-- 关联智能体 -->
          <div v-if="postData.agents && postData.agents.length > 0" class="linked-agents">
            <h3>关联的智能体</h3>
            <el-card 
              v-for="agent in postData.agents" 
              :key="agent.id" 
              class="agent-card"
              shadow="hover"
              @click="viewAgentDetail(agent.id)"
            >
              <div class="agent-card-content">
                <el-avatar :src="agent.avatar" class="agent-avatar">AI</el-avatar>
                <div class="agent-info">
                  <div class="agent-name">{{ agent.name }}</div>
                  <div class="agent-desc">{{ agent.description }}</div>
                </div>
                <el-button 
                  :type="agent.isFollowed ? 'success' : 'primary'"
                  size="small"
                  @click.stop="toggleFollowAgent(agent)"
                >
                  {{ agent.isFollowed ? '已关注' : '关注' }}
                </el-button>
              </div>
            </el-card>
          </div>
          
          <!-- 关联知识库 -->
          <div v-if="postData.knowledgeBases && postData.knowledgeBases.length > 0" class="linked-kbs">
            <h3>关联的知识库</h3>
            <el-card 
              v-for="kb in postData.knowledgeBases" 
              :key="kb.id" 
              class="kb-card"
              shadow="hover"
              @click="viewKbDetail(kb.id)"
            >
              <div class="kb-card-content">
                <div class="kb-icon">KB</div>
                <div class="kb-info">
                  <div class="kb-name">{{ kb.name }}</div>
                  <div class="kb-desc">{{ kb.description }}</div>
                  <div class="kb-meta">
                    <span>{{ kb.fileCount }} 文件</span>
                    <span>{{ kb.followCount }} 关注</span>
                  </div>
                </div>
                <el-button 
                  :type="kb.isFollowed ? 'success' : 'primary'"
                  size="small"
                  @click.stop="toggleFollowKb(kb)"
                >
                  {{ kb.isFollowed ? '已关注' : '关注' }}
                </el-button>
              </div>
            </el-card>
          </div>
        </div>
        
        <!-- 操作区域 -->
        <div class="post-actions">
          <div class="action-item">
            <el-button 
              type="text" 
              :class="{ 'is-active': postData.isLiked }"
              @click="toggleLike"
            >
              <el-icon><Pointer /></el-icon>
              点赞 {{ postData.likes }}
            </el-button>
          </div>
          
          <div class="action-item">
            <el-button 
              type="text" 
              :class="{ 'is-active': postData.isFavorited }"
              @click="toggleFavorite"
            >
              <el-icon><Star /></el-icon>
              收藏 {{ postData.favorites }}
            </el-button>
          </div>
          
          <div class="action-item">
            <el-button type="text" @click="focusCommentInput">
              <el-icon><ChatDotRound /></el-icon>
              评论 {{ postData.commentCount }}
            </el-button>
          </div>
          
          <div class="action-item view-count">
            <el-icon><View /></el-icon>
            {{ postData.viewCount }} 次浏览
          </div>
        </div>
        
        <!-- 评论区 -->
        <div class="comments-section">
          <h3>全部评论 ({{ postData.commentCount }})</h3>
          
          <!-- 评论输入框 -->
          <div class="comment-input">
            <el-input
              v-model="commentContent"
              type="textarea"
              :rows="2"
              placeholder="写下你的评论..."
              :disabled="!isLoggedIn"
              ref="commentInputRef"
            />
            <el-button 
              type="primary" 
              @click="submitComment"
              :disabled="!isLoggedIn || !commentContent.trim()"
            >
              发表评论
            </el-button>
          </div>
          
          <!-- 评论列表 -->
          <div class="comment-list">
            <el-empty v-if="postData.comments.length === 0" description="暂无评论" />
            
            <div v-else class="comment-item" v-for="comment in postData.comments" :key="comment.id">
              <el-avatar 
                :src="comment.avatar" 
                class="comment-avatar" 
                @click="viewUserProfile(comment.userId)"
              >
                {{ getAvatarFallback(comment.username) }}
              </el-avatar>
              <div class="comment-content">
                <div class="comment-header">
                  <span class="comment-username" @click="viewUserProfile(comment.userId)">
                    {{ comment.username }}
                  </span>
                  <span class="comment-time">{{ comment.time }}</span>
                </div>
                <div class="comment-text">{{ comment.content }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 错误状态 -->
      <el-result
        v-else-if="error"
        icon="error"
        :title="error"
        sub-title="请检查网络连接或稍后重试"
      >
        <template #extra>
          <el-button type="primary" @click="fetchPostData">重试</el-button>
          <el-button @click="goBack">返回</el-button>
        </template>
      </el-result>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, computed } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { 
    ArrowLeft, 
    Pointer, 
    Star, 
    ChatDotRound, 
    View 
  } from '@element-plus/icons-vue'
  import DOMPurify from 'dompurify'
  import { marked } from 'marked'
  
  const route = useRoute()
  const router = useRouter()
  const postId = ref(route.params.id)
  const postData = ref(null)
  const loading = ref(true)
  const error = ref('')
  const commentContent = ref('')
  const commentInputRef = ref(null)
  
  // 获取用户登录状态
  const isLoggedIn = computed(() => {
    return localStorage.getItem('token') !== null
  })
  
  // 获取当前用户ID
  const userId = computed(() => {
    const userInfo = localStorage.getItem('userInfo')
    if (userInfo) {
      try {
        return JSON.parse(userInfo).id
      } catch (e) {
        return null
      }
    }
    return null
  })
  
  // 获取帖子详情
  const fetchPostData = async () => {
    try {
      loading.value = true
      error.value = ''
      
      const token = localStorage.getItem('token')
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
      
      const response = await fetch(`/community/posts/${postId.value}/`, {
        method: 'GET',
        headers
      })
      
      if (!response.ok) {
        throw new Error(`获取帖子详情失败: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        postData.value = result.data
      } else {
        throw new Error(result.message || '获取帖子详情失败')
      }
    } catch (e) {
      console.error('获取帖子详情失败:', e)
      error.value = '获取帖子详情失败'
    } finally {
      loading.value = false
    }
  }
  
  // 返回上一页
  const goBack = () => {
    router.back()
  }
  
  // 点赞/取消点赞
  const toggleLike = async () => {
    try {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录')
        return
      }
      
      const token = localStorage.getItem('token')
      const method = postData.value.isLiked ? 'DELETE' : 'POST'
      
      const response = await fetch(`/user/like/post/${postId.value}/`, {
        method,
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) {
        throw new Error(`操作失败: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        postData.value.likes = postData.value.isLiked ? (postData.value.likes - 1) : (postData.value.likes + 1)
        postData.value.isLiked = !postData.value.isLiked

        ElMessage.success(postData.value.isLiked ? '点赞成功' : '取消点赞成功')
      } else {
        throw new Error(result.message || '操作失败')
      }
    } catch (e) {
      console.error('点赞操作失败:', e)
      ElMessage.error('操作失败，请稍后重试')
    }
  }
  
  // 收藏/取消收藏
  const toggleFavorite = async () => {
    try {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录')
        return
      }
      
      const token = localStorage.getItem('token')
      const method = postData.value.isFavorited ? 'DELETE' : 'POST'
      
      const response = await fetch(`/user/favorite/post/${postId.value}/`, {
        method,
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) {
        throw new Error(`操作失败: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        postData.value.isFavorited = !postData.value.isFavorited
        postData.value.favorites = result.data.favoriteCount
        ElMessage.success(postData.value.isFavorited ? '收藏成功' : '取消收藏成功')
      } else {
        throw new Error(result.message || '操作失败')
      }
    } catch (e) {
      console.error('收藏操作失败:', e)
      ElMessage.error('操作失败，请稍后重试')
    }
  }
  
  // 关注/取消关注作者
  const toggleFollowAuthor = async () => {
    try {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录')
        return
      }
      
      const token = localStorage.getItem('token')
      const authorId = postData.value.author.id
      const method = postData.value.isAuthorFollowed ? 'DELETE' : 'POST'
      
      const response = await fetch(`/user/follow/${authorId}/`, {
        method,
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) {
        throw new Error(`操作失败: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        postData.value.isAuthorFollowed = !postData.value.isAuthorFollowed
        ElMessage.success(postData.value.isAuthorFollowed ? '关注成功' : '取消关注成功')
      } else {
        throw new Error(result.message || '操作失败')
      }
    } catch (e) {
      console.error('关注操作失败:', e)
      ElMessage.error('操作失败，请稍后重试')
    }
  }
  
  // 关注/取消关注智能体
  const toggleFollowAgent = async (agent) => {
    try {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录')
        return
      }
      
      const token = localStorage.getItem('token')
      const method = agent.isFollowed ? 'DELETE' : 'POST'
      
      const response = await fetch(`/user/follow/agent/${agent.id}/`, {
        method,
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) {
        throw new Error(`操作失败: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        agent.isFollowed = !agent.isFollowed
        agent.followCount = agent.isFollowed ? (agent.followCount + 1) : (agent.followCount - 1)
        ElMessage.success(agent.isFollowed ? '关注智能体成功' : '取消关注智能体成功')
      } else {
        throw new Error(result.message || '操作失败')
      }
    } catch (e) {
      console.error('关注智能体操作失败:', e)
      ElMessage.error('操作失败，请稍后重试')
    }
  }
  
  // 关注/取消关注知识库
  const toggleFollowKb = async (kb) => {
    try {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录')
        return
      }
      
      const token = localStorage.getItem('token')
      const method = kb.isFollowed ? 'DELETE' : 'POST'
      
      const response = await fetch(`/user/follow/knowledge-base/${kb.id}/`, {
        method,
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) {
        throw new Error(`操作失败: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        kb.isFollowed = !kb.isFollowed
        kb.followCount = kb.isFollowed ? (kb.followCount + 1) : (kb.followCount - 1)
        ElMessage.success(kb.isFollowed ? '关注知识库成功' : '取消关注知识库成功')
      } else {
        throw new Error(result.message || '操作失败')
      }
    } catch (e) {
      console.error('关注知识库操作失败:', e)
      ElMessage.error('操作失败，请稍后重试')
    }
  }
  
  const fetchLatestComments = async () => {
  try {
    const token = localStorage.getItem('token')
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
    
    const response = await fetch(`/community/posts/${postId.value}/comments/`, {
      method: 'GET',
      headers
    })
    
    if (!response.ok) {
      throw new Error(`获取评论失败: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      postData.value.comments = result.data.items || []
      postData.value.commentCount = result.data.total || 0
    } else {
      throw new Error(result.message || '获取评论失败')
    }
  } catch (e) {
    console.error('获取评论失败:', e)
  }
}
  // 提交评论
  const submitComment = async () => {
    try {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录')
        return
      }
      
      if (!commentContent.value.trim()) {
        ElMessage.warning('评论内容不能为空')
        return
      }
      
      const token = localStorage.getItem('token')
      const response = await fetch(`/user/comment/post/${postId.value}/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: commentContent.value.trim()
        })
      })
      
      if (!response.ok) {
        throw new Error(`发表评论失败: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.code === 200) {        
        // 清空评论输入框
        commentContent.value = ''
        await fetchLatestComments()
        
        ElMessage.success('评论发表成功')
      } else {
        throw new Error(result.message || '发表评论失败')
      }
    } catch (e) {
      console.error('发表评论失败:', e)
      ElMessage.error('发表评论失败，请稍后重试')
    }
  }
  
  // 聚焦评论输入框
  const focusCommentInput = () => {
    if (!isLoggedIn.value) {
      ElMessage.warning('请先登录')
      return
    }
    
    if (commentInputRef.value) {
      commentInputRef.value.focus()
    }
  }
  
  // 查看用户资料
  const viewUserProfile = (userId) => {
    router.push(`/user-profile/${userId}`)
  }
  
  // 查看智能体详情
  const viewAgentDetail = (agentId) => {
    router.push(`/agent-detail/${agentId}`)
  }
  
  // 查看知识库详情
  const viewKbDetail = (kbId) => {
    router.push(`/knowledge-base/${kbId}`)
  }
  
  // 获取头像占位符
  const getAvatarFallback = (username) => {
    return username ? username.charAt(0).toUpperCase() : 'U'
  }
  // 格式化帖子内容，支持Markdown和防XSS
  // 格式化帖子内容，支持Markdown和防XSS
  const formatContent = (content) => {
    if (!content) return ''
  
    // 使用类型断言
    const rawHtml = marked.parse(content) as string
    return DOMPurify.sanitize(rawHtml)
}
  
  // 加载帖子数据
  onMounted(() => {
    fetchPostData()
  })
  </script>
  
  <style scoped>
  .post-detail-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .post-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    border-bottom: 1px solid #ebeef5;
    padding-bottom: 15px;
  }
  
  .back-btn {
    margin-right: 15px;
  }
  
  .post-header h1 {
    margin: 0;
    font-size: 22px;
    font-weight: 600;
  }
  
  .post-title h2 {
    font-size: 24px;
    margin-bottom: 20px;
  }
  
  .author-info {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .author-avatar {
    cursor: pointer;
  }
  
  .author-meta {
    margin-left: 12px;
    flex: 1;
  }
  
  .author-name {
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 4px;
    cursor: pointer;
  }
  
  .author-name:hover {
    color: #409eff;
  }
  
  .post-time {
    font-size: 13px;
    color: #909399;
  }
  
  .post-body {
    margin-bottom: 20px;
  }
  
  .post-text {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 20px;
  }
  
  .post-images {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 15px 0;
  }
  
  .post-image {
    width: 180px;
    height: 180px;
    border-radius: 8px;
    object-fit: cover;
  }
  
  .linked-agents, .linked-kbs {
    margin-top: 20px;
  }
  
  .linked-agents h3, .linked-kbs h3 {
    font-size: 18px;
    margin-bottom: 12px;
  }
  
  .agent-card, .kb-card {
    margin-bottom: 12px;
    cursor: pointer;
  }
  
  .agent-card-content, .kb-card-content {
    display: flex;
    align-items: center;
  }
  
  .agent-avatar {
    margin-right: 12px;
  }
  
  .agent-info, .kb-info {
    flex: 1;
    min-width: 0;
  }
  
  .agent-name, .kb-name {
    font-weight: 500;
    margin-bottom: 6px;
  }
  
  .agent-desc, .kb-desc {
    color: #606266;
    font-size: 13px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .kb-meta {
    font-size: 12px;
    color: #909399;
    display: flex;
    gap: 10px;
    margin-top: 6px;
  }
  
  .kb-icon {
    width: 40px;
    height: 40px;
    background-color: #67c23a;
    color: white;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-right: 12px;
  }
  
  .post-actions {
    display: flex;
    padding: 15px 0;
    border-top: 1px solid #ebeef5;
    border-bottom: 1px solid #ebeef5;
    margin-bottom: 20px;
  }
  
  .action-item {
    margin-right: 20px;
    flex-grow: 0;
  }
  
  .action-item .el-button {
    font-size: 14px;
  }
  
  .view-count {
    margin-left: auto;
    color: #909399;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  
  .comments-section {
    margin-top: 30px;
  }
  
  .comments-section h3 {
    font-size: 18px;
    margin-bottom: 15px;
  }
  
  .comment-input {
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .comment-input .el-button {
    align-self: flex-end;
  }
  
  .comment-list {
    margin-top: 20px;
  }
  
  .comment-item {
    display: flex;
    padding: 15px 0;
    border-bottom: 1px solid #f0f2f5;
  }
  
  .comment-avatar {
    cursor: pointer;
  }
  
  .comment-content {
    flex: 1;
    margin-left: 12px;
    min-width: 0;
  }
  
  .comment-header {
    margin-bottom: 6px;
  }
  
  .comment-username {
    font-weight: 500;
    margin-right: 10px;
    cursor: pointer;
  }
  
  .comment-username:hover {
    color: #409eff;
  }
  
  .comment-time {
    font-size: 12px;
    color: #909399;
  }
  
  .comment-text {
    font-size: 14px;
    line-height: 1.6;
  }
  
  .is-active {
    color: #409EFF;
  }
  
  /* 响应式调整 */
  @media (max-width: 768px) {
    .post-detail-container {
      padding: 15px;
    }
    
    .post-image {
      width: 120px;
      height: 120px;
    }
    
    .post-title h2 {
      font-size: 20px;
    }
  }
  </style>