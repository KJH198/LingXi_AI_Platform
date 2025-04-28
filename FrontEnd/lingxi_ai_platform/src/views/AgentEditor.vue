<template>
  <div class="agent-editor-container">
    <!-- 顶部导航栏 -->
    <header class="editor-header">
      <div class="header-left">
        <el-button icon="ArrowLeft" @click="goBack" plain>返回</el-button>
        <h2>{{ agentData.name || '新建智能体' }}</h2>
        <el-tag v-if="!isPublished" type="info">未发布</el-tag>
        <el-tag v-else type="success">已发布</el-tag>
      </div>
      <div class="header-actions">
        <el-button @click="handleSaveDraft">保存草稿</el-button>
        <el-button type="primary" @click="handlePublish">发布智能体</el-button>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <div class="editor-main">
      <!-- 左侧步骤导航 -->
      <div class="editor-steps">
        <el-steps direction="vertical" :active="activeStep" finish-status="success">
          <el-step title="基本信息" @click="setActiveStep(0)" />
          <el-step title="通用模型选择" @click="setActiveStep(1)" />
          <el-step title="知识库配置" @click="setActiveStep(2)" />
          <el-step title="工作流配置" @click="setActiveStep(3)" />
          <el-step title="预览与调试" @click="setActiveStep(4)" />
        </el-steps>
      </div>

      <!-- 右侧内容区域 -->
      <div class="editor-content">
        <!-- 1. 基本信息配置 -->
        <div v-show="activeStep === 0" class="step-content">
          <h3>基本信息</h3>
          <el-form :model="agentData" label-width="100px">
            <el-form-item label="智能体名称" required>
              <el-input v-model="agentData.name" placeholder="请输入智能体名称"></el-input>
            </el-form-item>
            <el-form-item label="简介">
              <el-input
                v-model="agentData.description"
                type="textarea"
                :rows="4"
                placeholder="请输入智能体简介"
              ></el-input>
            </el-form-item>
          </el-form>
          <div class="step-actions">
            <el-button type="primary" @click="nextStep">下一步</el-button>
          </div>
        </div>

        <!-- 2. 通用模型选择 -->
        <div v-show="activeStep === 1" class="step-content">
          <h3>通用模型选择</h3>
          <div class="model-cards">
            <el-card
              v-for="model in availableModels" 
              :key="model.id"
              :class="{ 'model-card': true, 'model-selected': agentData.modelId === model.id }"
              @click="selectModel(model)"
            >
              <div class="model-card-content">
                <img :src="model.icon" class="model-icon" />
                <h4>{{ model.name }}</h4>
                <p>{{ model.description }}</p>
                <div class="model-features">
                  <el-tag 
                    v-for="feature in model.features" 
                    :key="feature" 
                    size="small"
                  >
                    {{ feature }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </div>

          <div v-if="agentData.modelId" class="selected-model-info">
            <el-alert
              type="success"
              :title="`已选择: ${getSelectedModelName()}`"
              show-icon
              :closable="false"
            >
              <template #default>
                <p>模型将使用默认参数配置。您可以继续下一步进行知识库配置。</p>
              </template>
            </el-alert>
          </div>

          <div class="step-actions">
            <el-button @click="prevStep">上一步</el-button>
            <el-button 
              type="primary" 
              @click="nextStep"
              :disabled="!agentData.modelId"
            >
              下一步
            </el-button>
          </div>
        </div>

        <!-- 3. 知识库配置 -->
        <div v-show="activeStep === 2" class="step-content">
          <knowledge-base-config 
            :agent-data="agentData"
            :active="activeStep === 2"
            @update:knowledgeBases="updateKnowledgeBases">
          </knowledge-base-config>
          <div class="step-actions">
            <el-button @click="prevStep">上一步</el-button>
            <el-button type="primary" @click="nextStep">下一步</el-button>
          </div>
        </div>

        <!-- 4. 工作流配置 -->
        <div v-show="activeStep === 3" class="step-content">
          <workflow-list 
            :workflow-id="agentData.workflowId"
            :active="activeStep === 3"
            @update:workflowId="updateWorkflowId">
          </workflow-list>
          <div class="step-actions">
            <el-button @click="prevStep">上一步</el-button>
            <el-button type="primary" @click="nextStep">下一步</el-button>
          </div>
        </div>

        <!-- 5. 预览与调试 -->
        <div v-show="activeStep === 4" class="step-content">
          <h3>预览与调试</h3>
          
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
                    <el-avatar :size="36" :src="message.role === 'user' ? userAvatar : defaultAgentAvatar"></el-avatar>
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
                <!-- 动态输入提示 -->
                <div v-if="waitingForDynamicInput" class="dynamic-input-prompt">
                  <div class="message-avatar">
                    <el-avatar :size="36" :src="defaultAgentAvatar"></el-avatar>
                    <div class="output-port-name">output</div>
                  </div>
                  <div class="message-content">
                    <div class="dynamic-input-title">等待输入</div>
                    <div class="dynamic-input-vars">
                      <el-tag v-for="(varName, index) in dynamicInputVars" :key="index" type="info">
                        {{ varName }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 输入区域容器 -->
              <div class="input-container">
                <!-- 动态输入区域 -->
                <div v-if="waitingForDynamicInput" class="dynamic-input">
                  <el-input
                    v-model="dynamicInputValue"
                    type="textarea"
                    :rows="3"
                    :placeholder="`请输入${dynamicInputVars.join('、')}`"
                  ></el-input>
                  <el-button
                    type="primary"
                    icon="Position"
                    :disabled="!dynamicInputValue.trim()"
                    @click="handleDynamicInput"
                  >
                    发送
                  </el-button>
                </div>
                
                <!-- 普通输入区域 -->
                <div v-else class="chat-input">
                  <el-input
                    v-model="userInput"
                    type="textarea"
                    :rows="3"
                    placeholder="输入消息，测试智能体的回复..."
                    :disabled="isGenerating"
                    @keydown.enter.prevent="handleSendMessage"
                  ></el-input>
                  <el-button
                    type="primary"
                    icon="Position"
                    :disabled="!userInput.trim() || isGenerating"
                    @click="handleSendMessage"
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
          
          <div class="step-actions">
            <el-button @click="prevStep">上一步</el-button>
            <el-button type="primary" @click="handlePublish">完成并发布</el-button>
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
import { ref, reactive, computed, nextTick, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import KnowledgeBaseConfig from '@/views/KnowledgeBaseConfig.vue'
import WorkflowList from '@/views/WorkflowList.vue'

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
interface StaticInput {
  name: string;
  value: string;
}

const staticInputs = ref<StaticInput[]>([])

// 动态输入相关
const waitingForDynamicInput = ref(false)
const dynamicInputVars = ref<string[]>([])
const dynamicInputValue = ref('')

// 在 script setup 部分添加新的接口和状态
const nodeOutputs = ref<Record<string, any>>({})

// 在 script setup 部分添加新的状态变量
const currentNodeName = ref('')

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
    
    const response = await fetch('/agent/staticInput', {
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
      throw new Error(result.message || '发送静态输入失败')
    }
  } catch (error) {
    console.error('发送静态输入失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '发送静态输入失败')
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
  
  // 在聊天记录中添加节点输出
  chatMessages.value.push({
    role: 'assistant',
    content: `${output}`,
    time: new Date().toLocaleTimeString(),
    nodeName: node_name
  })
  
  // 滚动到底部
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

// 修改 handleResponse 方法
const handleResponse = (response: any) => {
  if (response.requiresDynamicInput) {
    // 需要动态输入
    waitingForDynamicInput.value = true
    dynamicInputVars.value = response.requiredVariables
  } else {
    // 普通响应
    chatMessages.value.push({
      role: 'assistant',
      content: response.content,
      time: new Date().toLocaleTimeString(),
      nodeName: response.nodeName || currentNodeName.value
    })
  }
}

// 修改 handleSendMessage 方法
const handleSendMessage = async () => {
  if (!userInput.value.trim() || isGenerating.value) return
  
  // 添加用户消息
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
  
  // 模拟生成回复
  isGenerating.value = true
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('请先登录')
    }
    
    const response = await fetch('/agent/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        workflowId: agentData.workflowId,
        message: inputText,
        staticInputs: staticInputs.value.map(input => ({
          name: input.name,
          value: input.value
        }))
      })
    })
    
    if (!response.ok) {
      throw new Error('发送消息失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      handleResponse(result.data)
    } else {
      throw new Error(result.message || '发送消息失败')
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败')
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
const resetChat = (): void => {
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
  ElMessage.success('聊天记录已重置')
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
    await ElMessageBox.confirm(
      '确定要发布智能体吗？发布后，其他用户将可以访问您的智能体。',
      '发布智能体',
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
      knowledgeBases: agentData.knowledgeBases,
      workflowId: agentData.workflowId
    }
    
    // 这里实现真正的发布逻辑
    const response = await fetch('user/agent/publish', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(publishData)
    })
    
    if (!response.ok || response.status !== 200) {
      throw new Error('发布智能体失败')
    }

    ElMessage.success(`智能体"${agentData.name}"发布成功！`)
    clearLocalStorage() // 发布成功后清除本地存储中的临时数据
    router.push('/community')

  } catch (error) {
    if (error === 'cancel') return
    
    console.error('发布智能体失败:', error)
    ElMessage.error('发布智能体失败，请稍后重试')
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

// 处理动态输入
const handleDynamicInput = async () => {
  if (!dynamicInputValue.value.trim()) return
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const response = await fetch('/agent/dynamicInput', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        workflowId: agentData.workflowId,
        input: dynamicInputValue.value,
        variables: dynamicInputVars.value
      })
    })
    
    if (!response.ok) {
      throw new Error('发送动态输入失败')
    }
    
    const result = await response.json()
    if (result.code === 200) {
      // 添加用户输入到聊天记录
      chatMessages.value.push({
        role: 'user',
        content: dynamicInputValue.value,
        time: new Date().toLocaleTimeString()
      })
      
      // 重置动态输入状态
      dynamicInputValue.value = ''
      waitingForDynamicInput.value = false
      dynamicInputVars.value = []
      
      // 继续处理响应
      handleResponse(result.data)
    }
  } catch (error) {
    console.error('发送动态输入失败:', error)
    ElMessage.error('发送动态输入失败')
  }
}

// 在 AgentEditor.vue 中修改 onMounted 钩子
onMounted(() => {
  console.log('AgentEditor 组件已挂载，开始初始化数据')
  
  // 建立 WebSocket 连接
  const ws = new WebSocket('ws://localhost:8000/ws/node_output/')
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleNodeOutput(data)
    } catch (error) {
      console.error('处理节点输出失败:', error)
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket 连接错误:', error)
  }
  
  ws.onclose = () => {
    console.log('WebSocket 连接已关闭')
  }
  
  ws.onopen = () => {
    console.log('WebSocket 连接已建立')
  }
  
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
      
      // 重置步骤
      activeStep.value = 0
    } catch (e) {
      console.error('解析初始数据失败:', e)
    }
  } else {
    // 没有初始数据，可能是编辑现有智能体或从其他页面返回
    // 从本地存储恢复所有数据
    restoreFromLocalStorage()
  }
  
  // 添加初始消息
  resetChat()
  
  // 监听页面刷新或关闭事件，保存数据
  window.addEventListener('beforeunload', () => {
    saveToLocalStorage()
  })
  
  // 监听步骤变化，当切换到预览与调试步骤时获取静态输入配置
  watch(activeStep, (newStep) => {
    if (newStep === 4) { // 4是预览与调试的步骤索引
      fetchStaticInputs()
    }
  })
})
</script>

<style scoped>
.agent-editor-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 顶部导航样式 */
.editor-header {
  background-color: #fff;
  padding: 0 20px;
  height: 64px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 主内容区域样式 */
.editor-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 步骤导航样式 */
.editor-steps {
  width: 240px;
  background-color: #fff;
  padding: 20px 0;
  border-right: 1px solid #ebeef5;
}

:deep(.el-steps) {
  padding: 0 20px;
}

:deep(.el-step__title) {
  font-size: 14px;
  cursor: pointer;
}

:deep(.el-step__head) {
  cursor: pointer;
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
}

.step-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

/* 模型卡片样式 */
.model-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.model-card {
  cursor: pointer;
  transition: all 0.3s;
  height: 100%;
}

.model-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.model-selected {
  border: 2px solid #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
}

.model-card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
}

.model-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 10px;
}

.model-card-content h4 {
  margin: 0 0 10px 0;
}

.model-card-content p {
  text-align: center;
  color: #606266;
  font-size: 13px;
  margin-bottom: 10px;
}

.model-features {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
}

.param-description {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

/* 步骤操作按钮样式 */
.step-actions {
  margin-top: 30px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 预览与调试样式 */
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
}

.message {
  display: flex;
  margin-bottom: 16px;
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
  padding: 12px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.bot-message .message-content {
  background-color: #ecf5ff;
}

.message-text {
  white-space: pre-wrap;
  word-break: break-word;
}

.message-text :deep(p) {
  margin: 0 0 10px 0;
}

.message-text :deep(p:last-child) {
  margin-bottom: 0;
}

.message-time {
  font-size: 12px;
  color: #909399;
  text-align: right;
  margin-top: 4px;
}

.chat-input {
  padding: 16px;
  background-color: #fff;
  border-top: 1px solid #dcdfe6;
  display: flex;
  gap: 12px;
}

.chat-input .el-input {
  flex: 1;
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

/* 动态输入提示样式 */
.dynamic-input-prompt {
  display: flex;
  margin-bottom: 16px;
  background-color: #f0f9eb;
  border-radius: 8px;
  padding: 12px;
}

.dynamic-input-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #67c23a;
}

.dynamic-input-vars {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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

/* 输入区域容器样式 */
.input-container {
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-top: 1px solid #dcdfe6;
}

/* 动态输入区域样式 */
.dynamic-input {
  padding: 16px;
  display: flex;
  gap: 12px;
}

.dynamic-input .el-input {
  flex: 1;
}

/* 普通输入区域样式 */
.chat-input {
  padding: 16px;
  display: flex;
  gap: 12px;
}

.chat-input .el-input {
  flex: 1;
}
</style>