<template>
  <div class="my-posts-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-button 
            @click="router.push('/community')" 
            type="primary" 
            plain
            size="medium"
            icon="ArrowLeft"
          >
            返回社区
          </el-button>
          <h2>我的帖子</h2>
        </div>
        <el-button type="primary" @click="showCreatePostDialog">
          <el-icon class="el-icon--left"><Plus /></el-icon>发布新帖子
        </el-button>
      </el-header>

      <el-main>
        <!-- 帖子列表 -->
        <div v-if="posts.length > 0" class="post-list">
          <el-card v-for="post in posts" :key="post.id" class="post-card" shadow="hover">
            <div class="post-content">
              <!-- 帖子标题和管理操作 -->
              <div class="post-header">
                <h3 class="post-title" @click="viewPostDetails(post)">{{ post.title }}</h3>
                <div class="post-actions">
                  <el-button type="primary" size="small" @click="editPost(post)">
                    <el-icon class="el-icon--left"><Edit /></el-icon>编辑
                  </el-button>
                  <el-button type="danger" size="small" @click="deletePost(post)">
                    <el-icon class="el-icon--left"><Delete /></el-icon>删除
                  </el-button>
                </div>
              </div>
              
              <!-- 帖子内容 -->
              <p class="post-excerpt">{{ post.content }}</p>
              
              <!-- 帖子图片 -->
              <div v-if="post.images && post.images.length" class="post-images">
                <el-image 
                  v-for="(img, index) in post.images.slice(0, 3)" 
                  :key="index"
                  :src="img"
                  fit="cover"
                  class="post-image"
                />
                <div v-if="post.images.length > 3" class="more-images">
                  +{{ post.images.length - 3 }}
                </div>
              </div>
              
              <!-- 发布信息和统计 -->
              <div class="post-meta">
                <div class="post-date">
                  <el-icon><Timer /></el-icon>
                  <span>{{ post.time }}</span>
                </div>
                <div class="post-stats">
                  <span>
                    <el-icon><View /></el-icon>
                    {{ post.views || 0 }}
                  </span>
                  <span>
                    <el-icon><Star /></el-icon>
                    {{ post.likes || 0 }}
                  </span>
                  <span>
                    <el-icon><ChatDotRound /></el-icon>
                    {{ post.comments?.length || 0 }}
                  </span>
                </div>
              </div>
              
              <!-- 帖子状态 -->
              <div class="post-status">
                <el-tag :type="getStatusType(post.status)">{{ getStatusText(post.status) }}</el-tag>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 空状态展示 -->
        <el-empty 
          v-else 
          description="暂无帖子" 
          :image-size="200"
        >
          <el-button type="primary" @click="showCreatePostDialog">
            <el-icon class="el-icon--left"><Plus /></el-icon>发布第一篇帖子
          </el-button>
        </el-empty>

        <!-- 分页 -->
        <div class="pagination" v-if="posts.length > 0">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 30, 50]"
            layout="total, sizes, prev, pager, next"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            background
          />
        </div>
      </el-main>
    </el-container>
    
    <!-- 发布帖子对话框 -->
    <el-dialog
      v-model="postDialogVisible"
      :title="isEditing ? '编辑帖子' : '发布帖子'"
      width="60%"
      :close-on-click-modal="false"
    >
      <el-form :model="postForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input 
            v-model="postForm.title" 
            placeholder="请输入标题" 
            maxlength="100" 
            show-word-limit 
          />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input
            v-model="postForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入内容"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        
        <!-- 附加智能体 -->
        <el-form-item label="智能体">
          <div class="resource-selector">
            <el-select
              v-model="postForm.selectedAgents"
              multiple
              filterable
              clearable
              placeholder="选择要分享的智能体"
              style="width: 100%"
            >
              <el-option
                v-for="agent in userAgents"
                :key="agent.id"
                :label="agent.name"
                :value="agent.id"
              >
                <div class="resource-option">
                  <div class="resource-icon">AI</div>
                  <div class="resource-info">
                    <div class="resource-name">{{ agent.name }}</div>
                    <div class="resource-desc">{{ agent.description }}</div>
                  </div>
                </div>
              </el-option>
            </el-select>
            <el-button type="primary" plain size="small" @click="fetchUserAgents">
              <el-icon><RefreshRight /></el-icon>刷新
            </el-button>
          </div>
        </el-form-item>
        
        <!-- 附加知识库 -->
        <el-form-item label="知识库">
          <div class="resource-selector">
            <el-select
              v-model="postForm.selectedKnowledgeBases"
              multiple
              filterable
              clearable
              placeholder="选择要分享的知识库"
              style="width: 100%"
            >
              <el-option
                v-for="kb in userKnowledgeBases"
                :key="kb.id"
                :label="kb.name"
                :value="kb.id"
              >
                <div class="resource-option">
                  <div class="resource-icon">KB</div>
                  <div class="resource-info">
                    <div class="resource-name">{{ kb.name }}</div>
                    <div class="resource-desc">{{ kb.description }}</div>
                  </div>
                </div>
              </el-option>
            </el-select>
            <el-button type="primary" plain size="small" @click="fetchUserKnowledgeBases">
              <el-icon><RefreshRight /></el-icon>刷新
            </el-button>
          </div>
        </el-form-item>
        
        <!-- 图片上传 -->
        <el-form-item label="图片">
          <el-upload
            action="#"
            list-type="picture-card"
            :auto-upload="false"
            :on-change="handleImageChange"
            :on-remove="handleImageRemove"
            :file-list="postForm.fileList"
            :limit="9"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">最多上传9张图片，每张不超过5MB</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelPostSubmit">取消</el-button>
          <el-button type="primary" :loading="posting" @click="handlePostSubmit">{{ isEditing ? '保存' : '发布' }}</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowLeft, 
  Edit, 
  Delete, 
  View, 
  Star, 
  ChatDotRound, 
  Plus, 
  RefreshRight, 
  Timer 
} from '@element-plus/icons-vue'

const router = useRouter()
const posts = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const postDialogVisible = ref(false)
const isEditing = ref(false)
const currentEditId = ref(null)
const posting = ref(false)

// 帖子表单
const postForm = reactive({
  title: '',
  content: '',
  images: [],
  fileList: [],
  selectedAgents: [],
  selectedKnowledgeBases: []
})

// 用户的智能体和知识库列表
const userAgents = ref([])
const userKnowledgeBases = ref([])

// 获取用户的帖子列表
const fetchPosts = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }

    const userId = localStorage.getItem('userId')
    
    // 发送请求
    const response = await fetch(`/user/${userId}/posts/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error('获取帖子列表失败')
    }
    
    const result = await response.json()
    console.log('获取帖子列表成功:', result)
    
    if (result.code === 200) {
      posts.value = result.data.items || []
      total.value = result.data.total || 0
    } else {
      throw new Error(result.message || '获取帖子列表失败')
    }
  } catch (error) {
    console.error('获取帖子列表失败:', error)
    ElMessage.error('获取帖子列表失败，请稍后重试')
    
    // 模拟数据（开发阶段使用）
    posts.value = [
      {
        id: 1,
        title: '如何有效利用灵犀AI提升工作效率',
        content: '在日常工作中，我们可以通过以下几种方式利用灵犀AI提升工作效率：首先，可以使用智能助手功能自动处理重复性任务；其次，通过知识库整合和共享团队知识；最后，利用数据分析功能辅助决策...',
        images: ['https://picsum.photos/300/200'],
        time: '2025-05-01 14:30',
        views: 245,
        likes: 42,
        comments: [
          { id: 1, username: '用户A', content: '非常实用的建议！' }
        ],
        status: 'approved'
      },
      {
        id: 2,
        title: '分享我制作的英语学习助手',
        content: '最近我使用灵犀AI平台开发了一个英语学习助手，它可以帮助用户练习口语、纠正发音、推荐适合的学习材料，并且能够根据用户的学习进度提供个性化的学习计划...',
        images: [
          'https://picsum.photos/300/200',
          'https://picsum.photos/301/200',
          'https://picsum.photos/302/200',
          'https://picsum.photos/303/200'
        ],
        time: '2025-05-03 09:15',
        views: 387,
        likes: 78,
        comments: [
          { id: 2, username: '用户B', content: '这个助手太棒了！' },
          { id: 3, username: '用户C', content: '请问如何获取这个助手？' }
        ],
        status: 'approved'
      },
      {
        id: 3,
        title: '关于人工智能伦理的思考',
        content: '随着人工智能技术的快速发展，我们需要更加重视AI伦理问题。本文将从数据隐私、算法偏见、决策透明度等几个方面探讨人工智能伦理...',
        images: [],
        time: '2025-05-04 20:45',
        views: 156,
        likes: 25,
        comments: [],
        status: 'pending'
      }
    ]
    total.value = posts.value.length
  }
}

// 获取用户的智能体列表
const fetchUserAgents = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }

    // 发送请求
    const response = await fetch('/user/agents/list', {
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
    if (result.code === 200) {
      userAgents.value = result.data || []
    } else {
      throw new Error(result.message || '获取智能体列表失败')
    }
  } catch (error) {
    console.error('获取智能体列表失败:', error)
    ElMessage.error('获取智能体列表失败，请稍后重试')
    
    // 模拟数据
    userAgents.value = [
      {
        id: 'agent1',
        name: '英语学习助手',
        description: '帮助学习英语的智能体'
      },
      {
        id: 'agent2',
        name: '编程教练',
        description: '辅助编程学习和解决问题'
      }
    ]
  }
}

// 获取用户的知识库列表
const fetchUserKnowledgeBases = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }

    // 发送请求
    const response = await fetch('/user/knowledge-bases/list/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error('获取知识库列表失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      userKnowledgeBases.value = result.data || []
    } else {
      throw new Error(result.message || '获取知识库列表失败')
    }
  } catch (error) {
    console.error('获取知识库列表失败:', error)
    ElMessage.error('获取知识库列表失败，请稍后重试')
    
    // 模拟数据
    userKnowledgeBases.value = [
      {
        id: 'kb1',
        name: '机器学习笔记',
        description: '机器学习相关的学习笔记和资料'
      },
      {
        id: 'kb2',
        name: '产品文档',
        description: '产品相关的文档和说明'
      }
    ]
  }
}

// 帖子状态类型和文本
const getStatusType = (status) => {
  const statusMap = {
    'approved': 'success',
    'pending': 'warning',
    'rejected': 'danger',
    'draft': 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'approved': '已发布',
    'pending': '审核中',
    'rejected': '已拒绝',
    'draft': '草稿'
  }
  return statusMap[status] || '未知状态'
}

// 打开创建帖子对话框
const showCreatePostDialog = () => {
  isEditing.value = false
  currentEditId.value = null
  
  // 重置表单
  postForm.title = ''
  postForm.content = ''
  postForm.images = []
  postForm.fileList = []
  postForm.selectedAgents = []
  postForm.selectedKnowledgeBases = []
  
  // 获取用户的智能体和知识库
  fetchUserAgents()
  fetchUserKnowledgeBases()
  
  // 显示对话框
  postDialogVisible.value = true
}

// 编辑帖子
const editPost = (post) => {
  isEditing.value = true
  currentEditId.value = post.id
  
  // 填充表单数据
  postForm.title = post.title
  postForm.content = post.content
  
  // 处理图片
  postForm.images = []
  postForm.fileList = (post.images || []).map((url, index) => {
    return {
      name: `image-${index + 1}.jpg`,
      url: url
    }
  })
  
  // 填充智能体和知识库选择
  postForm.selectedAgents = (post.agents || []).map(agent => agent.id)
  postForm.selectedKnowledgeBases = (post.knowledgeBases || []).map(kb => kb.id)
  
  // 获取资源列表
  fetchUserAgents()
  fetchUserKnowledgeBases()
  
  // 显示对话框
  postDialogVisible.value = true
}

// 取消发帖
const cancelPostSubmit = () => {
  // 确认是否取消
  if (postForm.title || postForm.content || postForm.images.length || 
      postForm.selectedAgents.length || postForm.selectedKnowledgeBases.length) {
    ElMessageBox.confirm('确定要取消吗？已编辑的内容将不会保存。', '取消', {
      confirmButtonText: '确定',
      cancelButtonText: '继续编辑',
      type: 'warning'
    }).then(() => {
      postDialogVisible.value = false
    }).catch(() => {})
  } else {
    postDialogVisible.value = false
  }
}

// 图片移除
const handleImageRemove = (file) => {
  const index = postForm.images.findIndex(item => item === file.raw)
  if (index !== -1) {
    postForm.images.splice(index, 1)
  }
  
  // 更新文件列表
  const fileIndex = postForm.fileList.findIndex(item => item.uid === file.uid)
  if (fileIndex !== -1) {
    postForm.fileList.splice(fileIndex, 1)
  }
}

// 图片上传
const handleImageChange = (file, fileList) => {
  // 检查文件大小
  if (file.size / 1024 / 1024 > 5) {
    ElMessage.warning('图片大小不能超过5MB')
    return false
  }
  
  // 添加到已选图片列表
  if (!postForm.images.includes(file.raw)) {
    postForm.images.push(file.raw)
  }
  
  // 更新文件列表
  postForm.fileList = fileList
  
  return true
}

// 提交帖子
const handlePostSubmit = async () => {
  // 表单验证
  if (!postForm.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  if (!postForm.content.trim()) {
    ElMessage.warning('请输入内容')
    return
  }
  
  posting.value = true
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      posting.value = false
      return
    }
    
    // 先上传图片（如果有新图片）
    let uploadedImages = []
    
    // 如果是编辑模式，保留原有图片 URL
    if (isEditing.value) {
      uploadedImages = postForm.fileList
        .filter(file => file.url && !file.raw)
        .map(file => file.url)
    }
    
    // 上传新图片
    const newImages = postForm.images.filter(img => img instanceof File)
    if (newImages.length > 0) {
      const formData = new FormData()
      newImages.forEach(img => {
        formData.append('files', img)
      })
      
      // 图片上传请求
      const uploadResponse = await fetch('/user/post/upload-images/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })
      
      if (!uploadResponse.ok) {
        throw new Error('图片上传失败')
      }
      
      const uploadResult = await uploadResponse.json()
      if (uploadResult.code === 200) {
        uploadedImages = [...uploadedImages, ...(uploadResult.data || [])]
      } else {
        throw new Error(uploadResult.message || '图片上传失败')
      }
    }
    
    // 构建帖子数据
    const postData = {
      title: postForm.title,
      content: postForm.content,
      images: uploadedImages,
      agents: postForm.selectedAgents,
      knowledgeBases: postForm.selectedKnowledgeBases
    }
    
    // 根据是否编辑模式决定请求方法和URL
    const url = isEditing.value 
      ? `/user/post/update/${currentEditId.value}/` 
      : '/user/post/create/'
    
    const method = isEditing.value ? 'PUT' : 'POST'
    
    // 发送请求
    const response = await fetch(url, {
      method: method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(postData)
    })
    
    if (!response.ok) {
      throw new Error(isEditing.value ? '更新帖子失败' : '发布帖子失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      ElMessage.success(isEditing.value ? '更新成功' : '发布成功')
      postDialogVisible.value = false
      
      // 刷新帖子列表
      fetchPosts()
    } else {
      throw new Error(result.message || (isEditing.value ? '更新帖子失败' : '发布帖子失败'))
    }
  } catch (error) {
    console.error(isEditing.value ? '更新帖子失败:' : '发布帖子失败:', error)
    ElMessage.error((isEditing.value ? '更新' : '发布') + '帖子失败，请稍后重试')
  } finally {
    posting.value = false
  }
}

// 删除帖子
const deletePost = (post) => {
  ElMessageBox.confirm(
    `确定要删除帖子 "${post.title}" 吗？此操作不可恢复。`,
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

      // 调用后端API删除帖子
      const response = await fetch(`/user/post/${post.id}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error('删除帖子失败')
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        ElMessage.success('帖子删除成功')
        // 重新加载帖子列表
        fetchPosts()
      } else {
        throw new Error(result.message || '删除帖子失败')
      }
    } catch (error) {
      console.error('删除帖子失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }).catch(() => {})
}

// 查看帖子详情
const viewPostDetails = (post) => {
  router.push(`/post/${post.id}`)
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchPosts()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchPosts()
}

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
.my-posts-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 20px;
}

.post-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.post-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
}

.post-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-title {
  margin: 0;
  font-size: 18px;
  color: #303133;
  cursor: pointer;
}

.post-title:hover {
  color: #409EFF;
}

.post-excerpt {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-images {
  display: flex;
  gap: 8px;
  overflow: hidden;
}

.post-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 4px;
}

.more-images {
  width: 100px;
  height: 100px;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  border-radius: 4px;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #909399;
  font-size: 13px;
}

.post-date {
  display: flex;
  align-items: center;
  gap: 4px;
}

.post-stats {
  display: flex;
  gap: 15px;
}

.post-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.post-status {
  display: flex;
  justify-content: flex-end;
}

.post-actions {
  display: flex;
  gap: 8px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

.resource-selector {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.resource-option {
  display: flex;
  gap: 10px;
  padding: 5px 0;
}

.resource-icon {
  width: 36px;
  height: 36px;
  background-color: #ecf5ff;
  color: #409eff;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.resource-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.resource-name {
  font-weight: 500;
  font-size: 14px;
}

.resource-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}
</style>