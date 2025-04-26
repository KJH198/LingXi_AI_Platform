<template>
  <div class="community-container">
    <!-- 顶部导航栏 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2>灵犀AI社区</h2>
          <el-menu mode="horizontal" :default-active="activeMenu">
            <el-menu-item index="1">首页</el-menu-item>
            <el-menu-item index="2">热门</el-menu-item>
            <el-menu-item index="3">最新</el-menu-item>
            <el-menu-item index="3" @click="showAnnouncementList">公告</el-menu-item>
          </el-menu>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="showCreateAgentDialog">构建智能体</el-button>
          <el-button type="primary" @click="showPostDialog">发布帖子</el-button>
          <el-dropdown>
            <el-avatar :size="40" :src="userInfo.avatar" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
                <el-dropdown-item @click="router.push('/my-posts')">我的帖子</el-dropdown-item>
                <el-dropdown-item @click="router.push('/my-agents')">我的智能体</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主要内容区 -->
      <el-main>
        <!-- 帖子列表 -->
        <div class="post-list">
          <el-card v-for="post in posts" :key="post.id" class="post-card">
            <template #header>
              <div class="post-header">
                <div class="post-title">
                  <el-avatar :size="32" :src="post.avatar" />
                  <span class="username">{{ post.username }}</span>
                  <span class="time">{{ post.time }}</span>
                </div>
                <el-dropdown>
                  <el-button type="text">
                    <el-icon><More /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item>举报</el-dropdown-item>
                      <el-dropdown-item>收藏</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
            <div class="post-content">
              <h3>{{ post.title }}</h3>
              <p>{{ post.content }}</p>
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
                <el-button type="text">
                  <el-icon><Star /></el-icon>
                  {{ post.likes }}
                </el-button>
                <el-button type="text">
                  <el-icon><ChatDotRound /></el-icon>
                  {{ post.comments.length }}
                </el-button>
                <el-button type="text">
                  <el-icon><Share /></el-icon>
                  分享
                </el-button>
              </div>
              <el-button type="primary" size="small" @click="showCommentDialog(post)">评论</el-button>
            </div>
          </el-card>
        </div>

        <!-- 分页 -->
        <div class="pagination">
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
      </el-main>
    </el-container>

    <!-- 发帖对话框 -->
    <el-dialog
      v-model="postDialogVisible"
      title="发布帖子"
      width="50%"
    >
      <el-form :model="postForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="postForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="postForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入内容"
          />
        </el-form-item>
        <el-form-item label="图片">
          <el-upload
            action="#"
            list-type="picture-card"
            :auto-upload="false"
            :on-change="handleImageChange"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="postDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handlePostSubmit">发布</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 评论对话框 -->
    <el-dialog
      v-model="commentDialogVisible"
      title="评论"
      width="40%"
    >
      <div class="comment-list">
        <div v-for="comment in currentPost?.comments" :key="comment.id" class="comment-item">
          <el-avatar :size="32" :src="comment.avatar" />
          <div class="comment-content">
            <div class="comment-header">
              <span class="username">{{ comment.username }}</span>
              <span class="time">{{ comment.time }}</span>
            </div>
            <p>{{ comment.content }}</p>
          </div>
        </div>
      </div>
      <div class="comment-input">
        <el-input
          v-model="commentContent"
          type="textarea"
          :rows="2"
          placeholder="写下你的评论..."
        />
        <el-button type="primary" @click="handleCommentSubmit">发表评论</el-button>
      </div>
    </el-dialog>

    <!-- 公告列表弹窗 -->
    <el-dialog
      v-model="announcementListDialogVisible"
      title="公告列表"
      width="50%"
    >
      <el-table :data="announcements" style="width: 100%" border>
        <el-table-column prop="title" label="标题" width="200" />
        <el-table-column prop="content" label="内容预览">
          <template #default="scope">
            <span>{{ scope.row.content.slice(0, 50) }}...</span>
          </template>
        </el-table-column>
        <el-table-column label="是否已读" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.viewed ? 'success' : 'info'">
              {{ scope.row.viewed ? '已读' : '未读' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="primary" size="small" @click="showAnnouncement(scope.row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="announcementListDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 公告详情弹窗 -->
    <el-dialog
      v-model="announcementDialogVisible"
      title="公告详情"
      width="50%"
    >
      <div>
        <h3>{{ selectedAnnouncement.title }}</h3>
        <p>{{ selectedAnnouncement.content }}</p>
      </div>
      <template #footer>
        <el-button @click="announcementDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="createAgentDialogVisible"
      title="创建智能体"
      width="50%"
    >
      <el-form :model="agentInitData" label-width="100px">
        <el-form-item label="智能体名称" required>
          <el-input v-model="agentInitData.name" placeholder="请输入智能体名称"></el-input>
        </el-form-item>
        <el-form-item label="简介">
          <el-input
            v-model="agentInitData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入智能体简介"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createAgentDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCreateAgent">创建并进入编辑器</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Star, 
  ChatDotRound, 
  Share, 
  More, 
  Plus 
} from '@element-plus/icons-vue'

const router = useRouter()
const activeMenu = ref('1')
const postDialogVisible = ref(false)
const commentDialogVisible = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)
const commentContent = ref('')
const currentPost = ref<Post | null>(null)

// 用户信息
const userInfo = reactive({
  username: '',
  avatar: ''
})

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    // 首先尝试从本地存储获取用户信息
    const storedUserInfo = localStorage.getItem('userInfo')
    if (storedUserInfo) {
      const parsedUserInfo = JSON.parse(storedUserInfo)
      Object.assign(userInfo, parsedUserInfo)
      return
    }

    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }

    // 模拟API请求延迟
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 模拟返回的用户数据
    const mockUserData = {
      username: '未知',
      avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
    }

    // 更新用户信息
    Object.assign(userInfo, mockUserData)

    // 实际API请求代码（暂时注释）
    const response = await fetch('/user/user_info/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error('获取用户信息失败')
    }

    const data = await response.json();
    if (data.code !== 200) {
      throw new Error(data.message || '获取用户信息失败');
    }

    // 更新用户信息
    const newUserInfo = {
      username: data.username,
      avatar: data.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
    }
    Object.assign(userInfo, newUserInfo)
    
    // 更新本地存储
    localStorage.setItem('userInfo', JSON.stringify(newUserInfo))
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败，请稍后重试')
  }
}

// 组件挂载时获取用户信息
onMounted(() => {
  fetchUserInfo()
})

// 定义接口
interface Comment {
  id: number
  username: string
  avatar: string
  time: string
  content: string
}

interface Post {
  id: number
  username: string
  avatar: string
  time: string
  title: string
  content: string
  images?: string[]
  likes: number
  comments: Comment[]
}

// 模拟帖子数据
const posts = ref<Post[]>([
  {
    id: 1,
    username: '用户A',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    time: '2024-03-27 10:00',
    title: '分享一个有趣的AI应用',
    content: '最近发现了一个非常有趣的AI应用，可以帮助我们更好地学习和工作...',
    images: [
      'https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg',
      'https://fuss10.elemecdn.com/8/27/f01c15bb73e1ef3793e64e6b7bbccjpeg.jpeg'
    ],
    likes: 128,
    comments: [
      {
        id: 1,
        username: '用户B',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        time: '2024-03-27 10:30',
        content: '确实很有趣，感谢分享！'
      }
    ]
  }
])

// 公告数据
const announcements = ref([
  { id: 1, title: '系统维护通知', content: '系统将于本周六凌晨2:00-4:00进行维护升级。', viewed: false },
  { id: 2, title: '新功能上线', content: '我们上线了新的智能体编辑功能，快来体验吧！', viewed: false },
])

const announcementListDialogVisible = ref(false)
const announcementDialogVisible = ref(false)
const selectedAnnouncement = reactive({ title: '', content: '' })

const markAnnouncementAsViewed = (announcement) => {
  announcement.viewed = true;
};

const showAnnouncementList = () => {
  announcementListDialogVisible.value = true
}

const showAnnouncement = (announcement) => {
  selectedAnnouncement.title = announcement.title
  selectedAnnouncement.content = announcement.content
  announcementDialogVisible.value = true
  markAnnouncementAsViewed(announcement);
}

const checkNewAnnouncements = () => {
  const newAnnouncement = announcements.value.find((announcement) => !announcement.viewed);
  if (newAnnouncement) {
    ElMessage({
      message: '有新的公告，点击查看！',
      type: 'info',
      duration: 5000,
      onClose: () => {
        showAnnouncement(newAnnouncement);
      },
    });
  }
}

// 发帖表单
const postForm = reactive({
  title: '',
  content: '',
  images: [] as File[]
})

// 处理发帖
const showPostDialog = () => {
  postDialogVisible.value = true
}

const handlePostSubmit = () => {
  ElMessage.success('发布成功')
  postDialogVisible.value = false
}

// 处理评论
const showCommentDialog = (post: Post) => {
  currentPost.value = post
  commentDialogVisible.value = true
}

const handleCommentSubmit = () => {
  if (!commentContent.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  ElMessage.success('评论成功')
  commentContent.value = ''
}

// 处理图片上传
const handleImageChange = (file: { raw: File }) => {
  postForm.images.push(file.raw)
}

// 处理分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  // TODO: 重新加载数据
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  // TODO: 重新加载数据
}

// 退出登录
const handleLogout = () => {
  ElMessage.success('退出成功')
  router.push('/login')
}

const createAgentDialogVisible = ref(false)
const agentInitData = reactive({
  name: '',
  description: '',
  category: '',
  visibility: 'public'
})

// 分类数据
const categories = ref([
  { label: '教育学习', value: 'education' },
  { label: '工作效率', value: 'productivity' },
  { label: '编程开发', value: 'programming' },
  { label: '生活助手', value: 'lifestyle' },
  { label: '创意设计', value: 'creative' },
  { label: '健康医疗', value: 'health' },
  { label: '娱乐休闲', value: 'entertainment' },
  { label: '其他', value: 'other' }
])

// 显示创建智能体对话框
const showCreateAgentDialog = () => {
  createAgentDialogVisible.value = true
}

// 创建智能体
// 在 Community.vue 中修改 handleCreateAgent 函数
const handleCreateAgent = () => {
  if (!agentInitData.name.trim()) {
    ElMessage.warning('请输入智能体名称')
    return
  }
  
  // 检查是否存在之前的草稿数据
  const storedAgentData = localStorage.getItem('agentData')
  if (storedAgentData) {
    try {
      const parsedData = JSON.parse(storedAgentData)
      // 只有当草稿包含有效数据时才询问
      if (parsedData && (parsedData.name || parsedData.modelId || parsedData.knowledgeBases?.length > 0 || parsedData.workflowId)) {
        ElMessageBox.confirm(
          '检测到您有未完成的智能体草稿，是否继续编辑该草稿？',
          '发现草稿',
          {
            confirmButtonText: '继续编辑草稿',
            cancelButtonText: '创建新智能体',
            type: 'info',
            distinguishCancelAndClose: true,
          }
        ).then(() => {
          // 用户选择继续编辑草稿
          createAgentDialogVisible.value = false
          router.push('/agent-editor')
        }).catch((action) => {
          if (action === 'cancel') {
            // 用户选择创建新智能体，清除之前的草稿
            localStorage.removeItem('agentData')
            localStorage.removeItem('selectedKnowledgeBases')
            localStorage.removeItem('selectedWorkflowId')
            localStorage.removeItem('selectedWorkflowName')
            
            // 将基本信息存入本地缓存，仅保留名称和描述
            const simpleAgentData = {
              name: agentInitData.name,
              description: agentInitData.description
            }
            localStorage.setItem('agentInitData', JSON.stringify(simpleAgentData))
            
            // 关闭对话框并导航到智能体编辑页面
            createAgentDialogVisible.value = false
            router.push('/agent-editor')
          }
        })
        return
      }
    } catch (e) {
      console.error('解析存储的智能体数据失败:', e)
    }
  }
  
  // 如果没有草稿或草稿无效，直接创建新智能体
  // 将基本信息存入本地缓存
  const simpleAgentData = {
    name: agentInitData.name,
    description: agentInitData.description
  }
  localStorage.setItem('agentInitData', JSON.stringify(simpleAgentData))
  
  // 关闭对话框并导航到智能体编辑页面
  createAgentDialogVisible.value = false
  router.push('/agent-editor')
}

</script>

<style scoped>
.community-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.post-list {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 0;
}

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

.username {
  font-weight: bold;
  color: #333;
}

.time {
  color: #999;
  font-size: 12px;
}

.post-content {
  margin: 15px 0;
}

.post-content h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.post-content p {
  color: #666;
  line-height: 1.6;
  margin: 0 0 15px 0;
}

.post-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  margin-top: 15px;
}

.post-image {
  width: 100%;
  height: 150px;
  border-radius: 4px;
  object-fit: cover;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
}

.post-actions {
  display: flex;
  gap: 15px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.comment-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.comment-item {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.comment-content {
  flex: 1;
}

.comment-header {
  margin-bottom: 5px;
}

.comment-input {
  display: flex;
  gap: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>