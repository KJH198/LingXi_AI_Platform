<template>
  <div class="kb-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton style="width: 100%" animated>
        <template #template>
          <div style="padding: 20px">
            <el-skeleton-item variant="image" style="width: 100%; height: 150px" />
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px">
              <div>
                <el-skeleton-item variant="h3" style="width: 200px; margin-bottom: 10px" />
                <el-skeleton-item variant="text" style="width: 300px" />
              </div>
              <div>
                <el-skeleton-item variant="button" style="width: 100px; margin-right: 10px" />
                <el-skeleton-item variant="button" style="width: 100px" />
              </div>
            </div>
          </div>
        </template>
      </el-skeleton>
    </div>

    <div v-else class="kb-detail">
      <!-- 返回按钮 -->
      <div class="back-button">
        <el-button @click="goBack" text>
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
      </div>

      <!-- 知识库基本信息 -->
      <el-card class="kb-header">
        <div class="header-content">
          <div class="kb-avatar">
            <div class="avatar-placeholder">KB</div>
          </div>
          <div class="kb-info">
            <h1>{{ kbData.name }}</h1>
            <div class="kb-creator">
              <span>创建者:</span>
              <el-avatar :size="24" :src="kbData.creator.avatar" @click="viewUserProfile(kbData.creator.id)" style="cursor: pointer; margin: 0 5px" />
              <span class="creator-name" @click="viewUserProfile(kbData.creator.id)">{{ kbData.creator.username }}</span>
            </div>
            <div class="kb-stats">
              <span class="stat-item"><el-icon><Document /></el-icon> {{ kbData.fileCount || 0 }} 文件</span>
              <span class="stat-item"><el-icon><View /></el-icon> {{ kbData.views || 0 }} 浏览</span>
              <span class="stat-item"><el-icon><User /></el-icon> {{ kbData.followers || 0 }} 关注</span>
              <span class="stat-item"><el-icon><Timer /></el-icon> {{ kbData.created_at || '未知' }} 创建</span>
            </div>
            <div class="kb-tags" v-if="kbData.tags && kbData.tags.length">
              <el-tag v-for="tag in kbData.tags" :key="tag" size="small" class="tag">{{ tag }}</el-tag>
            </div>
          </div>
          <div class="kb-actions">
            <el-button 
              :type="kbData.isFollowed ? 'success' : 'primary'" 
              @click="handleFollow"
            >
              <el-icon><Star /></el-icon> 
              {{ kbData.isFollowed ? '已关注' : '关注' }}
            </el-button>
            <el-button 
              :type="kbData.isLiked ? 'danger' : 'default'" 
              @click="handleLike"
            >
              <el-icon><Pointer /></el-icon> 
              {{ kbData.isLiked ? '已点赞' : '点赞' }}
            </el-button>
            <!-- <el-button @click="handleShare">
              <el-icon><Share /></el-icon> 分享
            </el-button> -->
          </div>
        </div>
      </el-card>

      <!-- 详细内容 -->
      <el-tabs v-model="activeTab" class="kb-tabs">
        <el-tab-pane label="介绍" name="intro">
          <el-card class="tab-card">
            <h2>知识库介绍</h2>
            <div class="description">
              <p>{{ kbData.description || '暂无介绍' }}</p>
            </div>

            <!-- <h3>适用场景</h3>
            <div class="scenarios" v-if="kbData.scenarios && kbData.scenarios.length">
              <el-tag v-for="scenario in kbData.scenarios" :key="scenario" size="large" class="scenario-tag">
                {{ scenario }}
              </el-tag>
            </div>
            <el-empty v-else description="暂无适用场景说明" /> -->
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="文件列表" name="files">
          <el-card class="tab-card">
            <div class="file-header">
              <h2>文件列表</h2>
              <div class="search-box">
                <el-input
                  v-model="fileSearchKeyword"
                  placeholder="搜索文件..."
                  prefix-icon="el-icon-search"
                  clearable
                  @input="handleFileSearch"
                />
              </div>
            </div>

            <div class="file-list" v-if="kbData.files && filteredFiles.length">
              <el-table
                :data="filteredFiles"
                style="width: 100%"
                :row-class-name="tableRowClassName"
              >
                <el-table-column prop="name" label="文件名" min-width="250">
                  <template #default="scope">
                    <div class="file-name-cell">
                      <el-icon><Document /></el-icon>
                      <span>{{ scope.row.name }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="type" label="类型" width="120" />
                <el-table-column prop="size" label="大小" width="120" />
                <el-table-column prop="lastUpdated" label="更新时间" width="180" />
                <!-- <el-table-column label="操作" width="180">
                  <template #default="scope">
                    <el-button
                      type="primary"
                      size="small"
                      @click="previewFile(scope.row)"
                      v-if="canPreviewFile(scope.row)"
                    >
                      预览
                    </el-button>
                    <el-button
                      type="primary"
                      size="small"
                      @click="downloadFile(scope.row)"
                      v-if="kbData.creator.id === currentUserId || scope.row.isPublic"
                    >
                      下载
                    </el-button>
                  </template>
                </el-table-column> -->
              </el-table>

              <!-- 文件分页 -->
              <div class="pagination" v-if="kbData.files.length > 10">
                <el-pagination
                  v-model:current-page="fileCurrentPage"
                  :page-size="filePageSize"
                  layout="total, prev, pager, next"
                  :total="kbData.files.length"
                  @current-change="handleFilePageChange"
                />
              </div>
            </div>
            <el-empty v-else description="暂无文件或无搜索结果" />
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="相关智能体" name="agents">
          <el-card class="tab-card">
            <h2>相关智能体</h2>
            <div class="related-agents" v-if="kbData.relatedAgents && kbData.relatedAgents.length">
              <div v-for="agent in kbData.relatedAgents" :key="agent.id" class="agent-item" @click="viewAgent(agent.id)">
                <div class="agent-icon">AI</div>
                <div class="agent-info">
                  <h3>{{ agent.name }}</h3>
                  <p>{{ agent.description }}</p>
                  <div class="agent-meta">
                    <span><el-icon><User /></el-icon> {{ agent.creator.username }}</span>
                    <span><el-icon><Star /></el-icon> {{ agent.followCount || 0 }} 关注</span>
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
            <el-empty v-else description="暂无相关智能体" />
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="评论" name="comments">
          <el-card class="tab-card">
            <h2>评论</h2>
            
            <!-- 评论输入框 -->
            <div class="comment-input">
              <el-avatar :size="40" :src="currentUserAvatar">U</el-avatar>
              <div class="input-area">
                <el-input
                  v-model="commentContent"
                  type="textarea"
                  :rows="2"
                  placeholder="写下你的评论..."
                  maxlength="200"
                  show-word-limit
                />
                <div class="comment-actions">
                  <el-button type="primary" @click="submitComment" :disabled="!commentContent.trim()">发表评论</el-button>
                </div>
              </div>
            </div>
            
            <!-- 评论列表 -->
            <div class="comment-list" v-if="kbData.comments && kbData.comments.length">
              <div v-for="comment in kbData.comments" :key="comment.id" class="comment-item">
                <el-avatar :size="40" :src="comment.user.avatar" @click="viewUserProfile(comment.user.id)">{{ comment.user.username.substring(0, 1) }}</el-avatar>
                <div class="comment-content">
                  <div class="comment-header">
                    <span class="comment-username" @click="viewUserProfile(comment.user.id)">{{ comment.user.username }}</span>
                    <span class="comment-time">{{ comment.time }}</span>
                  </div>
                  <p>{{ comment.content }}</p>
                  <div class="comment-actions">
                    <el-button
                      :type="comment.isLiked ? 'primary' : 'text'"
                      size="small" 
                      @click="likeComment(comment)">
                      <el-icon><Pointer /></el-icon> {{ comment.likes || 0 }}
                    </el-button>
                    <!-- <el-button text size="small" @click="replyComment(comment)">
                      <el-icon><ChatLineRound /></el-icon> 回复
                    </el-button> -->
                    
                    <!-- 添加删除按钮，仅对评论作者或知识库创建者显示 -->
                    <el-button 
                      v-if="canDeleteComment(comment)" 
                      text 
                      type="danger" 
                      size="small" 
                      @click="confirmDeleteComment(comment)"
                    >
                      <el-icon><Delete /></el-icon> 删除
                    </el-button>
                  </div>
                  
                  <!-- 回复列表 -->
                  <!-- <div class="reply-list" v-if="comment.replies && comment.replies.length">
                    <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                      <el-avatar :size="32" :src="reply.user.avatar" @click="viewUserProfile(reply.user.id)">{{ reply.user.username.substring(0, 1) }}</el-avatar>
                      <div class="reply-content">
                        <div class="reply-header">
                          <span class="reply-username" @click="viewUserProfile(reply.user.id)">{{ reply.user.username }}</span>
                          <span class="reply-time">{{ reply.time }}</span>
                        </div>
                        <p>{{ reply.content }}</p>
                      </div>
                    </div>
                  </div> -->
                  
                  <!-- 回复输入框 -->
                  <!-- <div class="reply-input" v-if="replyingTo === comment.id">
                    <el-input 
                      v-model="replyContent" 
                      size="small" 
                      placeholder="回复评论..." 
                      maxlength="100"
                      show-word-limit
                    >
                      <template #append>
                        <el-button @click="submitReply(comment)">回复</el-button>
                      </template>
                    </el-input>
                  </div> -->
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无评论，快来发表第一条评论吧" />

            <!-- 分页 -->
            <div class="pagination" v-if="kbData.comments && kbData.comments.length > 10">
              <el-pagination
                v-model:current-page="commentCurrentPage"
                :page-size="commentPageSize"
                layout="prev, pager, next"
                :total="totalComments"
                @current-change="handleCommentPageChange"
              />
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 文件预览对话框 -->
    <el-dialog v-model="filePreviewVisible" :title="currentPreviewFile?.name || '文件预览'" width="80%" destroy-on-close>
      <div class="file-preview-container">
        <!-- 文档预览 -->
        <div v-if="previewType === 'document'" class="document-preview">
          <div class="preview-content" v-html="documentContent"></div>
        </div>
        
        <!-- 图片预览 -->
        <div v-else-if="previewType === 'image'" class="image-preview">
          <el-image :src="previewUrl" fit="contain" style="width: 100%; max-height: 70vh;" />
        </div>
        
        <!-- PDF预览 -->
        <div v-else-if="previewType === 'pdf'" class="pdf-preview">
          <iframe :src="previewUrl" style="width: 100%; height: 70vh; border: none;"></iframe>
        </div>
        
        <!-- 其他文件类型 -->
        <div v-else class="unsupported-preview">
          <el-empty description="无法预览此类型的文件，请下载后查看">
            <template #extra>
              <el-button type="primary" @click="downloadFile(previewFile)">下载文件</el-button>
            </template>
          </el-empty>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Star, 
  View, 
  User, 
  ArrowLeft, 
  More, 
  StarFilled, 
  Share, 
  CopyDocument, 
  Warning, 
  Document,
  Timer,
  ChatLineRound,
  Pointer,
  Delete
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const activeTab = ref('intro')
const kbId = computed(() => route.params.id as string)
const commentContent = ref('')
const replyContent = ref('')
const replyingTo = ref<number | null>(null)
const commentCurrentPage = ref(1)
const commentPageSize = ref(10)
const totalComments = ref(0)
const fileCurrentPage = ref(1)
const filePageSize = ref(10)
const fileSearchKeyword = ref('')

// 文件预览相关
const filePreviewVisible = ref(false)
const currentPreviewFile = ref(null)
const previewType = ref('')
const previewUrl = ref('')
const documentContent = ref('')

// 用户头像
const currentUserAvatar = ref('')

// 知识库数据
const kbData = reactive({
  id: '',
  name: '',
  description: '',
  fileCount: 0,
  views: 0,
  followers: 0,
  created_at: '',
  isFollowed: false,
  isLiked: false,
  tags: [] as string[],
  scenarios: [] as string[],
  creator: {
    id: 0,
    username: '',
    avatar: ''
  },
  files: [] as {
    id: string;
    name: string;
    type: string;
    size: string;
    lastUpdated: string;
    isPublic: boolean;
    url?: string;
  }[],
  relatedAgents: [] as {
    id: string;
    name: string;
    description: string;
    creator: {
      id: number;
      username: string;
      avatar: string;
    };
    followCount: number;
    isFollowed: boolean;
  }[],
  comments: [] as {
    id: number;
    user: {
      id: number;
      username: string;
      avatar: string;
    };
    time: string;
    content: string;
    likes: number;
    isLiked: boolean;
  }[]
})

// 检查是否可以克隆知识库
const canClone = computed(() => {
  return kbData.creator.id !== getCurrentUserId()
})

const getCurrentUserId = () => {
  try {
    
    // 其次尝试从本地存储获取
    const storedUserId = localStorage.getItem('userId');
    if (storedUserId) {
      return parseInt(storedUserId, 10);
    }
    
    // 最后尝试从 token 解析
    const token = localStorage.getItem('token');
    if (token) {
      // 如果使用JWT，可以尝试解析token获取用户ID
      // 注意: 这种方法只适用于JWT，且ID需要包含在payload中
      try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const payload = JSON.parse(window.atob(base64));
        if (payload.userId || payload.user_id || payload.id) {
          return payload.userId || payload.user_id || payload.id;
        }
      } catch (tokenError) {
        console.error('解析token失败:', tokenError);
      }
    }
    
    // 所有方法都失败，返回null表示未登录或获取失败
    console.warn('无法获取当前用户ID，用户可能未登录');
    return null;
  } catch (error) {
    console.error('获取当前用户ID时发生错误:', error);
    return null;
  }
};

// 获取当前用户ID
const currentUserId = computed(() => getCurrentUserId())

// 过滤的文件列表
const filteredFiles = computed(() => {
  if (!fileSearchKeyword.value) {
    return kbData.files
  }
  const keyword = fileSearchKeyword.value.toLowerCase()
  return kbData.files.filter(file => 
    file.name.toLowerCase().includes(keyword) || 
    file.type.toLowerCase().includes(keyword)
  )
})

// 获取用户头像
const fetchUserAvatar = () => {
  const userInfo = localStorage.getItem('userInfo')
  if (userInfo) {
    try {
      const parsedInfo = JSON.parse(userInfo)
      currentUserAvatar.value = parsedInfo.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
    } catch (e) {
      currentUserAvatar.value = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
    }
  } else {
    currentUserAvatar.value = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
  }
}

// 获取知识库详情
const fetchKnowledgeBaseDetail = async () => {
  loading.value = true
  
  try {
    const token = localStorage.getItem('token')
    
    // 构建API请求
    const response = await fetch(`/knowledge-base/${kbId.value}/detail/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    })
    
    if (!response.ok) {
      throw new Error('获取知识库详情失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      kbData.id = result.data.id
      kbData.name = result.data.name
      kbData.description = result.data.description || '暂无介绍'
      kbData.fileCount = result.data.file_count || 0
      kbData.views = result.data.views || 0
      kbData.followers = result.data.followers || 0
      kbData.created_at = result.data.created_at || '未知'
      kbData.isFollowed = result.data.is_followed || false
      kbData.isLiked = result.data.is_liked || false
      kbData.tags = result.data.tags || []
      kbData.scenarios = result.data.scenarios || []

      kbData.creator = {
        id: result.data.creator.id,
        username: result.data.creator.username,
        avatar: result.data.creator.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
      }
      kbData.files = result.data.files || []
      kbData.relatedAgents = result.data.related_agents || []
      kbData.comments = result.data.comments || []
      totalComments.value = kbData.comments.length || 0
      fetchUserAvatar() // 获取当前用户头像
    } else {
      throw new Error(result.message || '获取知识库详情失败')
    }
  } catch (error) {
    console.error('获取知识库详情失败:', error)
    ElMessage.error('获取知识库详情失败，请稍后重试')
    
    // 模拟数据（开发阶段）
    setTimeout(() => {
      Object.assign(kbData, {
        id: kbId.value,
        name: '机器学习知识库',
        description: '这是一个涵盖机器学习基础理论和实践应用的知识库，包含各种算法介绍、模型选择指南、数据预处理方法和实际案例分析。适合初学者到中级学习者使用。',
        fileCount: 25,
        views: 1235,
        followers: 98,
        lastUpdated: '2025-05-05',
        isFollowed: false,
        isLiked: false,
        tags: ['机器学习', '人工智能', '数据科学', '教育资源'],
        scenarios: ['入门学习', '模型选择', '算法对比', '数据预处理', '实战案例'],
        creator: {
          id: 102,
          username: '数据科学家',
          avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
        },
        files: [
          {
            id: 'file1',
            name: '机器学习基础概念.pdf',
            type: 'PDF',
            size: '2.5 MB',
            lastUpdated: '2025-04-12',
            isPublic: true,
            url: 'https://example.com/files/ml-basics.pdf'
          },
          {
            id: 'file2',
            name: '监督学习算法对比.xlsx',
            type: 'Excel',
            size: '1.2 MB',
            lastUpdated: '2025-04-15',
            isPublic: true,
            url: 'https://example.com/files/supervised-algorithms.xlsx'
          },
          {
            id: 'file3',
            name: '数据预处理技巧.docx',
            type: 'Word',
            size: '850 KB',
            lastUpdated: '2025-04-20',
            isPublic: true,
            url: 'https://example.com/files/data-preprocessing.docx'
          },
          {
            id: 'file4',
            name: '神经网络结构示意图.png',
            type: 'Image',
            size: '1.5 MB',
            lastUpdated: '2025-04-22',
            isPublic: true,
            url: 'https://example.com/files/neural-network.png'
          },
          {
            id: 'file5',
            name: '决策树实现代码.py',
            type: 'Python',
            size: '45 KB',
            lastUpdated: '2025-04-25',
            isPublic: true,
            url: 'https://example.com/files/decision-tree.py'
          }
        ],
        relatedAgents: [
          {
            id: 'agent1',
            name: '机器学习教练',
            description: '帮助理解机器学习概念，解答问题并提供实践指导',
            creator: {
              id: 102,
              username: '数据科学家',
              avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
            },
            followCount: 146,
            isFollowed: false
          },
          {
            id: 'agent2',
            name: '算法选择助手',
            description: '根据数据特征和问题类型，推荐合适的机器学习算法',
            creator: {
              id: 103,
              username: 'AI专家',
              avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
            },
            followCount: 89,
            isFollowed: false
          }
        ],
        comments: [
          {
            id: 1,
            user: {
              id: 201,
              username: '学习者A',
              avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
            },
            time: '2025-05-03 14:20',
            content: '非常全面的知识库，特别是数据预处理的部分讲解得很详细，对我的项目有很大帮助。',
            likes: 8,
            replies: [
              {
                id: 101,
                user: {
                  id: 102,
                  username: '数据科学家',
                  avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
                },
                time: '2025-05-03 15:30',
                content: '谢谢反馈！如果有任何问题，欢迎随时提出。'
              }
            ]
          },
          {
            id: 2,
            user: {
              id: 202,
              username: '学习者B',
              avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
            },
            time: '2025-05-02 09:45',
            content: '决策树的代码实现非常清晰，但希望能增加一些关于随机森林的内容。',
            likes: 5,
            replies: []
          }
        ]
      })
      totalComments.value = kbData.comments.length
    }, 800)
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 查看用户资料
const viewUserProfile = (userId) => {
  router.push(`/user-profile/${userId}`)
}

// 表格行样式
const tableRowClassName = ({ row, rowIndex }) => {
  return ''
}

// 文件搜索
const handleFileSearch = () => {
  fileCurrentPage.value = 1
}

// 文件分页
const handleFilePageChange = (page) => {
  fileCurrentPage.value = page
}

// 评论分页
const handleCommentPageChange = (page) => {
  commentCurrentPage.value = page
}

// 检查文件是否可以预览
const canPreviewFile = (file) => {
  const previewableTypes = ['PDF', 'Image', 'Word', 'Excel', 'Text']
  return previewableTypes.includes(file.type) && file.isPublic
}

// 预览文件
const previewFile = (file) => {
  currentPreviewFile.value = file
  
  // 根据文件类型设置预览类型
  if (file.type === 'PDF') {
    previewType.value = 'pdf'
    previewUrl.value = file.url
  } else if (file.type === 'Image') {
    previewType.value = 'image'
    previewUrl.value = file.url
  } else if (['Word', 'Excel', 'Text'].includes(file.type)) {
    previewType.value = 'document'
    // 模拟文档内容，实际应该从API获取
    documentContent.value = `<div style="padding: 20px;">
      <h3>${file.name} 的内容预览</h3>
      <p>这是文档内容的预览。在实际应用中，应该从服务器获取文档的HTML渲染结果。</p>
      <p>对于Word、Excel和Text类型的文件，可以通过后端服务将其转换为HTML格式进行预览。</p>
    </div>`
  } else {
    previewType.value = 'unsupported'
  }
  
  filePreviewVisible.value = true
}

// 下载文件
const downloadFile = (file) => {
  // 检查权限
  if (!file.isPublic && kbData.creator.id !== currentUserId.value) {
    ElMessage.warning('您没有权限下载此文件')
    return
  }
  
  // 直接下载或通过API
  if (file.url) {
    const link = document.createElement('a')
    link.href = file.url
    link.download = file.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('开始下载文件')
  } else {
    // 通过API下载
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    // 模拟下载
    ElMessage.success('开始下载文件')
  }
}

// 关注知识库
const handleFollow = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const isFollowed = kbData.isFollowed
    
    // 关注/取消关注请求
    const response = await fetch(`/user/follow/knowledge-base/${kbId.value}/`, {
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
      kbData.isFollowed = !isFollowed
      kbData.followers = isFollowed ? kbData.followers - 1 : kbData.followers + 1
      
      ElMessage.success(isFollowed ? '已取消关注' : '关注成功')
    } else {
      throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
    }
  } catch (error) {
    console.error('关注操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
    
    // 模拟（开发阶段）
    kbData.isFollowed = !kbData.isFollowed
    kbData.followers = kbData.isFollowed ? kbData.followers + 1 : kbData.followers - 1
    ElMessage.success(kbData.isFollowed ? '关注成功' : '已取消关注')
  }
}

// 点赞知识库
const handleLike = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const isLiked = kbData.isLiked
    
    // 点赞/取消点赞请求
    const response = await fetch(`/knowledge-base/${kbId.value}/like/`, {
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
      kbData.isLiked = !isLiked
      
      ElMessage.success(isLiked ? '已取消点赞' : '点赞成功')
    } else {
      throw new Error(result.message || (isLiked ? '取消点赞失败' : '点赞失败'))
    }
  } catch (error) {
    console.error('点赞操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
    
    // 模拟（开发阶段）
    kbData.isLiked = !kbData.isLiked
    ElMessage.success(kbData.isLiked ? '点赞成功' : '已取消点赞')
  }
}

// 分享知识库
const handleShare = () => {
  const shareUrl = `${window.location.origin}/#/knowledge-base/${kbId.value}`
  
  // 复制到剪贴板
  navigator.clipboard.writeText(shareUrl).then(() => {
    ElMessage.success('链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制链接')
    // 显示链接弹窗
    ElMessageBox.alert(shareUrl, '分享链接', {
      confirmButtonText: '确定'
    })
  })
}

// 克隆知识库
const handleClone = () => {
  ElMessageBox.confirm('确定要克隆这个知识库吗？', '克隆知识库', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(() => {
    // 检查登录状态
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    // 模拟克隆
    setTimeout(() => {
      ElMessage.success('知识库克隆成功，请前往我的知识库查看')
    }, 1000)
  }).catch(() => {})
}

// 举报知识库
const handleReport = () => {
  ElMessageBox.prompt('请输入举报原因', '举报知识库', {
    confirmButtonText: '提交',
    cancelButtonText: '取消',
    inputPlaceholder: '请简要说明举报原因'
  }).then(({ value }) => {
    if (value.trim()) {
      // 发送举报请求
      ElMessage.success('举报已提交，感谢您的反馈')
    } else {
      ElMessage.warning('请输入举报原因')
    }
  }).catch(() => {})
}

// 查看智能体
const viewAgent = (agentId) => {
  router.push(`/agent-detail/${agentId}`)
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
    const response = await fetch(`/agent/${agent.id}/follow/`, {
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
    
    // 模拟（开发阶段）
    agent.isFollowed = !agent.isFollowed
    agent.followCount = agent.isFollowed ? agent.followCount + 1 : agent.followCount - 1
    ElMessage.success(agent.isFollowed ? '关注智能体成功' : '已取消关注智能体')
  }
}

// 提交评论
const submitComment = async () => {
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
    
    // 发送评论请求
    const response = await fetch(`/knowledge-base/${kbId.value}/comment/`, {
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
      throw new Error('评论失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      ElMessage.success('评论成功')
      console.log('发表评论id:', result.data.commentId, result.time)
      
      // 获取本地用户信息
      const userInfo = localStorage.getItem('userInfo')
      let userData = { id: 0, username: '匿名用户', avatar: currentUserAvatar.value }
      if (userInfo) {
        try {
          userData = JSON.parse(userInfo)
        } catch (e) {}
      }
      
      // 添加新评论
      const newComment = {
        id: result.data.commentId,
        user: {
          id: Number(localStorage.getItem('userId')) || userData.id,
          username: userData.username,
          avatar: userData.avatar
        },
        time: result.time || new Date().toLocaleString(),
        content: commentContent.value,
        likes: 0,
        isLiked: false,
      }
      
      kbData.comments.unshift(newComment)
      totalComments.value += 1
      
      // 清空评论框
      commentContent.value = ''
    } else {
      throw new Error(result.message || '评论失败')
    }
  } catch (error) {
    console.error('评论失败:', error)
    ElMessage.error('评论失败，请稍后重试')
    
    // 模拟（开发阶段）
    const userInfo = localStorage.getItem('userInfo')
    let userData = { id: 0, username: '当前用户', avatar: currentUserAvatar.value }
    if (userInfo) {
      try {
        userData = JSON.parse(userInfo)
      } catch (e) {}
    }
    
    const newComment = {
      id: Date.now(),
      user: {
        id: userData.id,
        username: userData.username,
        avatar: userData.avatar
      },
      time: new Date().toLocaleString(),
      content: commentContent.value,
      likes: 0,
      isLiked: false
    }
    
    kbData.comments.unshift(newComment)
    totalComments.value += 1
    commentContent.value = ''
    ElMessage.success('评论成功')
  }
}

// 点赞评论
const likeComment = async (comment) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    // 检查当前点赞状态
    const isLiked = comment.isLiked || false
    
    // 点赞评论请求 - 修正API路径和请求方法
    const response = await fetch(`/user/like/knowledge_base_comment/${comment.id}/`, {
      method: isLiked ? 'DELETE' : 'POST',  // 根据当前状态决定是点赞还是取消点赞
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log('点赞响应状态：', response.status)
    
    // 尝试解析响应，即使状态码不是200
    const result = await response.json().catch(e => {
      console.error('解析响应JSON失败:', e)
      return { code: 0, message: '响应格式错误' }
    })
    
    console.log('点赞结果:', result)
    
    // 更宽松的成功条件判断
    if (response.ok || result.code === 200) {
      // 更新状态
      comment.isLiked = !isLiked
      comment.likes = isLiked ? comment.likes - 1 : comment.likes + 1
      
      ElMessage.success(isLiked ? '已取消点赞' : '点赞成功')
      return // 成功时直接返回，避免执行后面的模拟代码
    } else {
      throw new Error(result.message || (isLiked ? '取消点赞失败' : '点赞失败'))
    }
  } catch (error) {
    console.error('点赞评论失败:', error)
  }
}

// 回复评论
const replyComment = (comment) => {
  // 如果已经在回复这条评论，则关闭回复框
  if (replyingTo.value === comment.id) {
    replyingTo.value = null
    replyContent.value = ''
  } else {
    // 否则打开回复框
    replyingTo.value = comment.id
    replyContent.value = ''
  }
}

// 提交回复
const submitReply = async (comment) => {
  if (!replyContent.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    // 发送回复请求
    const response = await fetch(`/comment/${comment.id}/reply/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: replyContent.value
      })
    })
    
    if (!response.ok) {
      throw new Error('回复失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      ElMessage.success('回复成功')
      
      // 获取本地用户信息
      const userInfo = localStorage.getItem('userInfo')
      let userData = { id: 0, username: '当前用户', avatar: currentUserAvatar.value }
      if (userInfo) {
        try {
          userData = JSON.parse(userInfo)
        } catch (e) {}
      }
      
      // 添加新回复
      const newReply = {
        id: Date.now(), // 临时ID
        user: {
          id: userData.id,
          username: userData.username,
          avatar: userData.avatar
        },
        time: new Date().toLocaleString(),
        content: replyContent.value
      }
      
      // 如果评论没有回复数组，则创建一个
      if (!comment.replies) {
        comment.replies = []
      }
      
      comment.replies.push(newReply)
      
      // 清空回复框和关闭回复状态
      replyContent.value = ''
      replyingTo.value = null
    } else {
      throw new Error(result.message || '回复失败')
    }
  } catch (error) {
    console.error('回复失败:', error)
    ElMessage.error('回复失败，请稍后重试')
    
    // 模拟（开发阶段）
    const userInfo = localStorage.getItem('userInfo')
    let userData = { id: 0, username: '当前用户', avatar: currentUserAvatar.value }
    if (userInfo) {
      try {
        userData = JSON.parse(userInfo)
      } catch (e) {}
    }
    
    const newReply = {
      id: Date.now(),
      user: {
        id: userData.id,
        username: userData.username,
        avatar: userData.avatar
      },
      time: new Date().toLocaleString(),
      content: replyContent.value
    }
    
    if (!comment.replies) {
      comment.replies = []
    }
    
    comment.replies.push(newReply)
    replyContent.value = ''
    replyingTo.value = null
    ElMessage.success('回复成功')
  }
}

// 检查评论是否可以删除
const canDeleteComment = (comment) => {
  return comment.user.id === currentUserId.value || kbData.creator.id === currentUserId.value
}

// 确认删除评论
const confirmDeleteComment = (comment) => {
  ElMessageBox.confirm('确定要删除这条评论吗？', '删除评论', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        return
      }
      
      // 删除评论请求
      const response = await fetch(`/user/comment/knowledge-base/${comment.id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error('删除评论失败')
      }
      
      const result = await response.json()
      if (result.code === 200) {
        ElMessage.success('评论已删除')
        
        // 更新本地数据
        const index = kbData.comments.findIndex(c => c.id === comment.id)
        if (index !== -1) {
          kbData.comments.splice(index, 1)
          totalComments.value -= 1
        }
      } else {
        throw new Error(result.message || '删除评论失败')
      }
    } catch (error) {
      console.error('删除评论失败:', error)
      ElMessage.error('操作失败，请稍后重试')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchUserAvatar()
  fetchKnowledgeBaseDetail()
})
</script>

<style scoped>
.kb-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container {
  padding: 20px;
}

.back-button {
  margin-bottom: 20px;
}

.kb-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.kb-avatar {
  flex-shrink: 0;
}

.avatar-placeholder {
  width: 100px;
  height: 100px;
  background-color: #67c23a;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: bold;
  border-radius: 8px;
}

.kb-info {
  flex: 1;
}

.kb-info h1 {
  margin-top: 0;
  margin-bottom: 10px;
}

.kb-creator {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  color: #606266;
}

.creator-name {
  color: #409eff;
  cursor: pointer;
}

.creator-name:hover {
  text-decoration: underline;
}

.kb-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #606266;
}

.kb-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  margin-right: 0;
}

.kb-actions {
  display: flex;
  gap: 10px;
}

.kb-tabs {
  margin-top: 20px;
}

.tab-card {
  margin-bottom: 20px;
}

.tab-card h2 {
  margin-top: 0;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.tab-card h3 {
  margin-top: 30px;
  margin-bottom: 15px;
}

.description {
  line-height: 1.6;
  color: #606266;
}

.scenarios {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
}

.scenario-tag {
  margin-right: 0;
}

/* 文件列表 */
.file-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-box {
  width: 300px;
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 相关智能体 */
.related-agents {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.agent-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.agent-item:hover {
  background-color: #f5f7fa;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.agent-icon {
  width: 50px;
  height: 50px;
  background-color: #409eff;
  color: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
}

.agent-info {
  flex: 1;
}

.agent-info h3 {
  margin-top: 0;
  margin-bottom: 6px;
}

.agent-info p {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
}

.agent-meta {
  display: flex;
  gap: 15px;
  color: #909399;
  font-size: 12px;
}

.agent-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 评论 */
.comment-input {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.input-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.comment-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.comment-list {
  margin-top: 20px;
}

.comment-item {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-username {
  font-weight: bold;
  color: #409eff;
  cursor: pointer;
}

.comment-username:hover {
  text-decoration: underline;
}

.comment-time {
  color: #909399;
  font-size: 12px;
}

.comment-content p {
  margin: 0 0 10px 0;
  color: #606266;
  line-height: 1.6;
}

.comment-actions {
  display: flex;
  gap: 15px;
}

.reply-list {
  margin-top: 15px;
  padding-left: 15px;
  border-left: 2px solid #ebeef5;
}

.reply-item {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #ebeef5;
}

.reply-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.reply-content {
  flex: 1;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.reply-username {
  font-weight: bold;
  color: #409eff;
  cursor: pointer;
}

.reply-username:hover {
  text-decoration: underline;
}

.reply-time {
  color: #909399;
  font-size: 12px;
}

.reply-content p {
  margin: 0;
  color: #606266;
}

.reply-input {
  margin-top: 10px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* 文件预览 */
.file-preview-container {
  width: 100%;
  min-height: 300px;
}

.document-preview {
  background-color: #f8f9fa;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: auto;
  max-height: 70vh;
}

.preview-content {
  padding: 20px;
  line-height: 1.6;
}
</style>
