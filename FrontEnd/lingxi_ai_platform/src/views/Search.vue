<template>
    <div class="search-container">
      <!-- 顶部搜索栏 -->
      <el-card shadow="never" class="search-header">
        <div class="search-bar">
          <div class="back-button" @click="router.push('/community')">
            <el-icon><ArrowLeft /></el-icon>
            <span>返回社区</span>
          </div>
          <div class="main-search">
            <el-input
              v-model="searchQuery"
              placeholder="搜索帖子、用户、智能体..."
              class="search-input"
              @keyup.enter="executeSearch"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
              <template #append>
                <el-button @click="executeSearch">搜索</el-button>
              </template>
            </el-input>
          </div>
        </div>
        
        <!-- 搜索类型选择 -->
        <div class="search-types">
          <el-radio-group v-model="searchType" @change="handleTypeChange">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button label="posts">帖子</el-radio-button>
            <el-radio-button label="users">用户</el-radio-button>
            <el-radio-button label="agents">智能体</el-radio-button>
            <el-radio-button label="kb">知识库</el-radio-button>
          </el-radio-group>
        </div>
      </el-card>
      
      <!-- 搜索结果显示 -->
      <div class="search-results">
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="3" animated />
          <el-skeleton :rows="3" animated style="margin-top: 20px" />
        </div>
        
        <el-empty v-else-if="noResults" description="没有找到相关结果" />
        
        <div v-else>
          <!-- 显示帖子搜索结果 -->
          <div v-if="(searchType === 'posts' || searchType === 'all') && results.posts.length > 0" class="result-section">
            <h2 class="result-title">帖子 ({{ resultsCount.posts }})</h2>
            <el-card v-for="post in results.posts" :key="post.id" class="post-card">
              <template #header>
                <div class="post-header">
                  <div class="post-title" @click="viewUserProfile(post.userId)">
                    <el-avatar :size="32" :src="post.avatar" />
                    <span class="username">{{ post.username }}</span>
                    <span class="time">{{ post.time }}</span>
                  </div>
                </div>
              </template>
              
              <div class="post-content">
                <h3 v-html="highlightKeyword(post.title)"></h3>
                <p v-html="highlightKeyword(post.content)"></p>
                
                <!-- 图片展示 -->
                <div class="post-images" v-if="post.images && post.images.length">
                  <el-image 
                    v-for="(img, index) in post.images" 
                    :key="index"
                    :src="img"
                    fit="cover"
                    class="post-image"
                  />
                </div>
              </div>
              
              <div class="post-footer">
                <div class="post-actions">
                  <el-button type="text">
                    <el-icon><Star /></el-icon>
                    {{ post.likes }}
                  </el-button>
                  <el-button type="text">
                    <el-icon><ChatDotRound /></el-icon>
                    {{ post.comments.length }}
                  </el-button>
                </div>
                <el-button type="primary" size="small" @click="viewPostDetail(post.id)">查看详情</el-button>
              </div>
            </el-card>
            
            <!-- 帖子分页 -->
            <div v-if="resultsCount.posts > pageSize" class="pagination">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 30, 50]"
                layout="total, sizes, prev, pager, next"
                :total="resultsCount.posts"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </div>
          
          <!-- 显示用户搜索结果 -->
          <div v-if="(searchType === 'users' || searchType === 'all') && results.users.length > 0" class="result-section">
            <h2 class="result-title">用户 ({{ resultsCount.users }})</h2>
            <el-row :gutter="20">
              <el-col v-for="user in results.users" :key="user.id" :xs="24" :sm="12" :md="8" :lg="6">
                <el-card class="user-card" @click="viewUserProfile(user.id)">
                  <div class="user-info">
                    <el-avatar :size="60" :src="user.avatar" />
                    <div class="user-details">
                      <h3 v-html="highlightKeyword(user.username)"></h3>
                      <p v-if="user.bio" v-html="highlightKeyword(user.bio)"></p>
                      <p v-else class="no-bio">这个用户很懒，还没有介绍自己</p>
                    </div>
                  </div>
                  <div class="user-stats">
                    <div>粉丝 {{ user.followersCount }}</div>
                    <div>帖子 {{ user.postsCount }}</div>
                    <div>智能体 {{ user.agentsCount }}</div>
                  </div>
                  <el-button 
                    size="small" 
                    :type="user.isFollowed ? 'success' : 'primary'"
                    @click.stop="followUser(user)"
                  >
                    {{ user.isFollowed ? '已关注' : '关注' }}
                  </el-button>
                </el-card>
              </el-col>
            </el-row>
            
            <!-- 用户分页 -->
            <div v-if="resultsCount.users > pageSize" class="pagination">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[12, 24, 36, 48]"
                layout="total, sizes, prev, pager, next"
                :total="resultsCount.users"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </div>
          
          <!-- 显示智能体搜索结果 -->
          <div v-if="(searchType === 'agents' || searchType === 'all') && results.agents.length > 0" class="result-section">
            <h2 class="result-title">智能体 ({{ resultsCount.agents }})</h2>
            <el-row :gutter="20">
              <el-col v-for="agent in results.agents" :key="agent.id" :xs="24" :sm="12" :md="8">
                <el-card class="agent-card" @click="viewAgentDetail(agent.id)">
                  <div class="agent-info">
                    <div class="agent-avatar">
                      <el-avatar v-if="agent.avatar" :size="60" :src="agent.avatar" />
                      <div v-else class="default-avatar">AI</div>
                    </div>
                    <div class="agent-details">
                      <h3 v-html="highlightKeyword(agent.name)"></h3>
                      <p v-html="highlightKeyword(agent.description)"></p>
                      <div class="agent-creator">
                        <span>创建者: </span>
                        <span class="username" @click.stop="viewUserProfile(agent.creator.id)">
                          {{ agent.creator.username }}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="agent-stats">
                    <span>{{ agent.followCount }} 人关注</span>
                  </div>
                  <el-button 
                    size="small" 
                    :type="agent.isFollowed ? 'success' : 'primary'"
                    @click.stop="followAgent(agent)"
                  >
                    {{ agent.isFollowed ? '已关注' : '关注' }}
                  </el-button>
                </el-card>
              </el-col>
            </el-row>
            
            <!-- 智能体分页 -->
            <div v-if="resultsCount.agents > pageSize" class="pagination">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[12, 24, 36, 48]"
                layout="total, sizes, prev, pager, next"
                :total="resultsCount.agents"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </div>
          
          <!-- 显示知识库搜索结果 -->
          <div v-if="(searchType === 'kb' || searchType === 'all') && results.kb.length > 0" class="result-section">
            <h2 class="result-title">知识库 ({{ resultsCount.kb }})</h2>
            <el-row :gutter="20">
              <el-col v-for="kb in results.kb" :key="kb.id" :xs="24" :sm="12" :md="8">
                <el-card class="kb-card" @click="viewKnowledgeBaseDetail(kb.id)">
                  <div class="kb-info">
                    <div class="kb-icon">KB</div>
                    <div class="kb-details">
                      <h3 v-html="highlightKeyword(kb.name)"></h3>
                      <p v-html="highlightKeyword(kb.description)"></p>
                      <div class="kb-creator">
                        <span>创建者: </span>
                        <span class="username" @click.stop="viewUserProfile(kb.creator.id)">
                          {{ kb.creator.username }}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="kb-stats">
                    <span>{{ kb.fileCount }} 个文件</span>
                    <span>{{ kb.followCount }} 人关注</span>
                  </div>
                  <el-button 
                    size="small" 
                    :type="kb.isFollowed ? 'success' : 'primary'"
                    @click.stop="followKnowledgeBase(kb)"
                  >
                    {{ kb.isFollowed ? '已关注' : '关注' }}
                  </el-button>
                </el-card>
              </el-col>
            </el-row>
            
            <!-- 知识库分页 -->
            <div v-if="resultsCount.kb > pageSize" class="pagination">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[12, 24, 36, 48]"
                layout="total, sizes, prev, pager, next"
                :total="resultsCount.kb"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, reactive, onMounted, computed, watch } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { 
    Search, 
    ArrowLeft, 
    Star, 
    ChatDotRound
  } from '@element-plus/icons-vue'
  
  // 定义接口
  interface Comment {
    id: number;
    username: string;
    avatar: string;
    time: string;
    content: string;
  }
  
  interface Post {
    id: number;
    userId: number;
    username: string;
    avatar: string;
    time: string;
    title: string;
    content: string;
    images?: string[];
    likes: number;
    comments: Comment[];
    agents?: Agent[];
    knowledgeBases?: KnowledgeBase[];
    isLiked?: boolean;
    isFavorited?: boolean;
    isFollowed?: boolean;
  }
  
  interface User {
    id: number;
    username: string;
    avatar: string;
    bio?: string;
    followersCount: number;
    followingCount: number;
    postsCount: number;
    agentsCount: number;
    isFollowed: boolean;
  }
  
  interface Agent {
    id: string;
    name: string;
    description: string;
    avatar?: string;
    creator: {
      id: number;
      username: string;
      avatar: string;
    };
    followCount: number;
    isFollowed: boolean;
  }
  
  interface KnowledgeBase {
    id: string;
    name: string;
    description: string;
    creator: {
      id: number;
      username: string;
      avatar: string;
    };
    fileCount: number;
    followCount: number;
    isFollowed: boolean;
  }
  
  const router = useRouter()
  const route = useRoute()
  
  // 搜索状态
  const searchQuery = ref('')
  const searchType = ref('all')
  const currentPage = ref(1)
  const pageSize = ref(10)
  const loading = ref(false)
  
  // 搜索结果
  const results = reactive({
    posts: [] as Post[],
    users: [] as User[],
    agents: [] as Agent[],
    kb: [] as KnowledgeBase[]
  })
  
  // 结果计数
  const resultsCount = reactive({
    posts: 0,
    users: 0,
    agents: 0,
    kb: 0
  })
  
  // 计算属性：没有搜索结果
  const noResults = computed(() => {
    if (searchType.value === 'all') {
      return resultsCount.posts === 0 && 
             resultsCount.users === 0 && 
             resultsCount.agents === 0 && 
             resultsCount.kb === 0
    } else if (searchType.value === 'posts') {
      return resultsCount.posts === 0
    } else if (searchType.value === 'users') {
      return resultsCount.users === 0
    } else if (searchType.value === 'agents') {
      return resultsCount.agents === 0
    } else if (searchType.value === 'kb') {
      return resultsCount.kb === 0
    }
    return true
  })
  
  // 从URL参数初始化搜索条件
  onMounted(() => {
    const query = route.query.q as string
    const type = route.query.type as string
    
    if (query) {
      searchQuery.value = query
      if (type && ['all', 'posts', 'users', 'agents', 'kb'].includes(type)) {
        searchType.value = type
      }
      
      // 执行搜索
      executeSearch()
    }
  })
  
  // 监听路由变化
  watch(() => route.query, (newQuery) => {
    const query = newQuery.q as string
    const type = newQuery.type as string
    
    if (query && query !== searchQuery.value) {
      searchQuery.value = query
      if (type && ['all', 'posts', 'users', 'agents', 'kb'].includes(type)) {
        searchType.value = type
      }
      
      // 执行搜索
      executeSearch()
    }
  }, { deep: true })
  
  // 处理搜索类型变化
  const handleTypeChange = () => {
    // 重置分页
    currentPage.value = 1
    
    // 更新URL参数
    updateUrlParams()
    
    // 执行搜索
    executeSearch()
  }
  
  // 更新URL参数
  const updateUrlParams = () => {
    router.replace({
      query: {
        ...route.query,
        q: searchQuery.value,
        type: searchType.value
      }
    })
  }
  
  // 执行搜索
  const executeSearch = async () => {
    if (!searchQuery.value.trim()) {
      ElMessage.warning('请输入搜索内容')
      return
    }
    
    loading.value = true
    
    try {
      // 更新URL参数
      updateUrlParams()
      
      // 获取token
      const token = localStorage.getItem('token')
      
      // 构建查询参数
      const params = new URLSearchParams({
        q: searchQuery.value,
        type: searchType.value,
        page: currentPage.value.toString(),
        size: pageSize.value.toString()
      })
      
      // 发送搜索请求
      const response = await fetch(`/community/search?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
      })
      
      if (!response.ok) {
        throw new Error('搜索失败')
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        // 处理搜索结果
        if (searchType.value === 'all') {
          // 全部搜索结果
          results.posts = result.data.posts.items || []
          results.users = result.data.users.items || []
          results.agents = result.data.agents.items || []
          results.kb = result.data.kb.items || []
          
          // 更新计数
          resultsCount.posts = result.data.posts.total || 0
          resultsCount.users = result.data.users.total || 0
          resultsCount.agents = result.data.agents.total || 0
          resultsCount.kb = result.data.kb.total || 0
        } else {
          // 特定类型搜索
          const key = searchType.value
          results[key] = result.data.items || []
          resultsCount[key] = result.data.total || 0
          
          // 清空其他类型的结果
          Object.keys(results).forEach(k => {
            if (k !== key) {
              results[k] = []
              resultsCount[k] = 0
            }
          })
        }
      } else {
        throw new Error(result.message || '搜索失败')
      }
    } catch (error) {
      console.error('搜索失败:', error)
      ElMessage.error('搜索失败，请稍后重试')
      
      // 开发模式下使用模拟数据
      const mockData = getMockSearchResults()
      if (searchType.value === 'all') {
        results.posts = mockData.posts
        results.users = mockData.users
        results.agents = mockData.agents
        results.kb = mockData.kb
        
        resultsCount.posts = mockData.posts.length
        resultsCount.users = mockData.users.length
        resultsCount.agents = mockData.agents.length
        resultsCount.kb = mockData.kb.length
      } else {
        const key = searchType.value
        results[key] = mockData[key]
        resultsCount[key] = mockData[key].length
        
        Object.keys(results).forEach(k => {
          if (k !== key) {
            results[k] = []
            resultsCount[k] = 0
          }
        })
      }
    } finally {
      loading.value = false
    }
  }
  
  // 分页处理
  const handleSizeChange = (val: number) => {
    pageSize.value = val
    currentPage.value = 1
    executeSearch()
  }
  
  const handleCurrentChange = (val: number) => {
    currentPage.value = val
    executeSearch()
  }
  
  // 关键词高亮处理
  const highlightKeyword = (text: string): string => {
    if (!text || !searchQuery.value.trim()) return text
    
    const keyword = searchQuery.value.trim()
    const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const regex = new RegExp(escapedKeyword, 'gi')
    return text.replace(regex, match => `<span class="highlight">${match}</span>`)
  }
  
  // 用户交互功能
  const viewUserProfile = (userId: number) => {
    router.push(`/user-profile/${userId}`)
  }
  
  const viewPostDetail = (postId: number) => {
    router.push(`/post/${postId}`)
  }
  
  const viewAgentDetail = (agentId: string) => {
    router.push(`/agent-detail/${agentId}`)
  }
  
  const viewKnowledgeBaseDetail = (kbId: string) => {
    router.push(`/knowledge-base/${kbId}`)
  }
  
  // 关注用户
  const followUser = async (user: User) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        return
      }

      if (String(user.id) === localStorage.getItem('userId')) {
        ElMessage.warning('不能关注自己')
        return
      }
      
      const isFollowed = user.isFollowed
      
      // 乐观更新UI
      user.isFollowed = !isFollowed
      if (isFollowed) {
        user.followersCount--
      } else {
        user.followersCount++
      }
      
      // 关注/取消关注请求
      const response = await fetch(`/user/follow/${user.id}/`, {
        method: isFollowed ? 'DELETE' : 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        // 请求失败时回滚UI状态
        user.isFollowed = isFollowed
        if (isFollowed) {
          user.followersCount++
        } else {
          user.followersCount--
        }
        throw new Error(isFollowed ? '取消关注失败' : '关注失败')
      }
      
      const result = await response.json()
      if (response.status === 200) {
        ElMessage.success(isFollowed ? '已取消关注' : '关注成功')
      } else {
        // 请求返回错误时回滚UI状态
        user.isFollowed = isFollowed
        if (isFollowed) {
          user.followersCount++
        } else {
          user.followersCount--
        }
        throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
      }
    } catch (error) {
      console.error('关注用户操作失败:', error)
      ElMessage.error('操作失败，请稍后重试')
    }
  }
  
  // 关注智能体
  const followAgent = async (agent: Agent) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        return
      }
      
      const isFollowed = agent.isFollowed
      
      // 乐观更新UI
      agent.isFollowed = !isFollowed
      if (isFollowed) {
        agent.followCount--
      } else {
        agent.followCount++
      }
      
      // 关注/取消关注请求
      const response = await fetch(`/user/follow/agent/${agent.id}/`, {
        method: isFollowed ? 'DELETE' : 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        // 请求失败时回滚UI状态
        agent.isFollowed = isFollowed
        if (isFollowed) {
          agent.followCount++
        } else {
          agent.followCount--
        }
        throw new Error(isFollowed ? '取消关注失败' : '关注失败')
      }
      
      const result = await response.json()
      if (result.code === 200) {
        ElMessage.success(isFollowed ? '已取消关注智能体' : '关注智能体成功')
      } else {
        // 请求返回错误时回滚UI状态
        agent.isFollowed = isFollowed
        if (isFollowed) {
          agent.followCount++
        } else {
          agent.followCount--
        }
        throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
      }
    } catch (error) {
      console.error('关注智能体操作失败:', error)
      ElMessage.error('操作失败，请稍后重试')
    }
  }
  
  // 关注知识库
  const followKnowledgeBase = async (kb: KnowledgeBase) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        return
      }
      
      const isFollowed = kb.isFollowed
      
      // 乐观更新UI
      kb.isFollowed = !isFollowed
      if (isFollowed) {
        kb.followCount--
      } else {
        kb.followCount++
      }
      
      // 关注/取消关注请求
      const response = await fetch(`/user/follow/knowledge-base/${kb.id}/`, {
        method: isFollowed ? 'DELETE' : 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        // 请求失败时回滚UI状态
        kb.isFollowed = isFollowed
        if (isFollowed) {
          kb.followCount++
        } else {
          kb.followCount--
        }
        throw new Error(isFollowed ? '取消关注失败' : '关注失败')
      }
      
      const result = await response.json()
      if (result.code === 200) {
        ElMessage.success(isFollowed ? '已取消关注知识库' : '关注知识库成功')
      } else {
        // 请求返回错误时回滚UI状态
        kb.isFollowed = isFollowed
        if (isFollowed) {
          kb.followCount++
        } else {
          kb.followCount--
        }
        throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
      }
    } catch (error) {
      console.error('关注知识库操作失败:', error)
      ElMessage.error('操作失败，请稍后重试')
    }
  }
  
  // 获取模拟搜索结果（开发阶段使用）
  const getMockSearchResults = () => {
    const keyword = searchQuery.value
    
    return {
      posts: [
        {
          id: 1,
          userId: 101,
          username: '用户A',
          avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
          time: '2025-04-27 10:00',
          title: `关于${keyword}的讨论`,
          content: `这是一个与${keyword}相关的帖子内容，讨论了很多有趣的话题...`,
          likes: 128,
          comments: [],
          isLiked: false
        }
      ],
      users: [
        {
          id: 101,
          username: `${keyword}用户`,
          avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
          bio: `我是一个对${keyword}很感兴趣的用户`,
          followersCount: 156,
          followingCount: 89,
          postsCount: 45,
          agentsCount: 12,
          isFollowed: false
        }
      ],
      agents: [
        {
          id: 'agent1',
          name: `${keyword}助手`,
          description: `这是一个专门处理${keyword}相关问题的智能体`,
          creator: { 
            id: 101, 
            username: '用户A', 
            avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png' 
          },
          followCount: 245,
          isFollowed: false
        }
      ],
      kb: [
        {
          id: 'kb1',
          name: `${keyword}资料库`,
          description: `这是一个关于${keyword}的知识库`,
          creator: { 
            id: 101, 
            username: '用户A', 
            avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png' 
          },
          fileCount: 24,
          followCount: 168,
          isFollowed: false
        }
      ]
    }
  }
  </script>
  
  <style scoped>
  .search-container {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .search-header {
    margin-bottom: 20px;
  }
  
  .search-bar {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 15px;
  }
  
  .back-button {
    display: flex;
    align-items: center;
    gap: 5px;
    cursor: pointer;
    padding: 5px;
    border-radius: 4px;
    color: #606266;
  }
  
  .back-button:hover {
    color: #409EFF;
    background-color: #f0f9ff;
  }
  
  .main-search {
    flex: 1;
  }
  
  .search-input {
    width: 100%;
  }
  
  .search-types {
    margin-top: 15px;
  }
  
  .search-results {
    margin-top: 20px;
  }
  
  .result-section {
    margin-bottom: 40px;
  }
  
  .result-title {
    font-size: 20px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #ebeef5;
  }
  
  /* 帖子卡片样式 */
  .post-card {
    margin-bottom: 20px;
  }
  
  .post-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .post-title {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .post-content h3 {
    margin-top: 0;
  }
  
  .post-images {
    display: flex;
    gap: 10px;
    margin: 10px 0;
    flex-wrap: wrap;
  }
  
  .post-image {
    width: 100px;
    height: 100px;
    border-radius: 4px;
    object-fit: cover;
  }
  
  .post-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;
    padding-top: 10px;
    border-top: 1px solid #f0f0f0;
  }
  
  .post-actions {
    display: flex;
    gap: 15px;
  }
  
  /* 用户卡片样式 */
  .user-card, .agent-card, .kb-card {
    height: 220px;
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    cursor: pointer;
    transition: transform 0.2s;
  }
  
  .user-card:hover, .agent-card:hover, .kb-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
  
  .user-info, .agent-info, .kb-info {
    display: flex;
    gap: 15px;
    margin-bottom: 15px;
  }
  
  .user-details, .agent-details, .kb-details {
    flex: 1;
  }
  
  .user-details h3, .agent-details h3, .kb-details h3 {
    margin: 0 0 5px 0;
    font-size: 16px;
  }
  
  .user-details p, .agent-details p, .kb-details p {
    margin: 0;
    font-size: 12px;
    color: #606266;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .no-bio {
    color: #909399;
    font-style: italic;
  }
  
  .user-stats, .agent-stats, .kb-stats {
    display: flex;
    justify-content: space-around;
    margin-top: auto;
    margin-bottom: 15px;
    padding: 10px 0;
    border-top: 1px solid #f0f0f0;
    border-bottom: 1px solid #f0f0f0;
    font-size: 13px;
    color: #606266;
  }
  
  .agent-avatar, .default-avatar {
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #ecf5ff;
    color: #409eff;
    border-radius: 50%;
    font-weight: bold;
    font-size: 18px;
  }
  
  .kb-icon {
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f0f9eb;
    color: #67c23a;
    border-radius: 50%;
    font-weight: bold;
    font-size: 18px;
  }
  
  .agent-creator, .kb-creator {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }
  
  .username {
    font-weight: bold;
    color: #333;
    cursor: pointer;
  }
  
  .username:hover {
    color: #409eff;
    text-decoration: underline;
  }
  
  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
  
  /* 加载状态 */
  .loading-container {
    padding: 20px;
  }
  
  /* 关键词高亮 */
  :deep(.highlight) {
    background-color: #ffeaa7;
    padding: 0 2px;
    border-radius: 2px;
    font-weight: bold;
  }
  </style>