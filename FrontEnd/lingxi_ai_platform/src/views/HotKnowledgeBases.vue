<template>
    <div class="hot-kb-container">
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>
      
      <!-- 空状态 -->
      <el-empty v-else-if="knowledgeBases.length === 0" description="暂无热门知识库" />
      
      <!-- 知识库列表 -->
      <div v-else class="kb-list">
        <div 
          v-for="kb in knowledgeBases" 
          :key="kb.id" 
          class="kb-item"
          @click="viewKnowledgeBaseDetail(kb.id)"
        >
          <div class="kb-icon">KB</div>
          <div class="kb-info">
            <div class="kb-name">{{ kb.name }}</div>
            <div class="kb-description">{{ kb.description }}</div>
            <div class="kb-stats">
              <span class="stat-item">
                <el-icon><Document /></el-icon> {{ kb.fileCount || 0 }} 文件
              </span>
              <span class="stat-item">
                <el-icon><View /></el-icon> {{ kb.views || 0 }} 浏览
              </span>
              <span class="stat-item">
                <el-icon><Star /></el-icon> {{ kb.followerCount || 0 }} 人关注
              </span>
              <span class="stat-item kb-creator" @click.stop="viewUserProfile(kb.creator?.id)">
                <el-icon><User /></el-icon> {{ kb.creator ? kb.creator.username : '未知' }}
              </span>
            </div>
          </div>
          <el-button 
            :type="kb.isFollowed ? 'success' : 'primary'" 
            size="small"
            @click.stop="followKnowledgeBase(kb)"
          >
            {{ kb.isFollowed ? '已关注' : '关注' }}
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
  import { Document, View, Star, User } from '@element-plus/icons-vue'
  
  const router = useRouter()
  const loading = ref(true)
  const knowledgeBases = ref([])
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)
  
  // 获取热门知识库
  const fetchHotKnowledgeBases = async () => {
    loading.value = true
    try {
      const token = localStorage.getItem('token')
      const params = new URLSearchParams({
        page: currentPage.value.toString(),
        size: pageSize.value.toString()
      })
      
      const response = await fetch(`/community/knowledge-bases/hot/?${params.toString()}`, {
        method: 'GET',
        headers: token ? {
          'Authorization': `Bearer ${token}`,
        } : {}
      })
      
      if (!response.ok) {
        throw new Error('获取热门知识库失败')
      }
      
      const result = await response.json()
      if (result.code === 200) {
        knowledgeBases.value = result.data.items || []
        total.value = result.data.total || 0
      } else {
        throw new Error(result.message || '获取热门知识库失败')
      }
    } catch (error) {
      console.error('获取热门知识库失败:', error)
      ElMessage.error('获取热门知识库失败，请稍后重试')
    } finally {
      loading.value = false
    }
  }
  
  // 查看知识库详情
  const viewKnowledgeBaseDetail = (kbId) => {
    router.push(`/knowledge-base/${kbId}`)
  }
  
  // 查看用户资料
  const viewUserProfile = (userId) => {
    if (userId) {
      router.push(`/user-profile/${userId}`)
    }
  }
  
  // 关注/取消关注知识库
  const followKnowledgeBase = async (kb) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        return
      }
      
      const isFollowed = kb.isFollowed
      
      // 关注/取消关注请求
      const response = await fetch(`/user/follow/knowledge-base/${kb.id}/`, {
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
        kb.followerCount = isFollowed ? 
          (kb.followerCount - 1) : 
          (kb.followerCount + 1)
        
        ElMessage.success(isFollowed ? '已取消关注知识库' : '关注知识库成功')
      } else {
        throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
      }
    } catch (error) {
      console.error('关注知识库操作失败:', error)
      ElMessage.error('操作失败，请稍后重试')
    }
  }
  
  // 分页处理
  const handleSizeChange = (val) => {
    pageSize.value = val
    currentPage.value = 1
    fetchHotKnowledgeBases()
  }
  
  const handleCurrentChange = (val) => {
    currentPage.value = val
    fetchHotKnowledgeBases()
  }
  
  // 初始加载
  onMounted(() => {
    fetchHotKnowledgeBases()
  })
  </script>
  
  <style scoped>
  .hot-kb-container {
    padding: 20px;
  }
  
  .section-title {
    margin-bottom: 20px;
    font-size: 18px;
    font-weight: 600;
  }
  
  .kb-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .kb-item {
    display: flex;
    align-items: center;
    padding: 15px;
    border: 1px solid #ebeef5;
    border-radius: 8px;
    background-color: #fff;
    transition: all 0.3s;
    cursor: pointer;
  }
  
  .kb-item:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .kb-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #67c23a;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    margin-right: 15px;
  }
  
  .kb-info {
    flex: 1;
    min-width: 0;
  }
  
  .kb-name {
    font-weight: 600;
    font-size: 16px;
    margin-bottom: 5px;
  }
  
  .kb-description {
    font-size: 14px;
    color: #606266;
    margin-bottom: 8px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .kb-stats {
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
  
  .kb-creator:hover {
    color: #409eff;
    text-decoration: underline;
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