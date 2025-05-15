<template>
  <div class="agent-editor-container">
    <!-- 主要内容区域 -->
    <div class="editor-main">
      <!-- 右侧内容区域 -->
      <div class="editor-content">
        <!-- 预览与调试 -->
        <div class="step-content">
          <h3>开始对话</h3>
          
          <div class="preview-container">
            <div class="chat-preview">
              <div class="chat-header">
                <h4>对话预览</h4>
                <el-button icon="Refresh" circle @click="resetChat"></el-button>
              </div>
              
              <div class="chat-messages" ref="chatMessagesRef">
                <div
                  v-for="(message, index) in chatMessages"
                  :key="index"
                  :class="['message', message.role === 'user' ? 'user-message' : 'bot-message']"
                >
                  <div class="message-avatar">
                    <el-avatar :size="36" :src="message.role === 'user' ? userAvatar : (agentData.avatar ? agentData.avatar : defaultAgentAvatar)"></el-avatar>
                    <div v-if="message.role === 'assistant'" class="output-port-name">{{ message.nodeName || 'output' }}</div>
                  </div>
                  <div class="message-content">
                    <div class="message-text" v-html="formatMessage(message.content)"></div>
                    <div class="message-time">{{ message.time }}</div>
                  </div>
                </div>
                <div v-if="isGenerating" class="bot-message message">
                  <div class="message-avatar">
                    <el-avatar :size="36" :src="defaultAgentAvatar"></el-avatar>
                    <div class="output-port-name">{{ currentNodeName || 'output' }}</div>
                  </div>
                  <div class="message-content">
                    <div class="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 输入区域容器 -->
              <div class="input-container">
                <div v-if="waitingForDynamicInput" class="dynamic-input-indicator">
                  <div class="dynamic-input-tag">
                    <el-icon><Edit /></el-icon>
                    <span>等待输入：{{ dynamicInputName }}</span>
                  </div>
                </div>
                <div class="chat-input">
                  <el-input
                    v-model="userInput"
                    type="textarea"
                    :rows="3"
                    :placeholder="waitingForDynamicInput ? `请输入${dynamicInputVars.join('、')}` : '请输入消息...'"
                    :disabled="isGenerating"
                    @keydown.enter.prevent="handleInput"
                  ></el-input>
                  <el-button
                    type="primary"
                    icon="Position"
                    :disabled="!userInput.trim() || isGenerating"
                    :class="{ 'dynamic-input-button': waitingForDynamicInput }"
                    @click="handleInput"
                  >
                    发送
                  </el-button>
                </div>
              </div>
            </div>
            
            <!-- 静态输入区域（移到右侧） -->
            <div v-if="staticInputs.length > 0" class="static-inputs-panel">
              <div class="static-inputs-header">
                <h4>静态输入</h4>
                <el-button 
                  type="primary" 
                  size="small"
                  :disabled="!hasStaticInputValues"
                  @click="handleSendStaticInputs"
                >
                  发送所有静态输入
                </el-button>
              </div>
              <div class="static-inputs-content">
                <div v-for="(input, index) in staticInputs" :key="index" class="static-input-item">
                  <div class="static-input-label">{{ input.name }}</div>
                  <el-input
                    v-model="input.value"
                    type="textarea"
                    :rows="2"
                    :placeholder="`请输入${input.name}`"
                  ></el-input>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 知识库详情对话框 -->
    <el-dialog
      v-model="knowledgeBaseDetailVisible"
      :title="`知识库详情: ${currentKnowledgeBase.name || ''}`"
      width="650px"
    >
      <el-skeleton :rows="6" animated v-if="loadingDetail" />
      
      <div v-else class="kb-detail-container">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="类型">
            {{ currentKnowledgeBase.type === 'text' ? '文本知识库' : '图片知识库' }}
          </el-descriptions-item>
          <el-descriptions-item label="描述">
            {{ currentKnowledgeBase.description || '无描述' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ currentKnowledgeBase.createdAt }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentKnowledgeBase.status === 'ready' ? 'success' : 'warning'">
              {{ currentKnowledgeBase.status === 'ready' ? '已就绪' : '处理中' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="kb-files">
          <h4>文件列表</h4>
          <div v-if="knowledgeBaseFiles.length === 0" class="empty-files">
            <el-empty description="暂无文件" />
          </div>
          <el-table v-else :data="knowledgeBaseFiles" style="width: 100%">
            <el-table-column prop="filename" label="文件名" />
            <el-table-column label="大小">
              <template #default="scope">
                {{ Math.round(scope.row.size / 1024) }} KB
              </template>
            </el-table-column>
            <el-table-column prop="upload_time" label="上传时间" />
            <el-table-column label="状态">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'processed' ? 'success' : 'warning'">
                  {{ scope.row.status === 'processed' ? '已处理' : '处理中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button link type="primary" size="small" @click="previewFile(scope.row)">
                  预览
                </el-button>
                <el-button link type="danger" size="small" @click="deleteFile(scope.row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 文件预览对话框 -->
    <el-dialog
      v-model="filePreviewVisible"
      :title="`文件预览: ${currentPreviewFile?.filename || ''}`"
      width="700px"
    >
      <el-skeleton :rows="15" animated v-if="previewLoading" />
      
      <div v-else-if="previewContent" class="file-preview">
        <pre>{{ previewContent }}</pre>
      </div>
      
      <div v-else class="empty-preview">
        <el-empty description="无法预览文件内容" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, onMounted, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import KnowledgeBaseConfig from '@/views/KnowledgeBaseConfig.vue'
import WorkflowList from '@/views/WorkflowList.vue'
import { Plus, Edit } from '@element-plus/icons-vue'

// 定义接口
interface AgentData {
  id: string;
  name: string;
  description: string;
  modelId: string;
  modelParams: {
    temperature: number;
    maxTokens: number;
    topP: number;
  };
  avatar: string;
  knowledgeBases: string[];
  workflowId: string;
}

interface ChatMessage {
  role: string;
  content: string;
  time: string;
  nodeName?: string;
}

interface ModelLog {
  time: string;
  type: string;
  message: string;
}

interface AvailableModel {
  id: string;
  name: string;
  icon: string;
  description: string;
  features: string[];
}

interface KnowledgeBase {
  id: string;
  name: string;
  type: string;
  description: string;
  createdAt: string;
  status: string;
  fileCount: number;
  totalSize: number;
  lastUpdated: string;
  userId: string;
}

interface KnowledgeBaseFile {
  id: string;
  filename: string;
  size: number;
  upload_time: string;
  status: string;
}

interface StaticInput {
  name: string;
  value: string;
}

const router = useRouter()
const route = useRoute()

// 基础数据
const activeStep = ref(0)
const isPublished = ref(false)
const debugTab = ref('request')
const chatMessagesRef = ref<HTMLElement | null>(null)

// 聊天预览相关
const userInput = ref('')
const isGenerating = ref(false)
const userAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
const defaultAgentAvatar = 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png'
const chatMessages = ref<ChatMessage[]>([])
const lastRequest = ref<Record<string, any>>({})
const lastResponse = ref<Record<string, any>>({})
const modelLogs = ref<ModelLog[]>([])

const avatarInput = ref<HTMLInputElement | null>(null)

// 智能体数据
const agentData = reactive<AgentData>({
  id: '',
  name: '',
  description: '',
  modelId: '',
  modelParams: {
    temperature: 0.7,
    maxTokens: 1024,
    topP: 0.95
  },
  avatar: '',
  knowledgeBases: [],
  workflowId: ''
})

// 可选模型列表
const availableModels = ref<AvailableModel[]>([
  {
    id: 'gpt-4',
    name: 'GPT-4',
    icon: 'https://cdn-icons-png.flaticon.com/512/4616/4616734.png',
    description: '最强大的多模态大语言模型，支持图像理解、复杂推理',
    features: ['文本处理', '图像理解', '复杂推理', '代码生成']
  },
  {
    id: 'claude-3',
    name: 'Claude 3',
    icon: 'https://cdn-icons-png.flaticon.com/512/8090/8090397.png',
    description: '强大的大语言模型，擅长文本处理和推理',
    features: ['文本处理', '复杂推理', '长文本处理']
  },
  {
    id: 'llama-3',
    name: 'LLaMA 3',
    icon: 'https://cdn-icons-png.flaticon.com/512/6295/6295417.png',
    description: '开源大语言模型，平衡性能和资源消耗',
    features: ['文本处理', '轻量级', '本地部署']
  },
  {
    id: 'qwen-max',
    name: '通义千问',
    icon: 'https://cdn-icons-png.flaticon.com/512/5968/5968282.png',
    description: '国产强大大语言模型，支持中英双语优化',
    features: ['中文优化', '文本处理', '知识丰富']
  }
])

// 知识库详情相关
const knowledgeBaseDetailVisible = ref(false)
const currentKnowledgeBase = ref<KnowledgeBase>({
  id: '',
  name: '',
  type: '',
  description: '', 
  createdAt: '',
  status: '',
  fileCount: 0,
  totalSize: 0,
  lastUpdated: '',
  userId: ''
})
const knowledgeBaseFiles = ref<KnowledgeBaseFile[]>([])
const loadingDetail = ref(false)

// 文件预览相关状态
const filePreviewVisible = ref(false)
const currentPreviewFile = ref<KnowledgeBaseFile | null>(null)
const previewContent = ref('')
const previewLoading = ref(false)

// 知识库列表相关
const knowledgeBases = ref<KnowledgeBase[]>([])
const selectedKnowledgeBases = ref<string[]>([])

// 静态输入相关
const staticInputs = ref<StaticInput[]>([])

// 动态输入相关
const waitingForDynamicInput = ref(false)
const dynamicInputVars = ref<string[]>([])
const dynamicInputName = ref('')

// 在 script setup 部分添加新的接口和状态
const nodeOutputs = ref<Record<string, any>>({})

// 在 script setup 部分添加新的状态变量
const currentNodeName = ref('')

// 在 script setup 部分添加新的状态变量
const ws = ref<WebSocket | null>(null)
const wsReconnectAttempts = ref(0)
const maxReconnectAttempts = 5
const reconnectDelay = 3000 // 3秒

// 计算是否有静态输入值
const hasStaticInputValues = computed(() => {
  return staticInputs.value.some(input => input.value.trim() !== '')
})

// 发送所有静态输入
const handleSendStaticInputs = async () => {
  if (!hasStaticInputValues.value) return
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const response = await fetch(`/agent/staticInput/${agentData.workflowId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        workflowId: agentData.workflowId,
        inputs: staticInputs.value.map(input => ({
          name: input.name,
          value: input.value
        }))
      })
    })
    
    const result = await response.json()
    
    // 检查响应状态
    if (response.ok && result.status === 'ok') {
      ElMessage.success('静态输入发送成功')
      // 清空所有静态输入
      staticInputs.value.forEach(input => {
        input.value = ''
      })
    } else {
      throw new Error(result.message || '工作流执行失败')
    }
  } catch (error) {
    console.error('发送静态输入失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '工作流执行失败')
  }
}

// 监听步骤变化，当切换到知识库配置步骤时获取最新数据
watch(activeStep, (newStep) => {
  if (newStep === 2) { // 2是知识库配置的步骤索引
    // 当进入知识库配置步骤时，触发获取知识库列表
    console.log('进入知识库配置步骤，刷新知识库列表')
  }
})

// 导航功能
const goBack = () => {
  // 离开前保存数据
  saveToLocalStorage()
  router.push('/community')
}

// 将所有数据保存到本地存储
const saveToLocalStorage = (): void => {
  // 保存完整的 agentData 对象
  localStorage.setItem('agentData', JSON.stringify({
    id: agentData.id,
    name: agentData.name,
    description: agentData.description,
    modelId: agentData.modelId,
    modelParams: agentData.modelParams,
    avatar: agentData.avatar,
    knowledgeBases: agentData.knowledgeBases,
    workflowId: agentData.workflowId,
    activeStep: activeStep.value
  }))
  
  console.log('所有数据已保存到本地存储:', agentData)
}

// 从本地存储恢复所有数据
const restoreFromLocalStorage = (): void => {
  console.log('从本地存储恢复数据')
  
  // 恢复agentData
  const storedAgentData = localStorage.getItem('agentData')
  
  if (storedAgentData) {
    try {
      const parsedData = JSON.parse(storedAgentData)
      
      // 基本信息
      if (parsedData.id) agentData.id = parsedData.id
      if (parsedData.name) agentData.name = parsedData.name
      if (parsedData.description) agentData.description = parsedData.description
      if (parsedData.avatar) agentData.avatar = parsedData.avatar
      // 恢复模型选择
      if (parsedData.modelId) agentData.modelId = parsedData.modelId
      
      // 恢复模型参数
      if (parsedData.modelParams) {
        if (parsedData.modelParams.temperature !== undefined) 
          agentData.modelParams.temperature = parsedData.modelParams.temperature
        if (parsedData.modelParams.maxTokens !== undefined) 
          agentData.modelParams.maxTokens = parsedData.modelParams.maxTokens
        if (parsedData.modelParams.topP !== undefined) 
          agentData.modelParams.topP = parsedData.modelParams.topP
      }
      
      // 恢复知识库选择
      if (parsedData.knowledgeBases && Array.isArray(parsedData.knowledgeBases)) {
        agentData.knowledgeBases = parsedData.knowledgeBases
      }
      
      // 恢复工作流选择
      if (parsedData.workflowId) {
        agentData.workflowId = parsedData.workflowId
      }
      if (parsedData.activeStep !== undefined) {
        activeStep.value = parsedData.activeStep
      }

      console.log('从localStorage恢复的数据:', parsedData)
      const selectedWorkflowId = localStorage.getItem('selectedWorkflowId');
      if (selectedWorkflowId && (!agentData.workflowId || agentData.workflowId === '')) {
        agentData.workflowId = selectedWorkflowId;
        console.log('从独立localStorage项恢复工作流ID:', selectedWorkflowId);
      }
    } catch (e) {
      console.error('解析存储的智能体数据失败:', e)
    }
  }
  
  // 同时检查单独保存的数据
  const selectedWorkflowId = localStorage.getItem('selectedWorkflowId')
  if (selectedWorkflowId && !agentData.workflowId) {
    agentData.workflowId = selectedWorkflowId
    console.log('从localStorage恢复工作流ID:', selectedWorkflowId)
  }
  
  const selectedKnowledgeBasesStr = localStorage.getItem('selectedKnowledgeBases')
  if (selectedKnowledgeBasesStr && agentData.knowledgeBases.length === 0) {
    try {
      const selectedKBs = JSON.parse(selectedKnowledgeBasesStr)
      if (Array.isArray(selectedKBs)) {
        agentData.knowledgeBases = selectedKBs
        console.log('从localStorage恢复知识库:', selectedKBs)
      }
    } catch (e) {
      console.error('解析存储的知识库数据失败:', e)
    }
  }
}

// 清除本地存储中的临时数据
const clearLocalStorage = (): void => {
  localStorage.removeItem('agentData')
  localStorage.removeItem('selectedKnowledgeBases')
  localStorage.removeItem('selectedWorkflowId')
  localStorage.removeItem('selectedWorkflowName')
  console.log('本地存储中的临时数据已清除')
}

const getSelectedModelName = (): string => {
  const selectedModel = availableModels.value.find(model => model.id === agentData.modelId)
  return selectedModel ? selectedModel.name : '未知模型'
}

// 步骤控制
const setActiveStep = (step: number) => {
  // 保存当前步骤数据到本地存储
  saveToLocalStorage()
  activeStep.value = step
}

const nextStep = () => {
  // 保存当前步骤数据到本地存储
  saveToLocalStorage() 
  if (activeStep.value < 4) {
    activeStep.value++
  }
}

const prevStep = () => {
  // 保存当前步骤数据到本地存储
  saveToLocalStorage()
  if (activeStep.value > 0) {
    activeStep.value--
  }
}

// 通用模型选择
const selectModel = (model: AvailableModel) => {
  agentData.modelId = model.id
  saveToLocalStorage() // 选择模型后立即保存
}

// 知识库更新回调
const updateKnowledgeBases = (knowledgeBases: string[]) => {
  agentData.knowledgeBases = knowledgeBases
  saveToLocalStorage() // 更新知识库后立即保存
}

// 工作流更新回调
const updateWorkflowId = (workflowId: string) => {
  agentData.workflowId = workflowId
  saveToLocalStorage() // 更新工作流后立即保存
}

// 修改 handleNodeOutput 方法
const handleNodeOutput = (data: { node_name: string, output: any }) => {
  const { node_name, output } = data
  nodeOutputs.value[node_name] = output
  currentNodeName.value = node_name
  
  // 将输出添加到缓冲区
  outputBuffer.value.push({ node_name, output })
  
  // 如果没有正在处理动态输入，则处理缓冲区中的输出
  if (!waitingForDynamicInput.value && !isProcessingOutput.value) {
    processOutputBuffer()
  }
}

// 修改处理输出缓冲区的方法
const processOutputBuffer = () => {
  if (outputBuffer.value.length === 0 || isProcessingOutput.value) return
  
  isProcessingOutput.value = true
  
  while (outputBuffer.value.length > 0) {
    const { node_name, output } = outputBuffer.value.shift()!
    
    // 直接添加新消息，不再检查是否存在相同节点名称的消息
    chatMessages.value.push({
      role: 'assistant',
      content: `${output}`,
      time: new Date().toLocaleTimeString(),
      nodeName: node_name
    })
  }
  
  // 滚动到底部
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
  
  isProcessingOutput.value = false
}

// 修改 handleResponse 方法
const handleResponse = (response: any) => {
  if (response.requiresDynamicInput) {
    // 需要动态输入
    waitingForDynamicInput.value = true
    dynamicInputVars.value = response.requiredVariables
    dynamicInputName.value = response.inputName // 记录输入名称
    // 不添加到聊天记录中
  } else {
    // 检查是否已经存在相同节点名称的消息
    const nodeName = response.nodeName || currentNodeName.value
    const existingMessageIndex = chatMessages.value.findIndex(
      msg => msg.role === 'assistant' && msg.nodeName === nodeName
    )
    
    if (existingMessageIndex === -1) {
      // 如果不存在，则添加新消息
      chatMessages.value.push({
        role: 'assistant',
        content: response.content,
        time: new Date().toLocaleTimeString(),
        nodeName: nodeName
      })
    } else {
      // 如果存在，则更新现有消息
      chatMessages.value[existingMessageIndex].content = response.content
      chatMessages.value[existingMessageIndex].time = new Date().toLocaleTimeString()
    }
  }
}

// 处理输入
const handleInput = async () => {
  if (!userInput.value.trim() || isGenerating.value) return
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    // 添加用户消息到聊天记录
    const userMessage: ChatMessage = {
      role: 'user',
      content: userInput.value,
      time: new Date().toLocaleTimeString()
    }
    chatMessages.value.push(userMessage)
    
    // 清空输入框
    const inputText = userInput.value
    userInput.value = ''
    
    // 滚动到底部
    await nextTick()
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
    
    // 记录请求
    lastRequest.value = {
      messages: [...chatMessages.value.map(m => ({ role: m.role, content: m.content }))],
      model: agentData.modelId,
      params: agentData.modelParams,
      staticInputs: staticInputs.value.map(input => ({
        name: input.name,
        value: input.value
      }))
    }
    
    // 添加日志
    addLog('info', '发送用户消息: ' + inputText)
    
    // 发送消息到dynamicInput
    isGenerating.value = true
    console.log('发送动态输入:', {
      input: dynamicInputName.value,
      variables: inputText
    })
    
    const response = await fetch('/agent/dynamicInput', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        input: dynamicInputName.value,
        variables: inputText
      })
    })
    
    if (!response.ok) {
      throw new Error('发送消息失败')
    }
    
    const result = await response.json()
    console.log('动态输入响应:', result)
    
    // 发送成功后重置动态输入状态
    waitingForDynamicInput.value = false
    dynamicInputVars.value = []
    dynamicInputName.value = ''
    
    // 处理缓冲区中的输出
    processOutputBuffer()
    
    // 检查是否还有其他待处理的动态输入
    const checkNextInputResponse = await fetch('/agent/checkNextInput', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (checkNextInputResponse.ok) {
      const nextInputResult = await checkNextInputResponse.json()
      if (nextInputResult.hasNextInput) {
        // 立即显示下一个动态输入请求
        waitingForDynamicInput.value = true
        dynamicInputName.value = nextInputResult.nextInputName
        dynamicInputVars.value = ['输入']
        ElMessage.info(`请处理下一个动态输入：${nextInputResult.nextInputName}`)
      }
    }
    
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败')
    // 发生错误时也重置状态
    waitingForDynamicInput.value = false
    dynamicInputVars.value = []
    dynamicInputName.value = ''
    // 处理缓冲区中的输出
    processOutputBuffer()
  } finally {
    isGenerating.value = false
  }
}

// 格式化消息（将markdown转为HTML）
const formatMessage = (message: string): string => {
  if (!message) return '';
  
  const html = marked.parse(message, { async: false }) as string;
  return DOMPurify.sanitize(html);
}

// 添加日志
const addLog = (type: string, message: string): void => {
  modelLogs.value.push({
    time: new Date().toLocaleTimeString(),
    type,
    message
  })
}

// 重置聊天
const resetChat = async (): Promise<void> => {
  chatMessages.value = [
    {
      role: 'assistant',
      content: `你好！我是${agentData.name || '智能助手'}。有什么我可以帮助你的吗？`,
      time: new Date().toLocaleTimeString()
    }
  ]
  lastRequest.value = {}
  lastResponse.value = {}
  modelLogs.value = []
  
  // 清空输出缓冲区
  outputBuffer.value = []
  isProcessingOutput.value = false
  
  // 重置动态输入状态
  waitingForDynamicInput.value = false
  dynamicInputVars.value = []
  dynamicInputName.value = ''
  
  // 重新启动预览
  try {
    await startPreview()
    ElMessage.success('聊天记录已重置')
  } catch (error) {
    console.error('重置预览失败:', error)
    ElMessage.error('重置预览失败，请稍后重试')
  }
}

// 预览文件
const previewFile = async (file: KnowledgeBaseFile): Promise<void> => {
  try {
    previewLoading.value = true
    filePreviewVisible.value = true
    currentPreviewFile.value = file
    previewContent.value = ''
    
    const response = await fetch(`/api/knowledgebase/${currentKnowledgeBase.value.id}/file/${file.id}/content`)
    
    if (!response.ok) {
      throw new Error('获取文件内容失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      previewContent.value = result.data.content
    } else {
      throw new Error(result.message || '获取文件内容失败')
    }
  } catch (error) {
    console.error('预览文件失败:', error)
    ElMessage.error('预览文件失败，请稍后重试')
  } finally {
    previewLoading.value = false
  }
}

// 删除知识库文件
const deleteFile = async (file: KnowledgeBaseFile): Promise<void> => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件"${file.filename}"吗？删除后将无法恢复。`,
      '删除文件',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await fetch(`/api/knowledgebase/${currentKnowledgeBase.value.id}/file/${file.id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error('删除文件失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      ElMessage.success('文件删除成功')
      
      // 更新文件列表
      knowledgeBaseFiles.value = knowledgeBaseFiles.value.filter(f => f.id !== file.id)
      
      // 如果删除后文件列表为空，刷新知识库列表
      if (knowledgeBaseFiles.value.length === 0) {
        // 这里应该调用fetchKnowledgeBases函数，但它没有在当前组件中定义
        // 可能需要在KnowledgeBaseConfig组件中实现相应功能
        console.log('文件列表为空，应刷新知识库列表')
      }
    } else {
      throw new Error(result.message || '删除文件失败')
    }
  } catch (error) {
    if (error === 'cancel') return
    
    console.error('删除文件失败:', error)
    ElMessage.error('删除文件失败，请稍后重试')
  }
}

// 删除知识库
const deleteKnowledgeBase = async (kb: KnowledgeBase): Promise<void> => {
  try {
    await ElMessageBox.confirm(
      `确定要删除知识库"${kb.name}"吗？删除后将无法恢复，且将从所有使用该知识库的智能体中移除。`,
      '删除知识库',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await fetch(`/api/knowledgebase/${kb.id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error('删除知识库失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      ElMessage.success('知识库删除成功')
      
      // 更新知识库列表
      knowledgeBases.value = knowledgeBases.value.filter(item => item.id !== kb.id)
      
      // 如果当前选择的知识库被删除，则从选择列表中移除
      selectedKnowledgeBases.value = selectedKnowledgeBases.value.filter(id => id !== kb.id)
      
      // 通知父组件更新
      updateKnowledgeBases(selectedKnowledgeBases.value)
    } else {
      throw new Error(result.message || '删除知识库失败')
    }
  } catch (error) {
    if (error === 'cancel') return
    
    console.error('删除知识库失败:', error)
    ElMessage.error('删除知识库失败，请稍后重试')
  }
}

// 保存草稿
const handleSaveDraft = async (): Promise<void> => {
  try {
    // 检查必填字段
    if (!agentData.name) {
      ElMessage.warning('请填写智能体名称')
      activeStep.value = 0
      return
    }
    
    // 首先保存当前所有数据到本地存储，以便在出错时能恢复
    saveToLocalStorage()
    
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    // 这里实现真正的保存逻辑
    // const response = await fetch('/api/agent/draft', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json',
    //     'Authorization': `Bearer ${token}`
    //   },
    //   body: JSON.stringify(agentData)
    // })
    
    // if (!response.ok) {
    //   throw new Error('保存草稿失败')
    // }
    
    // const result = await response.json()
    
    // if (result.code === 200) {
    //   // 设置返回的ID
    //   if (result.data && result.data.id) {
    //     agentData.id = result.data.id
    //   }
      
    //   ElMessage.success('智能体草稿已保存')
      
    //   // 保存成功后，清除本地存储中的临时数据
    //   clearLocalStorage()
    // } else {
    //   throw new Error(result.message || '保存草稿失败')
    // }
    
    // 仅用于演示
    ElMessage.success('智能体草稿已保存')
  } catch (error) {
    console.error('保存草稿失败:', error)
    ElMessage.error('保存草稿失败，请稍后重试')
  }
}

// 发布智能体
const handlePublish = async (): Promise<void> => {
  try {
    // 验证必填字段
    if (!agentData.name) {
      ElMessage.warning('请填写智能体名称')
      activeStep.value = 0
      return
    }
    
    if (!agentData.modelId) {
      ElMessage.warning('请选择模型')
      activeStep.value = 1
      return
    }

    if (!agentData.workflowId) {
      ElMessage.warning('请选择工作流')
      activeStep.value = 2
      return
    }
    
    // 确认发布
    let confirmMessage = isPublished.value 
      ? '确定要更新智能体吗？' 
      : '确定要发布智能体吗？发布后，其他用户将可以访问您的智能体。';
    
    await ElMessageBox.confirm(
      confirmMessage,
      isPublished.value ? '更新智能体' : '发布智能体',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'info' }
    )
    
    // 同样先保存到本地存储
    saveToLocalStorage()
    
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }

    const publishData = {
      name: agentData.name,
      description: agentData.description,
      modelId: agentData.modelId,
      avatar: agentData.avatar,
      knowledgeBases: agentData.knowledgeBases,
      workflowId: agentData.workflowId,
      modelParams: agentData.modelParams
    }
    
    // 根据是否已发布选择API端点
    const apiUrl = isPublished.value 
      ? `/user/agent/${agentData.id}/update/` 
      : '/user/agent/publish';
    
    // 选择HTTP方法
    const httpMethod = isPublished.value ? 'PUT' : 'POST';
    
    // 发送请求
    const response = await fetch(apiUrl, {
      method: httpMethod,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(publishData)
    })
    
    if (!response.ok) {
      throw new Error(`${isPublished.value ? '更新' : '发布'}智能体失败`)
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      ElMessage.success(`智能体"${agentData.name}"${isPublished.value ? '更新' : '发布'}成功！`)
      clearLocalStorage() // 发布成功后清除本地存储中的临时数据
      router.push('/my-agents')
    } else {
      throw new Error(result.message || `${isPublished.value ? '更新' : '发布'}智能体失败`)
    }

  } catch (error) {
    if (error === 'cancel') return
    
    console.error(`${isPublished.value ? '更新' : '发布'}智能体失败:`, error)
    ElMessage.error(`${isPublished.value ? '更新' : '发布'}智能体失败，请稍后重试`)
  }
}

// 修改获取静态输入配置的方法
const fetchStaticInputs = async () => {
  if (!agentData.workflowId) return
  
  try {
    const response = await fetch(`/agent/staticInputCount/${agentData.workflowId}`)
    if (!response.ok) {
      throw new Error('获取静态输入配置失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      // 根据后端返回的数据结构处理，并按名称排序
      const { node_count, node_names } = result.data
      staticInputs.value = node_names
        .map((name: string) => ({
          name: name,
          value: ''
        }))
        .sort((a: StaticInput, b: StaticInput) => a.name.localeCompare(b.name))
      console.log('获取静态输入配置成功:', staticInputs.value)
    } else {
      throw new Error(result.message || '获取静态输入配置失败')
    }
  } catch (error) {
    console.error('获取静态输入配置失败:', error)
    ElMessage.error('获取静态输入配置失败')
  }
}

// 修改WebSocket连接逻辑
const connectWebSocket = () => {
  try {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/ws/node_output/`
    
    console.log('正在连接WebSocket:', wsUrl)
    
    ws.value = new WebSocket(wsUrl)
    
    ws.value.onopen = () => {
      console.log('WebSocket连接已建立')
      wsReconnectAttempts.value = 0 // 重置重连次数
    }
    
    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('收到WebSocket消息:', data)
        
        if (data.type === 'output') {
          handleNodeOutput(data)
        } else if (data.type === 'request_input') {
          console.log('收到动态输入请求:', data)
          if (data.node_name) {
            waitingForDynamicInput.value = true
            dynamicInputName.value = data.node_name
            dynamicInputVars.value = ['输入']
            console.log('设置动态输入状态:', {
              waitingForDynamicInput: waitingForDynamicInput.value,
              dynamicInputVars: dynamicInputVars.value,
              dynamicInputName: dynamicInputName.value
            })
          } else {
            console.error('动态输入请求缺少节点名称:', data)
            ElMessage.error('动态输入请求格式错误')
          }
        } else {
          console.warn('未知的WebSocket消息类型:', data.type)
        }
      } catch (error) {
        console.error('处理WebSocket消息失败:', error)
        ElMessage.error('处理消息失败，请刷新页面重试')
      }
    }
    
    ws.value.onerror = (error) => {
      console.error('WebSocket连接错误:', error)
      ElMessage.error('WebSocket连接失败，正在尝试重连...')
    }
    
    ws.value.onclose = () => {
      console.log('WebSocket连接已关闭')
      if (wsReconnectAttempts.value < maxReconnectAttempts) {
        wsReconnectAttempts.value++
        console.log(`尝试重连 (${wsReconnectAttempts.value}/${maxReconnectAttempts})...`)
        setTimeout(connectWebSocket, reconnectDelay)
      } else {
        ElMessage.error('WebSocket连接失败，请刷新页面重试')
      }
    }
  } catch (error) {
    console.error('创建WebSocket连接失败:', error)
    ElMessage.error('创建WebSocket连接失败，请刷新页面重试')
  }
}

// 修改 onMounted 函数
onMounted(async () => {
  console.log('AgentEditor 组件已挂载，开始初始化数据')
  connectWebSocket()
  
  // 检查路由参数，判断是否是编辑模式
  const agentId = route.params.id
  
  if (agentId) {
    // 编辑现有智能体
    console.log('编辑模式，智能体ID:', agentId)
    try {
      // 清除本地可能存在的旧数据
      clearLocalStorage()
      
      // 从API加载智能体数据
      await loadAgentData(agentId)
      
      // 设置编辑模式
      isPublished.value = true
    } catch (error) {
      console.error('加载智能体数据失败:', error)
      ElMessage.error('加载智能体数据失败，请重试')
      // 加载失败时跳回列表页
      router.push('/my-agents')
      return
    }
  } else {
    // 检查是否有从 Community 传递过来的初始数据
    const initData = localStorage.getItem('agentInitData')
    
    if (initData) {
      try {
        // 有初始数据，说明是新建智能体
        const parsedInitData = JSON.parse(initData)
        
        // 清除之前可能存在的所有数据
        clearLocalStorage()
        
        // 只使用初始传入的数据
        if (parsedInitData.name) agentData.name = parsedInitData.name
        if (parsedInitData.description) agentData.description = parsedInitData.description
        
        // 清除 initData，防止下次进入页面时重复使用
        localStorage.removeItem('agentInitData')
      } catch (e) {
        console.error('解析初始数据失败:', e)
      }
    } else {
      // 没有初始数据，可能是从其他页面返回
      // 从本地存储恢复所有数据
      restoreFromLocalStorage()
    }
  }
  
  // 监听页面刷新或关闭事件，保存数据
  window.addEventListener('beforeunload', () => {
    saveToLocalStorage()
  })
  
  // 自动获取静态输入配置并启动预览
  await fetchStaticInputs()
  await startPreview()
})

// 添加 loadAgentData 函数
const loadAgentData = async (agentId) => {
  const token = localStorage.getItem('token')
  if (!token) {
    throw new Error('请先登录')
  }

  const response = await fetch(`/user/useAgent/${agentId}/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })

  if (!response.ok) {
    throw new Error(`获取智能体数据失败: ${response.status}`)
  }

  const result = await response.json()

  if (result.code !== 200 || !result.data) {
    throw new Error(result.message || '获取智能体数据失败')
  }

  // 更新状态
  const data = result.data
  
  // 设置基本信息
  agentData.id = data.id
  agentData.name = data.name || ''
  agentData.description = data.description || ''
  agentData.avatar = data.avatar || ''
  
  // 设置模型信息
  agentData.modelId = data.modelId || ''
  
  // 设置模型参数
  if (data.modelParams) {
    agentData.modelParams.temperature = data.modelParams.temperature ?? 0.7
    agentData.modelParams.maxTokens = data.modelParams.maxTokens ?? 1024
    agentData.modelParams.topP = data.modelParams.topP ?? 0.95
  }
  
  // 设置知识库
  agentData.knowledgeBases = data.knowledgeBases || []
  
  // 设置工作流
  agentData.workflowId = data.workflowId || ''
  
  // 确保加载工作流ID后打印日志，便于调试
  console.log('从API加载的工作流ID:', data.workflowId)
  console.log('设置后的工作流ID:', agentData.workflowId)
  
  // 如果从API获取的工作流ID为空，尝试从localStorage获取
  if (!agentData.workflowId) {
    const savedWorkflowId = localStorage.getItem('selectedWorkflowId')
    if (savedWorkflowId) {
      agentData.workflowId = savedWorkflowId
      console.log('从localStorage恢复工作流ID:', savedWorkflowId)
    }
  }
  
  console.log('智能体数据加载成功:', agentData)
}

// 在组件卸载时关闭WebSocket连接
onBeforeUnmount(() => {
  if (ws.value) {
    ws.value.close()
    ws.value = null
  }
})

// 添加页面离开守卫
onBeforeRouteLeave((to, from, next) => {
  console.log("页面离开");
  if (to.path !== '/create-ai' && agentData.avatar && agentData.avatar.includes('temp_') && !isPublished.value) {
    console.log("to.path :", to.path);
    //cleanupTempResources();
  }
  else {
    console.log("to.path :", to.path);
  }
  next();
})

// 添加浏览器关闭/刷新前的事件处理
onMounted(() => {
  window.addEventListener('beforeunload', (event) => {
    if (!isPublished.value && agentData.avatar) {
      //cleanupTempResources()
      // 现代浏览器通常需要返回值来显示确认对话框
      event.preventDefault()
      event.returnValue = ''
    }
  })
})

// 触发文件选择器
const triggerAvatarUpload = () => {
  avatarInput.value?.click()
}

// 处理头像选择变化
const handleAvatarChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  
  if (!files || files.length === 0) return
  
  const file = files[0]
  
  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请上传图片文件')
    return
  }
  
  // 检查文件大小（限制为2MB）
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过2MB')
    return
  }
  
  try {
    // 先创建一个临时预览URL
    const previewUrl = URL.createObjectURL(file)
    agentData.avatar = previewUrl
    
    const formData = new FormData()
    formData.append('avatar', file)
    
    // 如果agent已有ID，也发送ID
    if (agentData.id) {
      formData.append('agent_id', agentData.id)
    }
    
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const response = await fetch('/agent/upload_avatar', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('上传失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      // 用服务器返回的URL替换临时URL
      agentData.avatar = result.data.avatar
      ElMessage.success('头像上传成功')
      // 释放临时URL
      URL.revokeObjectURL(previewUrl)
      
      // 保存到本地存储
      saveToLocalStorage()
    } else {
      throw new Error(result.message || '上传失败')
    }
  } catch (error) {
    console.error('头像上传失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '头像上传失败')
  } finally {
    // 清空文件输入，允许重新选择同一文件
    target.value = ''
  }
}

// 在 script setup 部分添加新的函数
const startPreview = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }

    const response = await fetch('/agent/start_preview', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        agent_id: agentData.id,
        workflow_id: agentData.workflowId,
        model_id: agentData.modelId,
        knowledge_bases: agentData.knowledgeBases
      })
    })

    if (!response.ok) {
      throw new Error('启动预览失败')
    }
  } catch (error) {
    console.error('启动预览失败:', error)
    ElMessage.error('启动预览失败，请稍后重试')
  }
}

// 在AgentEditor.vue中添加清理临时资源的方法
const cleanupTempResources = async () => {
  try {
    // 检查是否有临时头像需要清理
    if (agentData.avatar && agentData.avatar.includes('temp_')) {
      const token = localStorage.getItem('token')
      if (!token) return
      

      const response = await fetch('/agent/cleanup_temp_resources', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          temp_avatar: agentData.avatar,
          agent_id: agentData.id || null
        })
      })

      if (!response.ok || response.status !== 200) {
        throw new Error('清理临时资源失败')
      }
      
      console.log('清理临时资源成功')
    }
  } catch (error) {
    console.error('清理临时资源失败:', error)
  }
}

// 在 script setup 部分添加新的状态变量
const outputBuffer = ref<Array<{ node_name: string, output: any }>>([])
const isProcessingOutput = ref(false)
</script>

<style scoped>
.agent-editor-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 主内容区域样式 */
.editor-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 内容区域样式 */
.editor-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.step-content {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  height: calc(100vh - 40px);
}

.preview-container {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
  height: 500px;
}

.chat-preview {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #fff;
}

.chat-header {
  padding: 10px 16px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h4 {
  margin: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px 8px 0 0;
}

.message {
  display: flex;
  margin-bottom: 16px;
  animation: messageFadeIn 0.3s ease-out;
}

@keyframes messageFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  margin: 0 8px;
}

.output-port-name {
  font-size: 12px;
  color: #909399;
  text-align: center;
}

.message-content {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.bot-message .message-content {
  background-color: #ecf5ff;
  border: 1px solid #d9ecff;
}

.user-message .message-content {
  background-color: #fff;
  border: 1px solid #ebeef5;
}

.message-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.message-time {
  font-size: 12px;
  color: #909399;
  text-align: right;
  margin-top: 4px;
}

.chat-input {
  padding: 16px;
  display: flex;
  gap: 12px;
  background-color: #f5f7fa;
  border-radius: 0 0 8px 8px;
}

.chat-input .el-input {
  flex: 1;
}

.chat-input .el-input :deep(.el-textarea__inner) {
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  background-color: #fff;
  transition: all 0.3s;
  padding: 12px;
  font-size: 14px;
  line-height: 1.5;
}

.chat-input .el-input :deep(.el-textarea__inner:focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.chat-input .el-input :deep(.el-textarea__inner:hover) {
  border-color: #c0c4cc;
}

.chat-input .el-input :deep(.el-textarea__inner:focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.chat-input .el-input :deep(.el-textarea__inner:hover) {
  border-color: #c0c4cc;
}

.dynamic-input-button {
  background-color: #67c23a !important;
  border-color: #67c23a !important;
  transition: all 0.3s;
}

.dynamic-input-button:hover {
  background-color: #85ce61 !important;
  border-color: #85ce61 !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.2);
}

.dynamic-input-button:active {
  transform: translateY(0);
  box-shadow: none;
}

.typing-indicator {
  display: inline-flex;
  align-items: center;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  margin: 0 2px;
  background-color: #606266;
  border-radius: 50%;
  display: inline-block;
  opacity: 0.4;
  animation: typing 1.4s infinite both;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0% { transform: translateY(0px); opacity: 0.4; }
  50% { transform: translateY(-5px); opacity: 0.8; }
  100% { transform: translateY(0px); opacity: 0.4; }
}

.debug-panel {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.debug-panel h4 {
  margin: 0;
  padding: 10px 16px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.debug-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  font-family: monospace;
  font-size: 13px;
  background-color: #f8f9fb;
}

.debug-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.logs {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-item {
  font-family: monospace;
  font-size: 12px;
  line-height: 1.5;
}

.log-time {
  color: #909399;
  margin-right: 8px;
}

.log-type {
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 8px;
  font-weight: bold;
}

.log-type-info {
  background-color: #ecf5ff;
  color: #409eff;
}

.log-type-success {
  background-color: #f0f9eb;
  color: #67c23a;
}

.log-type-warning {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.log-type-error {
  background-color: #fef0f0;
  color: #f56c6c;
}

/* 知识库详情和文件预览样式 */
.kb-detail-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.kb-files {
  margin-top: 10px;
}

.kb-files h4 {
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 500;
}

.empty-files {
  padding: 20px;
  text-align: center;
  color: #909399;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.file-preview {
  max-height: 400px;
  overflow-y: auto;
}

.file-preview pre {
  white-space: pre-wrap;
  word-break: break-word;
  padding: 16px;
  background-color: #f8f8f8;
  border-radius: 4px;
  margin: 0;
  font-family: monospace;
}

.empty-preview {
  padding: 40px 0;
  text-align: center;
}

/* 新的动态输入指示器样式 */
.dynamic-input-indicator {
  padding: 8px 16px;
  background-color: #f0f9eb;
  border-bottom: 1px solid #e1f3d8;
  animation: slideDown 0.3s ease-out;
}

.dynamic-input-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #67c23a;
  font-size: 14px;
  font-weight: 500;
}

.dynamic-input-tag .el-icon {
  font-size: 16px;
  color: #67c23a;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 输入区域容器样式 */
.input-container {
  position: relative;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-top: 1px solid #dcdfe6;
}

/* 聊天输入区域样式 */
.chat-input {
  padding: 16px;
  display: flex;
  gap: 12px;
  background-color: #f5f7fa;
  border-radius: 0 0 8px 8px;
}

.chat-input .el-input {
  flex: 1;
}

.chat-input .el-input :deep(.el-textarea__inner) {
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  background-color: #fff;
  transition: all 0.3s;
  padding: 12px;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
}

.chat-input .el-input :deep(.el-textarea__inner:focus) {
  border-color: #67c23a;
  box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.1);
}

.chat-input .el-input :deep(.el-textarea__inner:hover) {
  border-color: #85ce61;
}

/* 动态输入按钮样式 */
.dynamic-input-button {
  background-color: #67c23a !important;
  border-color: #67c23a !important;
  transition: all 0.3s;
}

.dynamic-input-button:hover {
  background-color: #85ce61 !important;
  border-color: #85ce61 !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.2);
}

.dynamic-input-button:active {
  transform: translateY(0);
  box-shadow: none;
}

/* 静态输入区域样式 */
.static-inputs-panel {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  overflow: hidden;
}

.static-inputs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.static-inputs-header h4 {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.static-inputs-content {
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.static-input-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.static-input-label {
  font-size: 14px;
  color: #606266;
}

/* 头像上传样式 */
.avatar-upload-container {
  margin-bottom: 16px;
}

.avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 2px dashed #ccc;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.avatar-preview:hover {
  border-color: #409EFF;
  background-color: #f5f7fa;
}

.agent-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #909399;
}

.avatar-placeholder .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.avatar-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>