<template>
  <div class="community-container">
    <!-- 顶部导航栏 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2>灵犀AI社区</h2>
          <el-menu mode="horizontal" :default-active="activeMenu" @select="handleMenuSelect">
            <el-menu-item index="1">首页</el-menu-item>
            <el-menu-item index="2">热门智能体</el-menu-item>
            <el-menu-item index="3">热门知识库</el-menu-item>
            <el-menu-item index="4" @click="showAnnouncementList">公告</el-menu-item>
          </el-menu>
        </div>
        <div class="header-right">
          <div class="search-container">
            <el-input 
              v-model="searchQuery"
              placeholder="搜索帖子、用户、智能体..."
              @keyup.enter="handleSearch"
              clearable
            >
              <template #prefix>
          <el-icon><Search /></el-icon>
              </template>
              <template #append>
          <el-button @click="handleSearch">搜索</el-button>
              </template>
            </el-input>
          </div>
          <el-button type="primary" @click="showCreateAgentDialog">构建智能体</el-button>
          <el-button type="primary" @click="showPostDialog">发布帖子</el-button>
          <el-dropdown>
            <el-avatar :size="40" :src="userInfo.avatar" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
                <el-dropdown-item @click="router.push('/agent-drafts')">我的智能体草稿</el-dropdown-item>
                <el-dropdown-item @click="router.push('/my-agents')">我的智能体</el-dropdown-item>
                <el-dropdown-item @click="router.push('/my-knowledgebases')">我的知识库</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主要内容区 -->
      <el-main>
        <!-- 加载指示器 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="3" animated />
          <el-skeleton :rows="3" animated style="margin-top: 20px" />
        </div>
        
        <!-- 空状态提示 -->
        <el-empty v-else-if="posts.length === 0" description="暂无内容" />
        
        <!-- 帖子列表 -->
        <div v-else class="post-list">
          <el-card v-for="post in posts" :key="post.id" class="post-card">
            <template #header>
              <div class="post-header">
                <div class="post-title" @click="viewUserProfile(post.userId)">
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
                      <el-dropdown-item @click="followUser(post.userId)">
                        {{ post.isFollowed ? '取消关注' : '关注' }}
                      </el-dropdown-item>
                      <el-dropdown-item @click="favoritePost(post)">
                        {{ post.isFavorited ? '取消收藏' : '收藏' }}
                      </el-dropdown-item>
                      <el-dropdown-item @click="reportPost(post.id)">举报</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
            
            <div class="post-content">
              <h3>{{ post.title }}</h3>
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
              
              <!-- 智能体展示 -->
              <div class="post-resources" v-if="post.agents && post.agents.length">
                <div class="resource-header">
                  <el-icon><Connection /></el-icon>
                  <span>相关智能体</span>
                </div>
                <div class="resource-list">
                  <div 
                    v-for="agent in post.agents" 
                    :key="agent.id" 
                    class="resource-item"
                    @click="viewAgentDetail(agent.id)"
                  >
                    <div class="resource-item-icon">AI</div>
                    <div class="resource-item-content">
                      <div class="resource-item-name">{{ agent.name }}</div>
                      <div class="resource-item-creator">by {{ agent.creator.username }}</div>
                    </div>
                    <el-button 
                      size="small" 
                      :type="agent.isFollowed ? 'success' : 'primary'"
                      @click.stop="followAgent(agent)"
                    >
                      {{ agent.isFollowed ? '已关注' : '关注' }}
                    </el-button>
                  </div>
                </div>
              </div>
              
              <!-- 知识库展示 -->
              <div class="post-resources" v-if="post.knowledgeBases && post.knowledgeBases.length">
                <div class="resource-header">
                  <el-icon><Collection /></el-icon>
                  <span>相关知识库</span>
                </div>
                <div class="resource-list">
                  <div 
                    v-for="kb in post.knowledgeBases" 
                    :key="kb.id" 
                    class="resource-item"
                    @click="viewKnowledgeBaseDetail(kb.id)"
                  >
                    <div class="resource-item-icon">KB</div>
                    <div class="resource-item-content">
                      <div class="resource-item-name">{{ kb.name }}</div>
                      <div class="resource-item-creator">by {{ kb.creator.username }}</div>
                    </div>
                    <el-button 
                      size="small" 
                      :type="kb.isFollowed ? 'success' : 'primary'"
                      @click.stop="followKnowledgeBase(kb)"
                    >
                      {{ kb.isFollowed ? '已关注' : '关注' }}
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="post-footer">
              <div class="post-actions">
                <el-button 
                  :type="post.isLiked ? 'primary' : 'text'" 
                  @click="likePost(post)"
                >
                  <el-icon><Pointer /></el-icon>
                  {{ post.likes }}
                </el-button>
                <el-button type="text" @click="showCommentDialog(post)">
                  <el-icon><ChatDotRound /></el-icon>
                  {{ post.comments.length }}
                </el-button>
                <el-button type="text" @click="sharePost(post)">
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
      width="60%"
      :close-on-click-modal="false"
    >
      <el-form :model="postForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="postForm.title" placeholder="请输入标题" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input
            v-model="postForm.content"
            type="textarea"
            :rows="4"
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
              <el-icon><RefreshRight /></el-icon>
              刷新
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
              <el-icon><RefreshRight /></el-icon>
              刷新
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
          <el-button type="primary" :loading="posting" @click="handlePostSubmit">发布</el-button>
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
    <!-- <el-dialog
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
    </el-dialog> -->

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
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Star, 
  ChatDotRound, 
  Share, 
  More, 
  Plus,
  RefreshRight,
  Collection,
  Connection,
  User as UserIcon
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
const loading = ref(false)

// 处理菜单选择
const handleMenuSelect = (key) => {
  activeMenu.value = key
  fetchPosts() // 切换菜单时重新加载帖子
}

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

    // 使用正确的API路径
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

    const data = await response.json()
    if (data.code === 200) {
      // 更新用户信息
      const newUserInfo = {
        id: data.id || 1,
        username: data.username,
        avatar: data.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        followers: data.followers,
        following: data.following
      }
      Object.assign(userInfo, newUserInfo)
      
      // 更新本地存储
      localStorage.setItem('userInfo', JSON.stringify(newUserInfo))
    } else {
      throw new Error(data.message || '获取用户信息失败')
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败，请稍后重试')
    
    // 使用默认值
    const defaultUserInfo = {
      username: '未知',
      avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
    }
    Object.assign(userInfo, defaultUserInfo)
  }
}

// 添加搜索图标导入
import { Search } from '@element-plus/icons-vue'
import { Pointer } from '@element-plus/icons-vue'

// 添加搜索相关状态
const searchQuery = ref('')

// 添加搜索处理函数
const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  
  // 跳转到搜索页面，带上查询参数
  router.push({
    path: '/search',
    query: {
      q: searchQuery.value,
      type: 'all'
    }
  })
}

// 获取帖子列表的新方法
const fetchPosts = async () => {
  loading.value = true
  
  try {
    // 获取token
    const token = localStorage.getItem('token')
    
    // 构建请求参数
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      size: pageSize.value.toString(),
      sort: activeMenu.value
    })
    
    // 发送请求
    const response = await fetch(`/community/posts/?${params.toString()}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    })
    
    if (!response.ok) {
      throw new Error('获取帖子列表失败')
    }
    
    const result = await response.json()
    
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
    setTimeout(() => {
      posts.value = [
        {
          id: 1,
          userId: 101,
          username: '用户A',
          avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
          time: '2025-04-27 10:00',
          title: '分享一个有趣的AI应用',
          content: '最近发现了一个非常有趣的AI应用，可以帮助我们更好地学习和工作...',
          images: [
            'https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg',
            'https://fuss10.elemecdn.com/8/27/f01c15bb73e1ef3793e64e6b7bbccjpeg.jpeg'
          ],
          likes: 128,
          isLiked: false,
          isFavorited: false,
          comments: [
            {
              id: 1,
              username: '用户B',
              avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
              time: '2025-04-27 10:30',
              content: '确实很有趣，感谢分享！'
            }
          ],
          agents: [
            {
              id: 'agent1',
              name: '英语学习助手',
              description: '帮助学习英语的智能体',
              creator: { id: 101, username: '用户A', avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png' },
              followCount: 35,
              isFollowed: false
            }
          ],
          knowledgeBases: [
            {
              id: 'kb1',
              name: '机器学习笔记',
              description: '机器学习相关的学习笔记和资料',
              creator: { id: 101, username: '用户A', avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png' },
              fileCount: 15,
              followCount: 42,
              isFollowed: false
            }
          ]
        }
      ]
      total.value = 100
    }, 500) // 模拟延迟
  } finally {
    loading.value = false
  }
}

// 当页码或每页数量变化时，重新加载数据
watch([currentPage, pageSize], () => {
  fetchPosts()
})

// 组件挂载时执行
onMounted(() => {
  fetchUserInfo()
  fetchPosts()
  checkNewAnnouncements()
})

// 定义接口
interface Comment {
  id: number
  username: string
  avatar: string
  time: string
  content: string
}

// 扩展 Post 接口
interface Post {
  id: number
  userId: number  // 新增用户ID
  username: string
  avatar: string
  time: string
  title: string
  content: string
  images?: string[]
  likes: number
  comments: Comment[]
  // 新增字段
  agents?: Agent[]  // 相关智能体
  knowledgeBases?: KnowledgeBase[]  // 相关知识库
  isLiked?: boolean  // 当前用户是否点赞
  isFavorited?: boolean  // 当前用户是否收藏
  isFollowed?: boolean  // 当前用户是否关注帖子作者
}

// 添加智能体接口
interface Agent {
  id: string
  name: string
  description: string
  avatar?: string
  creator: {
    id: number
    username: string
    avatar: string
  }
  followCount: number
  isFollowed?: boolean  // 当前用户是否关注
}

// 添加知识库接口
interface KnowledgeBase {
  id: string
  name: string
  description: string
  creator: {
    id: number
    username: string
    avatar: string
  }
  fileCount: number
  followCount: number
  isFollowed?: boolean  // 当前用户是否关注
}

// 添加用户接口
interface User {
  id: number
  username: string
  avatar: string
  bio?: string
  followersCount: number
  followingCount: number
  postsCount: number
  agentsCount: number
  isFollowed?: boolean  // 当前用户是否关注
}

// 模拟帖子数据
const posts = ref<Post[]>([
  {
    id: 1,
    userId: 101,
    username: '用户A',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    time: '2025-04-27 10:00',
    title: '分享一个有趣的AI应用',
    content: '最近发现了一个非常有趣的AI应用，可以帮助我们更好地学习和工作...',
    images: [
      'https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg',
      'https://fuss10.elemecdn.com/8/27/f01c15bb73e1ef3793e64e6b7bbccjpeg.jpeg'
    ],
    likes: 128,
    isLiked: false,
    isFavorited: false,
    comments: [
      {
        id: 1,
        username: '用户B',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        time: '2025-04-27 10:30',
        content: '确实很有趣，感谢分享！'
      }
    ],
    agents: [
      {
        id: 'agent1',
        name: '英语学习助手',
        description: '帮助学习英语的智能体',
        creator: { id: 101, username: '用户A', avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png' },
        followCount: 35,
        isFollowed: false
      }
    ],
    knowledgeBases: [
      {
        id: 'kb1',
        name: '机器学习笔记',
        description: '机器学习相关的学习笔记和资料',
        creator: { id: 101, username: '用户A', avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png' },
        fileCount: 15,
        followCount: 42,
        isFollowed: false
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

// 用户的智能体和知识库列表
const userAgents = ref<Agent[]>([])
const userKnowledgeBases = ref<KnowledgeBase[]>([])
const posting = ref(false)

// 扩展发帖表单
const postForm = reactive({
  title: '',
  content: '',
  images: [] as File[],
  imageUrls: [] as string[],
  selectedAgents: [] as string[],
  selectedKnowledgeBases: [] as string[]
})

// 获取用户的智能体列表
const fetchUserAgents = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }

    // 实际API请求
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

    const data = await response.json()
    if (data.code === 200) {
      userAgents.value = data.data || []
    } else {
      throw new Error(data.message || '获取智能体列表失败')
    }
  } catch (error) {
    console.error('获取智能体列表失败:', error)
    ElMessage.error('获取智能体列表失败，请稍后重试')
    
    // 模拟数据（开发阶段使用）
    userAgents.value = [
      {
        id: 'agent1',
        name: '英语学习助手',
        description: '帮助学习英语的智能体',
        creator: { id: 1, username: '当前用户', avatar: userInfo.avatar },
        followCount: 35,
        isFollowed: false
      },
      {
        id: 'agent2',
        name: '编程教练',
        description: '辅助编程学习和解决问题',
        creator: { id: 1, username: '当前用户', avatar: userInfo.avatar },
        followCount: 128,
        isFollowed: false
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

    // 实际API请求
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

    const data = await response.json()
    if (data.code === 200) {
      userKnowledgeBases.value = data.data || []
    } else {
      throw new Error(data.message || '获取知识库列表失败')
    }
  } catch (error) {
    console.error('获取知识库列表失败:', error)
    ElMessage.error('获取知识库列表失败，请稍后重试')
    
    // 模拟数据（开发阶段使用）
    userKnowledgeBases.value = [
      {
        id: 'kb1',
        name: '机器学习笔记',
        description: '机器学习相关的学习笔记和资料',
        creator: { id: 1, username: '当前用户', avatar: userInfo.avatar },
        fileCount: 15,
        followCount: 42,
        isFollowed: false
      },
      {
        id: 'kb2',
        name: '产品文档',
        description: '产品相关的文档和说明',
        creator: { id: 1, username: '当前用户', avatar: userInfo.avatar },
        fileCount: 8,
        followCount: 17,
        isFollowed: false
      }
    ]
  }
}

// 打开发帖对话框时获取用户资源
const showPostDialog = () => {
  // 重置表单
  postForm.title = ''
  postForm.content = ''
  postForm.images = []
  postForm.imageUrls = []
  postForm.selectedAgents = []
  postForm.selectedKnowledgeBases = []
  
  // 获取用户的智能体和知识库
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
    ElMessageBox.confirm('确定要取消发布吗？已编辑的内容将不会保存。', '取消发布', {
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
const handleImageRemove = (file, fileList) => {
  const index = postForm.images.findIndex(item => item === file.raw)
  if (index !== -1) {
    postForm.images.splice(index, 1)
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
  postForm.images.push(file.raw)
  
  // 创建预览URL
  const imageUrl = URL.createObjectURL(file.raw)
  postForm.imageUrls.push(imageUrl)
  
  return true
}

// 发布帖子
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
    
    // 先上传图片（如果有）
    let uploadedImages = []
    if (postForm.images.length > 0) {
      const formData = new FormData()
      postForm.images.forEach(img => {
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
        uploadedImages = uploadResult.data || []
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
    
    // 发布帖子请求
    const response = await fetch('/user/post/create/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(postData)
    })
    
    if (!response.ok) {
      throw new Error('发布帖子失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      ElMessage.success('发布成功')
      postDialogVisible.value = false
      
      // 刷新帖子列表
      fetchPosts()
    } else {
      throw new Error(result.message || '发布帖子失败')
    }
  } catch (error) {
    console.error('发布帖子失败:', error)
    ElMessage.error('发布帖子失败，请稍后重试')
  } finally {
    posting.value = false
  }
}

// 查看用户资料
const viewUserProfile = (userId) => {
  router.push(`/user-profile/${userId}`)
}

// 关注用户
const followUser = async (userId) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    // 检查是否已关注
    const post = posts.value.find(p => p.userId === userId)
    const isFollowed = post?.isFollowed
    
    // 关注/取消关注请求
    const response = await fetch(`/user/follow/${userId}/`, {
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
    if (response.status === 200) {
      // 更新状态
      posts.value.forEach(p => {
        if (p.userId === userId) {
          p.isFollowed = !isFollowed
        }
      })
      
      ElMessage.success(isFollowed ? '已取消关注' : '关注成功')
    } else {
      throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
    }
  } catch (error) {
    console.error('关注用户操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

// 收藏帖子
const favoritePost = async (post) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const isFavorited = post.isFavorited
    
    // 收藏/取消收藏请求
    const response = await fetch(`/user/favorite/post/${post.id}/`, {
      method: isFavorited ? 'DELETE' : 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(isFavorited ? '取消收藏失败' : '收藏失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      // 更新状态
      post.isFavorited = !isFavorited
      
      ElMessage.success(isFavorited ? '已取消收藏' : '收藏成功')
    } else {
      throw new Error(result.message || (isFavorited ? '取消收藏失败' : '收藏失败'))
    }
  } catch (error) {
    console.error('收藏帖子操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

// 点赞帖子
const likePost = async (post) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const isLiked = post.isLiked
    
    // 点赞/取消点赞请求
    const response = await fetch(`/user/like/post/${post.id}/`, {
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
  }
}

// 关注智能体
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
      agent.followCount = isFollowed ? agent.followCount - 1 : agent.followCount + 1
      
      ElMessage.success(isFollowed ? '已取消关注智能体' : '关注智能体成功')
    } else {
      throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
    }
  } catch (error) {
    console.error('关注智能体操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

// 关注知识库
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
      kb.followCount = isFollowed ? kb.followCount - 1 : kb.followCount + 1
      
      ElMessage.success(isFollowed ? '已取消关注知识库' : '关注知识库成功')
    } else {
      throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
    }
  } catch (error) {
    console.error('关注知识库操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

// 查看智能体详情
const viewAgentDetail = (agentId) => {
  router.push(`/agent-detail/${agentId}`)
}

// 查看知识库详情
const viewKnowledgeBaseDetail = (kbId) => {
  router.push(`/knowledge-base/${kbId}`)
}

// 举报帖子
const reportPost = (postId) => {
  ElMessageBox.prompt('请输入举报原因', '举报帖子', {
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

// 分享帖子
const sharePost = (post) => {
  const shareUrl = `${window.location.origin}/post/${post.id}`
  // 复制链接到剪贴板
  navigator.clipboard.writeText(shareUrl).then(() => {
    ElMessage.success('链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('链接复制失败，请手动复制')
    // 显示分享链接
    ElMessageBox.alert(`${shareUrl}`, '分享链接', {
      confirmButtonText: '关闭'
    })
  })
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchPosts()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchPosts()
}

// 评论相关
const showCommentDialog = (post) => {
  currentPost.value = post
  commentContent.value = ''
  commentDialogVisible.value = true
}

const handleCommentSubmit = async () => {
  if (!commentContent.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    // 评论请求
    const response = await fetch(`/user/comment/post/${currentPost.value.id}/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: commentContent.value
      })
    })
    
    if (!response.ok) {
      throw new Error('发表评论失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      // 添加新评论到列表
      const newComment = {
        id: Date.now(), // 临时ID
        username: userInfo.username,
        avatar: userInfo.avatar,
        time: new Date().toLocaleString(),
        content: commentContent.value
      }
      
      // 更新当前帖子的评论
      currentPost.value.comments.push(newComment)
      
      // 更新帖子列表中的评论数量
      posts.value.forEach(post => {
        if (post.id === currentPost.value.id) {
          post.comments = currentPost.value.comments
        }
      })
      
      // 清空输入框
      commentContent.value = ''
      
      ElMessage.success('评论成功')
    } else {
      throw new Error(result.message || '发表评论失败')
    }
  } catch (error) {
    console.error('发表评论失败:', error)
    ElMessage.error('发表评论失败，请稍后重试')
    
    // 开发阶段模拟成功
    const newComment = {
      id: Date.now(),
      username: userInfo.username || '当前用户',
      avatar: userInfo.avatar,
      time: new Date().toLocaleString(),
      content: commentContent.value
    }
    
    currentPost.value.comments.push(newComment)
    posts.value.forEach(post => {
      if (post.id === currentPost.value.id) {
        post.comments = currentPost.value.comments
      }
    })
    
    commentContent.value = ''
    ElMessage.success('评论成功')
  }
}

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    // 通过向后端发送用户id来注销登录
    try {
      const userId = localStorage.getItem('userId')
      if (!userId) {
        ElMessage.error('用户ID不存在，请重新登录')
        return
      }
      const response = await fetch(`/user/logout/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error('注销登录失败')
      } else {
        // 清除登录状态
        localStorage.removeItem('token');
        localStorage.removeItem('userInfo');
        router.push('/login');
        ElMessage.success('已退出登录');
      }
    } catch (error) {
      ElMessage.error('注销失败，请稍后重试');
    }
  }).catch(() => {})
}

// 添加创建智能体相关变量
const createAgentDialogVisible = ref(false)
const agentInitData = reactive({
  name: '',
  description: ''
})

// 显示创建智能体对话框
const showCreateAgentDialog = () => {
  agentInitData.name = ''
  agentInitData.description = ''
  createAgentDialogVisible.value = true
}

// 创建智能体
const handleCreateAgent = () => {
  if (!agentInitData.name.trim()) {
    ElMessage.warning('请输入智能体名称')
    return
  }
  
  // 将初始数据存储到本地存储以便编辑器页面获取
  localStorage.setItem('agentInitData', JSON.stringify(agentInitData))
  
  // 关闭对话框
  createAgentDialogVisible.value = false
  
  // 跳转到智能体编辑器页面
  router.push('/agent-editor')
}

// 获取用户信息
fetchUserInfo()

// 获取帖子列表
fetchPosts()

</script>

<style scoped>
.community-container {
  height: 100%;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #ebeef5;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.post-list {
  max-width: 800px;
  margin: 0 auto;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-title {
  display: flex;
  align-items: center;
  gap: 8px;
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

.comment-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.comment-item {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.comment-input {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.time {
  font-size: 12px;
  color: #909399;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

/* 加载中样式 */
.loading-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 0;
}

/* 资源选择器样式 */
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

/* 帖子中的资源展示 */
.post-resources {
  margin-top: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
  background-color: #f8fafc;
}

.resource-header {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 10px;
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background-color: #fff;
  border-radius: 4px;
  border: 1px solid #ebeef5;
  cursor: pointer;
  transition: all 0.3s;
}

.resource-item:hover {
  background-color: #f5f7fa;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.resource-item-icon {
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

.resource-item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.resource-item-name {
  font-weight: 500;
  font-size: 14px;
}

.resource-item-creator {
  font-size: 12px;
  color: #909399;
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

/* 修改帖子样式 */
.post-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.post-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.search-container {
  width: 300px;
  margin-right: 15px;
}
</style>