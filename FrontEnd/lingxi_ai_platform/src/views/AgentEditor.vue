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
            <el-step title="模型选择" @click="setActiveStep(1)" />
            <el-step title="人设与回复逻辑" @click="setActiveStep(2)" />
            <el-step title="知识库配置" @click="setActiveStep(3)" />
            <el-step title="工作流配置" @click="setActiveStep(4)" />
            <el-step title="预览与调试" @click="setActiveStep(5)" />
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
              <el-form-item label="智能体图标">
                <el-upload
                  class="agent-avatar-uploader"
                  action="#"
                  :show-file-list="false"
                  :on-success="handleAvatarSuccess"
                  :before-upload="beforeAvatarUpload"
                >
                  <img v-if="agentData.avatar" :src="agentData.avatar" class="agent-avatar" />
                  <el-icon v-else class="agent-avatar-uploader-icon"><Plus /></el-icon>
                </el-upload>
              </el-form-item>
              <el-form-item label="简介">
                <el-input
                  v-model="agentData.description"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入智能体简介"
                ></el-input>
              </el-form-item>
              <el-form-item label="标签">
                <el-select
                  v-model="agentData.tags"
                  multiple
                  filterable
                  allow-create
                  default-first-option
                  placeholder="请选择或添加标签"
                >
                  <el-option
                    v-for="tag in availableTags"
                    :key="tag"
                    :label="tag"
                    :value="tag"
                  ></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="分类">
                <el-select v-model="agentData.category" placeholder="请选择分类">
                  <el-option
                    v-for="category in categories"
                    :key="category.value"
                    :label="category.label"
                    :value="category.value"
                  ></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="可见性">
                <el-radio-group v-model="agentData.visibility">
                  <el-radio label="public">公开</el-radio>
                  <el-radio label="private">私有</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-form>
            <div class="step-actions">
              <el-button type="primary" @click="nextStep">下一步</el-button>
            </div>
          </div>
  
          <!-- 2. 模型选择 -->
          <div v-show="activeStep === 1" class="step-content">
            <h3>模型选择</h3>
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
                    <el-tag v-for="feature in model.features" :key="feature" size="small">
                      {{ feature }}
                    </el-tag>
                  </div>
                </div>
              </el-card>
            </div>
            <div class="model-params" v-if="agentData.modelId">
              <h4>模型参数设置</h4>
              <el-form :model="agentData.modelParams" label-width="180px">
                <el-form-item label="温度 (Temperature)">
                  <el-slider
                    v-model="agentData.modelParams.temperature"
                    :min="0"
                    :max="1"
                    :step="0.01"
                    show-input
                  ></el-slider>
                </el-form-item>
                <el-form-item label="最大输出长度">
                  <el-input-number
                    v-model="agentData.modelParams.maxTokens"
                    :min="1"
                    :max="4096"
                    step-strictly
                  ></el-input-number>
                </el-form-item>
                <el-form-item label="Top P">
                  <el-slider
                    v-model="agentData.modelParams.topP"
                    :min="0"
                    :max="1"
                    :step="0.01"
                    show-input
                  ></el-slider>
                </el-form-item>
              </el-form>
            </div>
            <div class="step-actions">
              <el-button @click="prevStep">上一步</el-button>
              <el-button type="primary" @click="nextStep" :disabled="!agentData.modelId">
                下一步
              </el-button>
            </div>
          </div>
  
          <!-- 3. 人设与回复逻辑 -->
          <div v-show="activeStep === 2" class="step-content">
            <h3>人设与回复逻辑</h3>
            <el-tabs v-model="personaTab">
              <el-tab-pane label="基本人设" name="basic">
                <el-form :model="agentData.persona" label-width="100px">
                  <el-form-item label="角色身份">
                    <el-input 
                      v-model="agentData.persona.role" 
                      placeholder="例如：专业厨师、心理咨询师、历史学家等"
                    ></el-input>
                  </el-form-item>
                  <el-form-item label="性格特点">
                    <el-select
                      v-model="agentData.persona.traits"
                      multiple
                      placeholder="请选择性格特点"
                    >
                      <el-option label="专业严谨" value="专业严谨"></el-option>
                      <el-option label="友好亲切" value="友好亲切"></el-option>
                      <el-option label="幽默风趣" value="幽默风趣"></el-option>
                      <el-option label="简洁明了" value="简洁明了"></el-option>
                      <el-option label="耐心细致" value="耐心细致"></el-option>
                      <el-option label="积极乐观" value="积极乐观"></el-option>
                    </el-select>
                  </el-form-item>
                  <el-form-item label="说话风格">
                    <el-input
                      v-model="agentData.persona.tone"
                      type="textarea"
                      :rows="3"
                      placeholder="描述智能体说话的风格，例如：使用专业术语，喜欢用比喻，语气温和等"
                    ></el-input>
                  </el-form-item>
                  <el-form-item label="背景故事">
                    <el-input
                      v-model="agentData.persona.background"
                      type="textarea"
                      :rows="5"
                      placeholder="为智能体设计一个背景故事，丰富其人物形象"
                    ></el-input>
                  </el-form-item>
                </el-form>
              </el-tab-pane>
              <el-tab-pane label="系统提示词" name="system">
                <p class="tip-text">
                  系统提示词会在每次对话开始时发送给模型，用于指导模型的行为方式。
                </p>
                <el-input
                  v-model="agentData.systemPrompt"
                  type="textarea"
                  :rows="10"
                  placeholder="输入系统提示词，定义智能体的行为规则和回复逻辑"
                ></el-input>
                <div class="template-prompts">
                  <h4>提示词模板</h4>
                  <el-button 
                    v-for="template in promptTemplates" 
                    :key="template.name"
                    size="small"
                    @click="applyPromptTemplate(template.content)"
                  >
                    {{ template.name }}
                  </el-button>
                </div>
              </el-tab-pane>
              <el-tab-pane label="高级逻辑" name="advanced">
                <h4>回复约束</h4>
                <el-form :model="agentData.constraints" label-width="120px">
                  <el-form-item label="最大回复长度">
                    <el-input-number
                      v-model="agentData.constraints.maxLength"
                      :min="10"
                      :max="2000"
                    ></el-input-number>
                  </el-form-item>
                  <el-form-item label="回复格式">
                    <el-select v-model="agentData.constraints.format" placeholder="请选择回复格式">
                      <el-option label="纯文本" value="text"></el-option>
                      <el-option label="Markdown" value="markdown"></el-option>
                      <el-option label="结构化JSON" value="json"></el-option>
                    </el-select>
                  </el-form-item>
                </el-form>
              </el-tab-pane>
            </el-tabs>
            <div class="step-actions">
              <el-button @click="prevStep">上一步</el-button>
              <el-button type="primary" @click="nextStep">下一步</el-button>
            </div>
          </div>
  
          <!-- 4. 知识库配置 -->
          <div v-show="activeStep === 3" class="step-content">
            <h3>知识库配置</h3>
            <div class="knowledge-base-actions">
              <el-button type="primary" icon="Plus" @click="showCreateKnowledgeDialog">
                创建知识库
              </el-button>
              <el-button icon="Upload" @click="showUploadKnowledgeDialog">
                上传文件
              </el-button>
            </div>
            
            <div class="knowledge-bases">
              <h4>我的知识库</h4>
              <el-table :data="knowledgeBases" style="width: 100%">
                <el-table-column prop="name" label="名称" />
                <el-table-column prop="description" label="描述" />
                <el-table-column prop="documentCount" label="文档数量" />
                <el-table-column prop="createdAt" label="创建时间" />
                <el-table-column fixed="right" label="操作" width="150">
                  <template #default="scope">
                    <el-button 
                      :type="isKnowledgeBaseSelected(scope.row.id) ? 'success' : 'primary'"
                      link
                      @click="toggleKnowledgeBase(scope.row)"
                    >
                      {{ isKnowledgeBaseSelected(scope.row.id) ? '已选择' : '选择' }}
                    </el-button>
                    <el-button link type="primary" @click="viewKnowledgeBase(scope.row)">查看</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div class="selected-knowledge-bases" v-if="agentData.knowledgeBases.length > 0">
              <h4>已选择的知识库</h4>
              <el-tag
                v-for="kb in selectedKnowledgeBasesInfo"
                :key="kb.id"
                closable
                @close="removeKnowledgeBase(kb.id)"
                class="knowledge-tag"
              >
                {{ kb.name }} ({{ kb.documentCount }}文档)
              </el-tag>
            </div>
            
            <div class="step-actions">
              <el-button @click="prevStep">上一步</el-button>
              <el-button type="primary" @click="nextStep">下一步</el-button>
            </div>
          </div>
  
          <!-- 5. 工作流配置 -->
          <div v-show="activeStep === 4" class="step-content">
            <h3>工作流配置</h3>
            
            <div v-if="!agentData.workflowId" class="workflow-enabled">
              <p class="tip-text">
                工作流允许您设计智能体的处理流程，包括输入处理、调用外部API、条件判断等。
              </p>
              <div class="workflow-actions">
                <el-button type="primary" @click="navigateToWorkflowEditor">
                  前往工作流编辑器
                </el-button>
                <el-button @click="importWorkflow">导入现有工作流</el-button>
              </div>
            </div>
            
            <div v-else class="workflow-enabled">
              <p class="tip-text">
                工作流允许您设计智能体的处理流程，包括输入处理、调用外部API、条件判断等。
              </p>
              <div class="workflow-actions">
                <el-button type="primary" @click="navigateToWorkflowEditor">
                  前往工作流编辑器
                </el-button>
                <el-button @click="importWorkflow">导入现有工作流</el-button>
              </div>
              
              <div v-if="agentData.workflowId" class="workflow-info">
                <el-result
                  icon="success"
                  title="工作流已配置"
                  sub-title="您的智能体将按照工作流定义的逻辑进行处理"
                >
                  <template #extra>
                    <el-button type="primary" @click="navigateToWorkflowEditor">
                      编辑工作流
                    </el-button>
                    <el-button @click="removeWorkflow">移除工作流</el-button>
                  </template>
                </el-result>
              </div>
            </div>
            
            <div class="step-actions">
              <el-button @click="prevStep">上一步</el-button>
              <el-button type="primary" @click="nextStep">下一步</el-button>
            </div>
          </div>
  
          <!-- 6. 预览与调试 -->
          <div v-show="activeStep === 5" class="step-content">
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
                      <el-avatar :size="36" :src="message.role === 'user' ? userAvatar : agentData.avatar || defaultAgentAvatar"></el-avatar>
                    </div>
                    <div class="message-content">
                      <div class="message-text" v-html="formatMessage(message.content)"></div>
                      <div class="message-time">{{ message.time }}</div>
                    </div>
                  </div>
                  <div v-if="isGenerating" class="bot-message message">
                    <div class="message-avatar">
                      <el-avatar :size="36" :src="agentData.avatar || defaultAgentAvatar"></el-avatar>
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
                
                <div class="chat-input">
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
              
              <div class="debug-panel">
                <h4>调试面板</h4>
                <el-tabs v-model="debugTab">
                  <el-tab-pane label="请求详情" name="request">
                    <div class="debug-content">
                      <pre>{{ JSON.stringify(lastRequest, null, 2) }}</pre>
                    </div>
                  </el-tab-pane>
                  <el-tab-pane label="响应详情" name="response">
                    <div class="debug-content">
                      <pre>{{ JSON.stringify(lastResponse, null, 2) }}</pre>
                    </div>
                  </el-tab-pane>
                  <el-tab-pane label="模型调用记录" name="logs">
                    <div class="debug-content logs">
                      <div v-for="(log, index) in modelLogs" :key="index" class="log-item">
                        <span class="log-time">{{ log.time }}</span>
                        <span :class="['log-type', `log-type-${log.type}`]">{{ log.type }}</span>
                        <span class="log-message">{{ log.message }}</span>
                      </div>
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>
            </div>
            
            <div class="step-actions">
              <el-button @click="prevStep">上一步</el-button>
              <el-button type="primary" @click="handlePublish">完成并发布</el-button>
            </div>
          </div>
        </div>
      </div>
  
      <!-- 创建知识库对话框 -->
      <el-dialog
        v-model="createKnowledgeDialogVisible"
        title="创建知识库"
        width="50%"
      >
        <el-form :model="newKnowledgeBase" label-width="80px">
          <el-form-item label="名称" required>
            <el-input v-model="newKnowledgeBase.name" placeholder="请输入知识库名称"></el-input>
          </el-form-item>
          <el-form-item label="描述">
            <el-input
              v-model="newKnowledgeBase.description"
              type="textarea"
              :rows="3"
              placeholder="请输入知识库描述"
            ></el-input>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="createKnowledgeDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="createKnowledgeBase">创建</el-button>
          </span>
        </template>
      </el-dialog>
  
      <!-- 上传文件对话框 -->
      <el-dialog
        v-model="uploadKnowledgeDialogVisible"
        title="上传知识文件"
        width="50%"
      >
        <el-form label-width="100px">
          <el-form-item label="选择知识库" required>
            <el-select v-model="selectedUploadKnowledgeBaseId" placeholder="请选择知识库">
              <el-option
                v-for="kb in knowledgeBases"
                :key="kb.id"
                :label="kb.name"
                :value="kb.id"
              ></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="上传文件">
            <el-upload
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              multiple
            >
              <el-button icon="Upload">选择文件</el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持上传 PDF、TXT、DOCX、MD 等格式文件，单个文件不超过10MB
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="uploadKnowledgeDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="uploadKnowledgeFiles" :disabled="!selectedUploadKnowledgeBaseId">上传</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, reactive, computed, nextTick, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { Plus, ArrowLeft, Position } from '@element-plus/icons-vue'
  import { marked } from 'marked'
  import DOMPurify from 'dompurify'
  
  const router = useRouter()
  const route = useRoute()
  
  // 基础数据
  const activeStep = ref(0)
  const isPublished = ref(false)
  const personaTab = ref('basic')
  const debugTab = ref('request')
  const chatMessagesRef = ref<HTMLElement>()
  
  // 创建知识库相关
  const createKnowledgeDialogVisible = ref(false)
  const uploadKnowledgeDialogVisible = ref(false)
  const selectedUploadKnowledgeBaseId = ref('')
  const uploadFiles = ref<File[]>([])
  
  // 聊天预览相关
  const userInput = ref('')
  const isGenerating = ref(false)
  const userAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
  const defaultAgentAvatar = 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png'
  const chatMessages = ref<{ role: string; content: string; time: string }[]>([])
  const lastRequest = ref({})
  const lastResponse = ref({})
  const modelLogs = ref<{ time: string; type: string; message: string }[]>([])
  
  // 智能体数据
  const agentData = reactive({
    id: '',
    name: '',
    description: '',
    avatar: '',
    tags: [] as string[],
    category: '',
    visibility: 'public',
    modelId: '',
    modelParams: {
      temperature: 0.7,
      maxTokens: 1024,
      topP: 0.95
    },
    persona: {
      role: '',
      traits: [] as string[],
      tone: '',
      background: ''
    },
    systemPrompt: '',
    useWorkflow: false,
    useReactMode: false,
    constraints: {
      maxLength: 500,
      format: 'markdown'
    },
    knowledgeBases: [] as string[],
    workflowId: ''
  })
  
  // 创建新知识库数据
  const newKnowledgeBase = reactive({
    name: '',
    description: ''
  })
  
  // 可选模型列表
  const availableModels = ref([
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
  
  // 可用标签
  const availableTags = ref([
    '教育助手', '编程助手', '生活顾问', '健康咨询', '内容创作', 
    '数据分析', '金融顾问', '法律咨询', '客服机器人', '娱乐聊天'
  ])
  
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
  
  // 提示词模板
  const promptTemplates = ref([
    { 
      name: '专业助手模板', 
      content: `你是一个专业的{领域}助手，拥有丰富的{领域}知识和经验。请以专业、准确的方式回答用户的问题，提供有价值的建议。
  在回答问题时，请注意以下几点：
  1. 确保信息的准确性和专业性
  2. 使用行业专业术语，但确保解释清晰
  3. 如果无法确定答案，请诚实说明，不要提供错误信息
  4. 保持友好和尊重的态度`
    },
    { 
      name: '角色扮演模板', 
      content: `你是{角色名称}，一个{角色背景简介}。
  
  性格特点：
  - {列出角色的主要性格特点}
  
  说话风格：
  - {描述角色的说话方式和语气}
  
  背景故事：
  {详细的角色背景故事}
  
  在与用户交流时，请始终保持角色身份，使用符合角色特点的语气和表达方式回应用户。避免使用会打破角色扮演的表述。`
    },
    { 
      name: '教学辅导模板', 
      content: `你是一位耐心、友好的{学科}老师，专注于帮助学生理解复杂概念并解决问题。
  
  在回答学生问题时遵循以下原则：
  1. 先确认学生的知识基础，针对性解答
  2. 使用简单明了的语言解释复杂概念
  3. 提供具体例子来帮助理解
  4. 鼓励批判性思考，引导学生自己找到答案
  5. 如果学生遇到困难，提供逐步指导而不是直接给出答案
  
  回应应保持积极鼓励的态度，避免任何负面或批判性的评价。`
    }
  ])
  
  // 模拟知识库数据
  const knowledgeBases = ref([
    {
      id: 'kb1',
      name: '产品手册库',
      description: '包含所有产品说明书和用户手册',
      documentCount: 24,
      createdAt: '2025-03-15'
    },
    {
      id: 'kb2',
      name: '技术博客集',
      description: '各类技术博客和文章整理',
      documentCount: 47,
      createdAt: '2025-03-20'
    },
    {
      id: 'kb3',
      name: '公司政策库',
      description: '公司内部政策和规章制度',
      documentCount: 12,
      createdAt: '2025-03-25'
    }
  ])
  
  // 计算选中的知识库信息
  const selectedKnowledgeBasesInfo = computed(() => {
    return knowledgeBases.value.filter(kb => 
      agentData.knowledgeBases.includes(kb.id)
    )
  })
  
  // 检查知识库是否被选中
  const isKnowledgeBaseSelected = (kbId: string) => {
    return agentData.knowledgeBases.includes(kbId)
  }
  
  // 导航功能
  const goBack = () => {
    router.push('/community')
  }
  
  // 步骤控制
  const setActiveStep = (step: number) => {
    activeStep.value = step
  }
  
  const nextStep = () => {
    if (activeStep.value < 5) {
      activeStep.value++
    }
  }
  
  const prevStep = () => {
    if (activeStep.value > 0) {
      activeStep.value--
    }
  }
  
  // 模型选择
  const selectModel = (model: any) => {
    agentData.modelId = model.id
  }
  
  // 创建知识库
  const showCreateKnowledgeDialog = () => {
    createKnowledgeDialogVisible.value = true
  }
  
  const createKnowledgeBase = () => {
    if (!newKnowledgeBase.name) {
      ElMessage.warning('请输入知识库名称')
      return
    }
    
    // 生成随机ID
    const id = 'kb' + Date.now()
    
    // 添加到知识库列表
    knowledgeBases.value.push({
      id,
      name: newKnowledgeBase.name,
      description: newKnowledgeBase.description,
      documentCount: 0,
      createdAt: new Date().toISOString().split('T')[0]
    })
    
    // 自动选择新创建的知识库
    agentData.knowledgeBases.push(id)
    
    // 重置表单
    newKnowledgeBase.name = ''
    newKnowledgeBase.description = ''
    
    createKnowledgeDialogVisible.value = false
    ElMessage.success('知识库创建成功')
  }
  
  // 上传知识文件
  const showUploadKnowledgeDialog = () => {
    uploadKnowledgeDialogVisible.value = true
  }
  
  const handleFileChange = (file: any) => {
    uploadFiles.value.push(file.raw)
  }
  
  const uploadKnowledgeFiles = () => {
    if (!selectedUploadKnowledgeBaseId.value) {
      ElMessage.warning('请选择知识库')
      return
    }
    
    if (uploadFiles.value.length === 0) {
      ElMessage.warning('请选择要上传的文件')
      return
    }
    
    // 模拟上传成功，更新知识库文档计数
    const kb = knowledgeBases.value.find(kb => kb.id === selectedUploadKnowledgeBaseId.value)
    if (kb) {
      kb.documentCount += uploadFiles.value.length
    }
    
    // 重置表单
    uploadFiles.value = []
    selectedUploadKnowledgeBaseId.value = ''
    
    uploadKnowledgeDialogVisible.value = false
    ElMessage.success('文件上传成功')
  }
  
  // 知识库操作
  const toggleKnowledgeBase = (kb: any) => {
    const index = agentData.knowledgeBases.indexOf(kb.id)
    if (index === -1) {
      // 添加知识库
      agentData.knowledgeBases.push(kb.id)
      ElMessage.success(`已添加知识库: ${kb.name}`)
    } else {
      // 移除知识库
      agentData.knowledgeBases.splice(index, 1)
      ElMessage.info(`已移除知识库: ${kb.name}`)
    }
  }
  
  const removeKnowledgeBase = (kbId: string) => {
    const index = agentData.knowledgeBases.indexOf(kbId)
    if (index !== -1) {
      agentData.knowledgeBases.splice(index, 1)
    }
  }
  
  const viewKnowledgeBase = (kb: any) => {
    ElMessage.info(`查看知识库: ${kb.name}（此功能正在开发中）`)
  }
  
  // 工作流相关
  const enableWorkflow = () => {
    agentData.useWorkflow = true
    // 切换到人设配置页面的高级逻辑选项卡
    activeStep.value = 2
    personaTab.value = 'advanced'
  }
  
  const navigateToWorkflowEditor = () => {
  // 保存当前数据然后导航
  localStorage.setItem('tempAgentData', JSON.stringify(agentData))
  router.push('/create-ai')
}
  
  const importWorkflow = () => {
    ElMessage.info('导入工作流功能正在开发中')
  }
  
  const removeWorkflow = () => {
    ElMessageBox.confirm(
      '确定要移除当前工作流吗？这将影响智能体的处理逻辑。',
      '移除工作流',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
      .then(() => {
        agentData.workflowId = ''
        ElMessage.success('工作流已移除')
      })
      .catch(() => {})
  }
  
  // 上传头像处理
  const handleAvatarSuccess = (res: any) => {
    agentData.avatar = res.url || URL.createObjectURL(res.raw)
  }
  
  const beforeAvatarUpload = (file: File) => {
    const isImage = file.type.startsWith('image/')
    const isLt2M = file.size / 1024 / 1024 < 2
    
    if (!isImage) {
      ElMessage.error('上传头像图片只能是图片格式!')
      return false
    }
    if (!isLt2M) {
      ElMessage.error('上传头像图片大小不能超过 2MB!')
      return false
    }
    
    // 模拟上传成功，创建临时URL
    agentData.avatar = URL.createObjectURL(file)
    return false // 阻止默认上传
  }
  
  // 应用提示词模板
  const applyPromptTemplate = (template: string) => {
    if (agentData.systemPrompt) {
      ElMessageBox.confirm(
        '应用模板将覆盖当前提示词，是否继续？',
        '提示',
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )
        .then(() => {
          agentData.systemPrompt = template
        })
        .catch(() => {})
    } else {
      agentData.systemPrompt = template
    }
  }
  
  // 聊天预览功能
  const handleSendMessage = async () => {
    if (!userInput.value.trim() || isGenerating.value) return
    
    // 添加用户消息
    const userMessage = {
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
      params: agentData.modelParams
    }
    
    // 添加日志
    addLog('info', '发送用户消息: ' + inputText)
    
    // 模拟生成回复
    isGenerating.value = true
    setTimeout(async () => {
      // 生成回复
      const botReply = generateResponse(inputText)
      
      // 添加AI回复
      const botMessage = {
        role: 'assistant',
        content: botReply,
        time: new Date().toLocaleTimeString()
      }
      chatMessages.value.push(botMessage)
      
      // 记录响应
      lastResponse.value = {
        content: botReply,
        usage: {
          prompt_tokens: inputText.length * 2,
          completion_tokens: botReply.length * 1.5,
          total_tokens: inputText.length * 2 + botReply.length * 1.5
        },
        finish_reason: 'stop'
      }
      
      // 添加日志
      addLog('success', '收到模型回复，长度: ' + botReply.length)
      
      isGenerating.value = false
      
      // 滚动到底部
      await nextTick()
      if (chatMessagesRef.value) {
        chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
      }
    }, 1500)
  }
  
  // 模拟生成响应
  const generateResponse = (input: string) => {
    // 基于人设和不同输入模拟不同的回复
    if (agentData.persona.role === '专业厨师') {
      if (input.includes('菜谱') || input.includes('做饭') || input.includes('料理')) {
        return `作为一名专业厨师，我很高兴为您提供建议！
  
  以下是一个简单的食谱：
  
  ## 香煎三文鱼配时蔬
  
  **材料：**
  - 三文鱼片 200g
  - 西兰花 100g
  - 胡萝卜 1根
  - 橄榄油 2汤匙
  - 盐和胡椒粉适量
  - 柠檬汁 1汤匙
  
  **步骤：**
  1. 将三文鱼用厨房纸吸干水分，撒上盐和胡椒调味
  2. 热锅中加入橄榄油，中火将三文鱼皮朝下放入锅中
  3. 煎至皮酥脆，约3-4分钟，翻面再煎1-2分钟
  4. 同时，将西兰花和胡萝卜切块，焯水后淋上橄榄油和盐调味
  5. 装盘时，挤上柠檬汁提味
  
  希望您喜欢这个简单又健康的食谱！如果有任何疑问，随时可以继续咨询我。`;
      } else {
        return `作为一名专业厨师，我很乐意解答您的问题。如果您对烹饪技巧、食材搭配或特定菜谱有疑问，请随时提出，我将尽力提供专业的建议和指导。
  
  您可以询问诸如：
  - 如何提升某道菜的味道
  - 食材的挑选和存储方法
  - 刀工和烹饪技巧
  - 特定饮食需求的菜谱建议
  
  请告诉我您需要什么样的烹饪帮助？`;
      }
    } else if (input.toLowerCase().includes('hello') || input.includes('你好')) {
      return `你好！我是${agentData.name || '智能助手'}，${agentData.description || '很高兴为您服务'}。
  
  有什么我可以帮助您的吗？无论是${agentData.persona.role ? '关于' + agentData.persona.role + '的问题' : '问题解答'}、信息查询还是日常对话，我都很乐意与您交流。`;
    } else if (input.includes('功能') || input.includes('你能做什么')) {
      return `作为${agentData.name || '智能助手'}，我可以为您提供以下帮助：
  
  ${agentData.persona.role ? `- 作为${agentData.persona.role}，提供专业知识和建议` : '- 回答各类问题，提供信息和建议'}
  ${agentData.knowledgeBases.length > 0 ? '- 基于我的知识库回答专业问题' : ''}
  ${agentData.useWorkflow ? '- 执行复杂的工作流程，处理多步骤任务' : ''}
  - 进行日常对话，提供信息和建议
  - 根据您的需求生成内容
  
  请随时告诉我您需要什么样的帮助，我会尽力满足您的需求。`;
    } else {
      return `感谢您的提问！${agentData.persona.role ? `作为${agentData.persona.role}，` : ''}我会尽力为您提供有用的信息和帮助。
  
  您的问题很有趣，根据我的理解，您想了解关于"${input.substring(0, 20)}..."的信息。这是一个很好的问题！
  
  ${agentData.knowledgeBases.length > 0 ? '我已经查阅了相关知识库，' : ''}根据我掌握的信息，这个主题涉及多个方面：
  
  1. 首先，我们需要了解基本概念和背景
  2. 其次，考虑实际应用场景和最佳实践
  3. 最后，可能存在的挑战和解决方案
  
  如果您能提供更具体的信息或疑问，我可以给您更有针对性的回答。请随时告诉我您想深入了解哪个方面。`;
    }
  }
  
  // 格式化消息（将markdown转为HTML）
  const formatMessage = (message: string) => {
    if (!message) return '';
    
    // 如果启用了markdown格式
    if (agentData.constraints.format === 'markdown') {
        const html = marked.parse(message, { async: false }) as string;
      return DOMPurify.sanitize(html);
    }
    
    // 纯文本格式，保留换行
    return message.replace(/\n/g, '<br>');
  }
  
  // 添加日志
  const addLog = (type: string, message: string) => {
    modelLogs.value.push({
      time: new Date().toLocaleTimeString(),
      type,
      message
    })
  }
  
  // 重置聊天
  const resetChat = () => {
    chatMessages.value = []
    lastRequest.value = {}
    lastResponse.value = {}
    modelLogs.value = []
    ElMessage.success('聊天记录已重置')
  }
  
  // 保存草稿
  const handleSaveDraft = () => {
    ElMessage.success('智能体草稿已保存')
  }
  
  // 发布智能体
  const handlePublish = () => {
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
    
    ElMessageBox.confirm(
      '确定要发布智能体吗？发布后，其他用户将可以访问您的智能体。',
      '发布智能体',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'info' }
    )
      .then(() => {
        ElMessage.success(`智能体"${agentData.name}"发布成功！`)
        isPublished.value = true
        router.push('/community')
      })
      .catch(() => {})
  }
  
  // 初始化
  onMounted(() => {
    // 如果URL中有agentId参数，尝试加载智能体数据
    const agentId = route.query.agentId
    if (agentId) {
      // 模拟从API加载数据
      ElMessage.info('正在加载智能体数据...')
      // 这里可以添加加载逻辑
    }
    
    // 添加初始消息
    chatMessages.value = [
      {
        role: 'assistant',
        content: `你好！我是${agentData.name || '智能助手'}。有什么我可以帮助你的吗？`,
        time: new Date().toLocaleTimeString()
      }
    ]
  })

  onMounted(() => {
  // 检查是否有来自前置对话框的初始数据
  const savedAgentInitData = localStorage.getItem('agentInitData')
  
  if (savedAgentInitData) {
    try {
      const initData = JSON.parse(savedAgentInitData)
      // 将初始数据填充到 agentData 中
      agentData.name = initData.name || ''
      agentData.description = initData.description || ''
      agentData.category = initData.category || ''
      agentData.visibility = initData.visibility || 'public'
      
      // 使用完后清除缓存数据
      localStorage.removeItem('agentInitData')
    } catch (error) {
      console.error('解析初始数据失败:', error)
    }
  }
  
  // 如果URL中有agentId参数，尝试加载智能体数据
  const agentId = route.query.agentId
  if (agentId) {
    // 模拟从API加载数据
    ElMessage.info('正在加载智能体数据...')
    // 这里可以添加加载逻辑
  }
  
  // 添加初始消息
  chatMessages.value = [
    {
      role: 'assistant',
      content: `你好！我是${agentData.name || '智能助手'}。有什么我可以帮助你的吗？`,
      time: new Date().toLocaleTimeString()
    }
  ]
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
  
  /* 步骤操作按钮样式 */
  .step-actions {
    margin-top: 30px;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
  
  /* 智能体头像上传样式 */
  .agent-avatar-uploader {
    width: 120px;
    height: 120px;
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .agent-avatar-uploader:hover {
    border-color: #409eff;
  }
  
  .agent-avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
  }
  
  .agent-avatar {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  /* 提示文本样式 */
  .tip-text {
    padding: 10px;
    background-color: #ecf8ff;
    color: #409eff;
    border-radius: 4px;
    margin: 10px 0;
    font-size: 13px;
  }
  
  /* 模板提示词样式 */
  .template-prompts {
    margin-top: 16px;
  }
  
  .template-prompts h4 {
    font-size: 14px;
    margin-bottom: 8px;
  }
  
  .template-prompts .el-button {
    margin-right: 8px;
    margin-bottom: 8px;
  }
  
  /* 知识库相关样式 */
  .knowledge-base-actions {
    margin-bottom: 20px;
    display: flex;
    gap: 12px;
  }
  
  .knowledge-tag {
    margin-right: 8px;
    margin-bottom: 8px;
  }
  
  .selected-knowledge-bases {
    margin-top: 20px;
    padding: 12px;
    background-color: #f5f7fa;
    border-radius: 4px;
  }
  
  /* 工作流相关样式 */
  .workflow-disabled {
    padding: 30px 0;
  }
  
  .workflow-actions {
    margin: 20px 0;
    display: flex;
    gap: 12px;
  }
  
  .workflow-info {
    margin-top: 20px;
  }
  
  /* 预览与调试样式 */
  .preview-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    height: 500px;
  }
  
  .chat-preview {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
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
    margin: 0 8px;
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
  
  .message-text :deep(code) {
    background-color: #f5f7fa;
    padding: 2px 4px;
    border-radius: 4px;
    font-family: monospace;
  }
  
  .message-text :deep(pre) {
    background-color: #282c34;
    color: #abb2bf;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
    font-family: monospace;
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
  
  /* 表单样式优化 */
  :deep(.el-form-item__label) {
    font-weight: 500;
  }
  
  :deep(.el-select) {
    width: 100%;
  }
  
  :deep(.el-input-number) {
    width: 100%;
  }
  </style>