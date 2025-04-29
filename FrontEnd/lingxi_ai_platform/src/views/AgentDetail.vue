<template>
  <div class="agent-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton style="width: 100%" animated>
        <template #template>
          <div style="padding: 20px">
            <el-skeleton-item variant="image" style="width: 100%; height: 200px" />
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

    <div v-else class="agent-detail">
      <!-- 返回按钮 -->
      <div class="back-button">
        <el-button @click="goBack" text>
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
      </div>

      <!-- 智能体基本信息 -->
      <el-card class="agent-header">
        <div class="header-content">
          <div class="agent-avatar">
            <div class="avatar-placeholder">AI</div>
          </div>
          <div class="agent-info">
            <h1>{{ agentData.name }}</h1>
            <div class="agent-creator">
              <span>创建者:</span>
              <el-avatar :size="24" :src="agentData.creator.avatar" @click="viewUserProfile(agentData.creator.id)" style="cursor: pointer; margin: 0 5px" />
              <span class="creator-name" @click="viewUserProfile(agentData.creator.id)">{{ agentData.creator.username }}</span>
            </div>
            <div class="agent-stats">
              <span class="stat-item"><el-icon><View /></el-icon> {{ agentData.views || 0 }} 浏览</span>
              <span class="stat-item"><el-icon><StarFilled /></el-icon> {{ agentData.likes || 0 }} 点赞</span>
              <span class="stat-item"><el-icon><User /></el-icon> {{ agentData.followers || 0 }} 关注</span>
              <span class="stat-item"><el-icon><ChatDotRound /></el-icon> {{ agentData.comments?.length || 0 }} 评论</span>
            </div>
            <div class="agent-tags" v-if="agentData.tags && agentData.tags.length">
              <el-tag v-for="tag in agentData.tags" :key="tag" size="small" class="tag">{{ tag }}</el-tag>
            </div>
          </div>
          <div class="agent-actions">
            <el-button 
              type="primary" 
              size="large" 
              @click="handleChat"
            >开始对话</el-button>
            <el-button 
              :type="agentData.isFollowed ? 'success' : 'default'" 
              size="large" 
              @click="handleFollow"
            >
              <el-icon><StarFilled /></el-icon> 
              {{ agentData.isFollowed ? '已关注' : '关注' }}
            </el-button>
            <el-dropdown trigger="click">
              <el-button>
                <el-icon><More /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleLike">
                    <el-icon><StarFilled /></el-icon> {{ agentData.isLiked ? '取消点赞' : '点赞' }}
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleShare">
                    <el-icon><Share /></el-icon> 分享
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleFork" v-if="canFork">
                    <el-icon><CopyDocument /></el-icon> 复制/调整
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleReport" divided>
                    <el-icon><Warning /></el-icon> 举报
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-card>

      <!-- 详细内容 -->
      <el-tabs v-model="activeTab" class="agent-tabs">
        <el-tab-pane label="介绍" name="intro">
          <el-card class="tab-card">
            <h2>智能体介绍</h2>
            <div class="description">
              <p>{{ agentData.description || '暂无介绍' }}</p>
            </div>

            <h3>能力与特点</h3>
            <div class="capabilities" v-if="agentData.capabilities && agentData.capabilities.length">
              <div v-for="(cap, index) in agentData.capabilities" :key="index" class="capability-item">
                <div class="capability-icon">
                  <el-icon><Check /></el-icon>
                </div>
                <div>
                  <h4>{{ cap.title }}</h4>
                  <p>{{ cap.description }}</p>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无能力说明" />

            <!-- 适用场景 -->
            <h3>适用场景</h3>
            <div class="scenarios" v-if="agentData.scenarios && agentData.scenarios.length">
              <el-tag v-for="scenario in agentData.scenarios" :key="scenario" size="large" class="scenario-tag">
                {{ scenario }}
              </el-tag>
            </div>
            <el-empty v-else description="暂无场景说明" />
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="使用示例" name="examples">
          <el-card class="tab-card">
            <h2>使用示例</h2>
            <div class="examples" v-if="agentData.examples && agentData.examples.length">
              <el-collapse accordion>
                <el-collapse-item v-for="(example, index) in agentData.examples" :key="index" :title="example.title">
                  <div class="example-content">
                    <h4>示例场景：{{ example.title }}</h4>
                    <div class="chat-example">
                      <div v-for="(message, msgIndex) in example.messages" :key="msgIndex" :class="['message', message.role === 'user' ? 'user-message' : 'agent-message']">
                        <div class="message-avatar">
                          <el-avatar :size="32" :src="message.role === 'user' ? userAvatar : agentAvatar">
                            {{ message.role === 'user' ? 'U' : 'AI' }}
                          </el-avatar>
                        </div>
                        <div class="message-content">
                          <p>{{ message.content }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
            <el-empty v-else description="暂无使用示例" />
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="相关知识库" name="knowledge">
          <el-card class="tab-card">
            <h2>相关知识库</h2>
            <div class="knowledge-bases" v-if="agentData.knowledgeBases && agentData.knowledgeBases.length">
              <div v-for="kb in agentData.knowledgeBases" :key="kb.id" class="kb-item" @click="viewKnowledgeBase(kb.id)">
                <div class="kb-icon">KB</div>
                <div class="kb-info">
                  <h3>{{ kb.name }}</h3>
                  <p>{{ kb.description }}</p>
                  <div class="kb-meta">
                    <span><el-icon><Document /></el-icon> {{ kb.fileCount || 0 }} 文件</span>
                    <span><el-icon><User /></el-icon> {{ kb.followCount || 0 }} 关注者</span>
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
            <el-empty v-else description="暂无相关知识库" />
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
            <div class="comment-list" v-if="agentData.comments && agentData.comments.length">
              <div v-for="comment in agentData.comments" :key="comment.id" class="comment-item">
                <el-avatar :size="40" :src="comment.user.avatar" @click="viewUserProfile(comment.user.id)">{{ comment.user.username.substring(0, 1) }}</el-avatar>
                <div class="comment-content">
                  <div class="comment-header">
                    <span class="comment-username" @click="viewUserProfile(comment.user.id)">{{ comment.user.username }}</span>
                    <span class="comment-time">{{ comment.time }}</span>
                  </div>
                  <p>{{ comment.content }}</p>
                  <div class="comment-actions">
                    <el-button text type="primary" size="small" @click="likeComment(comment)">
                      <el-icon><StarFilled /></el-icon> {{ comment.likes || 0 }}
                    </el-button>
                    <el-button text size="small" @click="replyComment(comment)">
                      <el-icon><ChatLineRound /></el-icon> 回复
                    </el-button>
                  </div>
                  
                  <!-- 回复列表 -->
                  <div class="reply-list" v-if="comment.replies && comment.replies.length">
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
                  </div>
                  
                  <!-- 回复输入框 -->
                  <div class="reply-input" v-if="replyingTo === comment.id">
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
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无评论，快来发表第一条评论吧" />

            <!-- 分页 -->
            <div class="pagination" v-if="agentData.comments && agentData.comments.length > 10">
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                layout="prev, pager, next"
                :total="totalComments"
                @current-change="handlePageChange"
              />
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  StarFilled, 
  View, 
  ChatDotRound, 
  User, 
  ArrowLeft, 
  More, 
  Share, 
  CopyDocument, 
  Warning, 
  Check, 
  Document,
  ChatLineRound 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const activeTab = ref('intro')
const agentId = computed(() => route.params.id as string)
const commentContent = ref('')
const replyContent = ref('')
const replyingTo = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)
const totalComments = ref(0)

// 用户头像
const currentUserAvatar = ref('')
const userAvatar = ref('https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png')
const agentAvatar = ref('')

// 智能体数据
const agentData = reactive({
  id: '',
  name: '',
  description: '',
  creator: {
    id: 0,
    username: '',
    avatar: ''
  },
  views: 0,
  likes: 0,
  followers: 0,
  isFollowed: false,
  isLiked: false,
  tags: [] as string[],
  capabilities: [] as { title: string; description: string }[],
  scenarios: [] as string[],
  examples: [] as {
    title: string;
    messages: { role: 'user' | 'agent'; content: string }[];
  }[],
  knowledgeBases: [] as {
    id: string;
    name: string;
    description: string;
    fileCount: number;
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
    replies: {
      id: number;
      user: {
        id: number;
        username: string;
        avatar: string;
      };
      time: string;
      content: string;
    }[];
  }[]
})

// 检查是否可以复制/调整智能体
const canFork = computed(() => {
  return agentData.creator.id !== getCurrentUserId()
})

// 获取当前登录用户ID
const getCurrentUserId = () => {
  const userInfo = localStorage.getItem('userInfo')
  if (userInfo) {
    try {
      return JSON.parse(userInfo).id || 0
    } catch (e) {
      return 0
    }
  }
  return 0
}

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

// 获取智能体详情
const fetchAgentDetail = async () => {
  loading.value = true
  
  try {
    const token = localStorage.getItem('token')
    
    // 构建API请求
    const response = await fetch(`/agent/${agentId.value}/detail/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    })
    
    if (!response.ok) {
      throw new Error('获取智能体详情失败')
    }
    
    const data = await response.json()
    if (data.code === 200) {
      // 更新智能体数据
      Object.assign(agentData, data.data)
      agentAvatar.value = data.data.avatar || ''
    } else {
      throw new Error(data.message || '获取智能体详情失败')
    }
  } catch (error) {
    console.error('获取智能体详情失败:', error)
    ElMessage.error('获取智能体详情失败，请稍后重试')
    
    // 模拟数据（开发阶段）
    setTimeout(() => {
      Object.assign(agentData, {
        id: agentId.value,
        name: '英语学习助手',
        description: '这是一个智能英语学习助手，能够帮助用户学习英语语法、口语、听力和阅读，提供个性化的学习计划和反馈。支持多种学习场景，适合各个年龄段和不同英语水平的用户。',
        creator: {
          id: 101,
          username: '语言学习专家',
          avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
        },
        views: 1520,
        likes: 328,
        followers: 156,
        isFollowed: false,
        isLiked: false,
        tags: ['英语学习', '教育', '外语', '智能辅导'],
        capabilities: [
          {
            title: '语法讲解与练习',
            description: '根据用户的英语水平，提供相应的语法知识讲解和针对性练习'
          },
          {
            title: '口语对话练习',
            description: '模拟各种生活场景的对话，帮助用户提高口语表达能力'
          },
          {
            title: '听力理解训练',
            description: '提供多种难度的听力材料，并进行理解测试和解析'
          },
          {
            title: '阅读能力提升',
            description: '根据用户兴趣推荐适合的阅读材料，并进行阅读理解辅导'
          },
          {
            title: '个性化学习计划',
            description: '根据用户的学习目标和进度，制定个性化的学习计划'
          }
        ],
        scenarios: ['日常英语学习', '出国旅游准备', '商务英语提升', '学术英语写作', '考试备考辅导'],
        examples: [
          {
            title: '语法学习示例',
            messages: [
              { role: 'user', content: '我总是搞不清楚when和while的用法区别，能解释一下吗？' },
              { role: 'agent', content: 'when和while都用于引导时间状语从句，但用法有区别：\n\n1. when通常表示"在...时候"，强调某一时刻或时间点发生的动作。\n例如：When I arrived home, he was watching TV.\n\n2. while通常表示"在...期间"，强调持续一段时间的动作。\n例如：While I was cooking dinner, she was doing homework.\n\n你想要我提供更多例句来练习吗？' },
              { role: 'user', content: '是的，请给我一些例句做练习。' },
              { role: 'agent', content: '好的，以下是一些使用when和while的例句，请尝试辨别它们的区别：\n\n1. _____ I was walking in the park, I saw an old friend.\n2. The phone rang _____ we were having dinner.\n3. _____ I opened the door, the cat ran out.\n4. She fell asleep _____ reading a book.\n5. He called me _____ I was about to leave.\n\n请填写适当的连词(when或while)，然后我会给你答案和解释。' }
            ]
          },
          {
            title: '口语练习示例',
            messages: [
              { role: 'user', content: '我下周要去美国旅游，可以帮我练习一下在餐厅点餐的对话吗？' },
              { role: 'agent', content: '当然可以！我们来模拟一下在美国餐厅点餐的场景。我会扮演服务员，你扮演顾客。\n\n服务员：Hi there! Welcome to Riverside Grill. My name is Sarah, I\'ll be your server today. Can I start you off with something to drink?\n\n请你回应这个开场白，可以点饮料。' },
              { role: 'user', content: 'Hi Sarah, nice to meet you. I\'d like a glass of iced tea, please.' },
              { role: 'agent', content: '服务员：Sure thing, one iced tea coming up. Are you ready to order or do you need a few more minutes with the menu?\n\n(现在你可以选择点餐或要求更多时间)' }
            ]
          }
        ],
        knowledgeBases: [
          {
            id: 'kb1',
            name: '英语语法大全',
            description: '包含英语各级别语法知识点、例句和练习',
            fileCount: 28,
            followCount: 86,
            isFollowed: false
          },
          {
            id: 'kb2',
            name: '商务英语词汇',
            description: '涵盖商务谈判、邮件写作等场景的专业词汇',
            fileCount: 15,
            followCount: 42,
            isFollowed: false
          }
        ],
        comments: [
          {
            id: 1,
            user: {
              id: 201,
              username: '英语学习者',
              avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
            },
            time: '2025-05-02 15:30',
            content: '这个智能体非常好用，帮我解决了很多语法问题，特别是对过去完成时的讲解非常清晰。',
            likes: 12,
            replies: [
              {
                id: 101,
                user: {
                  id: 101,
                  username: '语言学习专家',
                  avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
                },
                time: '2025-05-02 16:15',
                content: '谢谢你的反馈！我会持续更新和完善内容。'
              }
            ]
          },
          {
            id: 2,
            user: {
              id: 202,
              username: '出国准备中',
              avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
            },
            time: '2025-05-01 10:20',
            content: '口语对话练习功能很棒，模拟了很多实际场景，对提高我的口语有很大帮助。',
            likes: 8,
            replies: []
          }
        ]
      })
      totalComments.value = agentData.comments.length
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

// 查看知识库
const viewKnowledgeBase = (kbId) => {
  router.push(`/knowledge-base/${kbId}`)
}

// 关注智能体
const handleFollow = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const isFollowed = agentData.isFollowed
    
    // 关注/取消关注请求
    const response = await fetch(`/agent/${agentId.value}/follow/`, {
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
      agentData.isFollowed = !isFollowed
      agentData.followers = isFollowed ? agentData.followers - 1 : agentData.followers + 1
      
      ElMessage.success(isFollowed ? '已取消关注' : '关注成功')
    } else {
      throw new Error(result.message || (isFollowed ? '取消关注失败' : '关注失败'))
    }
  } catch (error) {
    console.error('关注操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
    
    // 模拟（开发阶段）
    agentData.isFollowed = !agentData.isFollowed
    agentData.followers = agentData.isFollowed ? agentData.followers + 1 : agentData.followers - 1
    ElMessage.success(agentData.isFollowed ? '关注成功' : '已取消关注')
  }
}

// 点赞智能体
const handleLike = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const isLiked = agentData.isLiked
    
    // 点赞/取消点赞请求
    const response = await fetch(`/agent/${agentId.value}/like/`, {
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
      agentData.isLiked = !isLiked
      agentData.likes = isLiked ? agentData.likes - 1 : agentData.likes + 1
      
      ElMessage.success(isLiked ? '已取消点赞' : '点赞成功')
    } else {
      throw new Error(result.message || (isLiked ? '取消点赞失败' : '点赞失败'))
    }
  } catch (error) {
    console.error('点赞操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
    
    // 模拟（开发阶段）
    agentData.isLiked = !agentData.isLiked
    agentData.likes = agentData.isLiked ? agentData.likes + 1 : agentData.likes - 1
    ElMessage.success(agentData.isLiked ? '点赞成功' : '已取消点赞')
  }
}

// 开始对话
const handleChat = () => {
  // 将智能体信息存储到localStorage
  const chatAgentInfo = {
    id: agentData.id,
    name: agentData.name,
    description: agentData.description,
    avatar: agentAvatar.value
  }
  localStorage.setItem('currentChatAgent', JSON.stringify(chatAgentInfo))
  
  // 跳转到聊天页面
  router.push('/chat')
}

// 分享智能体
const handleShare = () => {
  const shareUrl = `${window.location.origin}/#/agent-detail/${agentId.value}`
  
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

// 复制/调整智能体
const handleFork = () => {
  ElMessageBox.confirm('确定要复制这个智能体并进行调整吗？', '复制智能体', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(() => {
    // 保存智能体信息到本地存储，用于创建新智能体
    localStorage.setItem('forkAgent', JSON.stringify({
      sourceId: agentData.id,
      name: `${agentData.name} - 我的版本`,
      description: agentData.description,
      capabilities: agentData.capabilities,
      scenarios: agentData.scenarios,
      tags: agentData.tags,
      knowledgeBases: agentData.knowledgeBases
    }))
    
    // 跳转到智能体编辑器
    router.push('/agent-editor')
  }).catch(() => {})
}

// 举报智能体
const handleReport = () => {
  ElMessageBox.prompt('请输入举报原因', '举报智能体', {
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
    const response = await fetch(`/agent/${agentId.value}/comment/`, {
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
        id: Date.now(), // 临时ID
        user: {
          id: userData.id,
          username: userData.username,
          avatar: userData.avatar
        },
        time: new Date().toLocaleString(),
        content: commentContent.value,
        likes: 0,
        replies: []
      }
      
      agentData.comments.unshift(newComment)
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
      replies: []
    }
    
    agentData.comments.unshift(newComment)
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
    
    // 点赞评论请求
    const response = await fetch(`/comment/${comment.id}/like/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error('点赞失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      comment.likes += 1
      ElMessage.success('点赞成功')
    } else {
      throw new Error(result.message || '点赞失败')
    }
  } catch (error) {
    console.error('点赞评论失败:', error)
    ElMessage.error('操作失败，请稍后重试')
    
    // 模拟（开发阶段）
    comment.likes += 1
    ElMessage.success('点赞成功')
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
    const response = await fetch(`/knowledge-base/${kb.id}/follow/`, {
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
    
    // 模拟（开发阶段）
    kb.isFollowed = !kb.isFollowed
    kb.followCount = kb.isFollowed ? kb.followCount + 1 : kb.followCount - 1
    ElMessage.success(kb.isFollowed ? '关注知识库成功' : '已取消关注知识库')
  }
}

// 处理评论分页
const handlePageChange = (page) => {
  currentPage.value = page
  // 实际项目中应该加载指定页的评论
  // 这里仅作示例，不做实际处理
}

onMounted(() => {
  fetchUserAvatar()
  fetchAgentDetail()
})
</script>

<style scoped>
.agent-detail-container {
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

.agent-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.agent-avatar {
  flex-shrink: 0;
}

.avatar-placeholder {
  width: 100px;
  height: 100px;
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: bold;
  border-radius: 8px;
}

.agent-info {
  flex: 1;
}

.agent-info h1 {
  margin-top: 0;
  margin-bottom: 10px;
}

.agent-creator {
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

.agent-stats {
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

.agent-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  margin-right: 0;
}

.agent-actions {
  display: flex;
  gap: 10px;
}

.agent-tabs {
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

.capabilities {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.capability-item {
  display: flex;
  gap: 10px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.capability-icon {
  width: 24px;
  height: 24px;
  background-color: #67c23a;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.capability-item h4 {
  margin-top: 0;
  margin-bottom: 6px;
}

.capability-item p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.scenarios {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.scenario-tag {
  margin-right: 0;
}

.examples {
  margin-top: 20px;
}

.example-content {
  padding: 10px;
}

.example-content h4 {
  margin-top: 0;
  margin-bottom: 15px;
}

.chat-example {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 15px;
  background-color: #f8f9fa;
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.message:last-child {
  margin-bottom: 0;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  padding: 10px 15px;
  border-radius: 4px;
  max-width: 80%;
}

.message-content p {
  margin: 0;
  white-space: pre-line;
}

.user-message .message-content {
  background-color: #ecf5ff;
  border: 1px solid #d9ecff;
}

.agent-message .message-content {
  background-color: #f0f9eb;
  border: 1px solid #e1f3d8;
}

.knowledge-bases {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.kb-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.kb-item:hover {
  background-color: #f5f7fa;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.kb-icon {
  width: 50px;
  height: 50px;
  background-color: #67c23a;
  color: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
}

.kb-info {
  flex: 1;
}

.kb-info h3 {
  margin-top: 0;
  margin-bottom: 6px;
}

.kb-info p {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
}

.kb-meta {
  display: flex;
  gap: 15px;
  color: #909399;
  font-size: 12px;
}

.kb-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

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
</style>
