<template>
  <div class="knowledge-base-config">
    <h3>知识库配置</h3>
    <p class="description">
      为您的智能体添加知识库，使其能够访问专业领域知识。
    </p>

    <!-- 添加搜索栏 -->
    <div class="search-container">
      <el-input
        v-model="searchQuery"
        placeholder="搜索知识库..."
        prefix-icon="Search"
        clearable
        @input="searchKnowledgeBases"
      />
      <el-select v-model="typeFilter" placeholder="知识库类型" clearable @change="filterKnowledgeBases">
        <el-option label="全部类型" value="" />
        <el-option label="文本知识库" value="text" />
        <el-option label="图片知识库" value="image" />
      </el-select>
    </div>

    <!-- 已选择的知识库 -->
    <div class="selected-knowledge-bases" v-if="selectedKnowledgeBasesInfo.length > 0">
      <h4>已选择的知识库</h4>
      <div class="knowledge-tags">
        <el-tag
          v-for="kb in selectedKnowledgeBasesInfo"
          :key="kb.id"
          closable
          @close="removeKnowledgeBase(kb.id)"
          class="knowledge-tag"
        >
          {{ kb.name }}
        </el-tag>
      </div>
    </div>

    <!-- 知识库列表与操作 -->
    <div class="knowledge-base-actions">
      <div class="action-buttons">
        <el-button type="primary" @click="createKnowledgeDialogVisible = true">
          创建知识库
        </el-button>
        <el-button @click="uploadKnowledgeDialogVisible = true">上传文件</el-button>
      </div>
    </div>

    <!-- 知识库列表 -->
    <div class="knowledge-base-list">
      <h4>可选知识库</h4>
      <el-table :data="knowledgeBases" style="width: 100%">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="type" label="类型">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'text' ? 'primary' : 'success'">
              {{ scope.row.type === 'text' ? '文本' : '图片' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag 
              :type="scope.row.status === 'ready' ? 'success' : scope.row.status === 'processing' ? 'warning' : 'info'"
            >
              {{ scope.row.status === 'ready' ? '已就绪' : 
                 scope.row.status === 'processing' ? '处理中' : '未处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" />
        <el-table-column fixed="right" label="操作" width="150">
          <template #default="scope">
            <el-button
              link
              type="primary"
              size="small"
              @click="viewKnowledgeBase(scope.row)"
            >
              查看
            </el-button>
            <el-button
              link
              :type="isKnowledgeBaseSelected(scope.row.id) ? 'danger' : 'success'"
              size="small"
              @click="toggleKnowledgeBase(scope.row)"
            >
              {{ isKnowledgeBaseSelected(scope.row.id) ? '取消选择' : '选择' }}
            </el-button>
            <el-button v-if="scope.row.isOwner" link type="warning" size="small" @click="deleteKnowledgeBase(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
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
        <el-form-item label="类型" required>
          <el-select v-model="newKnowledgeBase.type" placeholder="请选择知识库类型">
            <el-option label="文本知识库" value="text"></el-option>
            <el-option label="图片知识库" value="image"></el-option>
          </el-select>
          <div class="el-form-item-description">
            <small v-if="newKnowledgeBase.type === 'text'">文本知识库支持PDF、TXT、DOCX、MD等格式文件</small>
            <small v-else-if="newKnowledgeBase.type === 'image'">图片知识库支持JPG、PNG、GIF等图片格式</small>
          </div>
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
          <el-select v-model="selectedUploadKnowledgeBaseId" placeholder="请选择知识库" @change="handleKnowledgeBaseChange">
            <el-option
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :label="kb.name"
              :value="kb.id"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <!-- 文本知识库上传选项 -->
        <template v-if="selectedKnowledgeBaseType === 'text'">
          <el-form-item label="上传文件">
            <el-upload
              action="#"
              :auto-upload="false"
              :on-change="handleTextFileChange"
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
        </template>
        
        <!-- 图片知识库上传选项 -->
        <template v-else-if="selectedKnowledgeBaseType === 'image'">
          <el-form-item label="上传图片">
            <el-upload
              action="#"
              :auto-upload="false"
              :on-change="handleImageFileChange"
              multiple
              accept="image/*"
              list-type="picture-card"
            >
              <el-icon><Plus /></el-icon>
              <template #tip>
                <div class="el-upload__tip">
                  支持上传JPG、PNG、GIF等图片格式，单个图片不超过5MB
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadKnowledgeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="uploadKnowledgeFiles" :disabled="!canUpload">上传</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const props = defineProps({
  agentData: {
    type: Object,
    required: true
  },
  active: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:knowledgeBases'])

// 知识库列表
const knowledgeBases = ref([
  {
    id: 'kb1',
    name: '产品手册库',
    description: '包含所有产品说明书和用户手册',
    createdAt: '2025-03-15',
    type: 'text'
  },
  {
    id: 'kb2',
    name: '技术博客集',
    description: '各类技术博客和文章整理',
    createdAt: '2025-03-20',
    type: 'text'
  },
  {
    id: 'kb3',
    name: '公司政策库',
    description: '公司内部政策和规章制度',
    createdAt: '2025-03-25',
    type: 'text'
  },
  {
    id: 'kb4',
    name: '产品宣传图库',
    description: '产品宣传图片和市场素材',
    createdAt: '2025-04-01',
    type: 'image'
  }
])

// 知识库详情对话框相关状态
const knowledgeBaseDetailVisible = ref(false)
const currentKnowledgeBase = ref({})
const knowledgeBaseFiles = ref([])

// 添加缓存标记
const knowledgeBasesLoaded = ref(false)

// 搜索与过滤
const searchQuery = ref('')
const typeFilter = ref('')

const searchKnowledgeBases = () => {
  console.log('搜索知识库:', searchQuery.value)
  // 实际应用中可以在这里调用API或过滤数据
}

const filterKnowledgeBases = () => {
  console.log('过滤知识库类型:', typeFilter.value)
  // 实际应用中可以在这里调用API或过滤数据
}

// 对话框控制
const createKnowledgeDialogVisible = ref(false)
const uploadKnowledgeDialogVisible = ref(false)

// 创建新知识库数据
const newKnowledgeBase = reactive({
  name: '',
  description: '',
  type: 'text' // 默认为文本类型
})

// 上传文件相关
const selectedUploadKnowledgeBaseId = ref('')
const selectedKnowledgeBaseType = ref('')
const uploadFiles = ref<File[]>([])

// 获取已选择知识库的详细信息
const selectedKnowledgeBasesInfo = computed(() => {
  return props.agentData.knowledgeBases
    .map(id => knowledgeBases.value.find(kb => kb.id === id))
    .filter(kb => kb !== undefined) as any[]
})

// 计算属性：是否可以上传
const canUpload = computed(() => {
  if (!selectedUploadKnowledgeBaseId.value) return false
  return uploadFiles.value.length > 0
})

// 检查知识库是否被选择
const isKnowledgeBaseSelected = (id: string) => {
  return props.agentData.knowledgeBases.includes(id)
}

// 添加或移除知识库
const toggleKnowledgeBase = (kb: any) => {
  if (isKnowledgeBaseSelected(kb.id)) {
    removeKnowledgeBase(kb.id)
  } else {
    addKnowledgeBase(kb.id)
  }
}

const addKnowledgeBase = (id: string) => {
  if (!props.agentData.knowledgeBases.includes(id)) {
    const newKnowledgeBases = [...props.agentData.knowledgeBases, id]
    emit('update:knowledgeBases', newKnowledgeBases)
  }
}

const removeKnowledgeBase = (id: string) => {
  const newKnowledgeBases = props.agentData.knowledgeBases.filter(kbId => kbId !== id)
  emit('update:knowledgeBases', newKnowledgeBases)
}

// 创建知识库
const createKnowledgeBase = async () => {
  if (!newKnowledgeBase.name) {
    ElMessage.warning('请输入知识库名称')
    return
  }
  
  if (!newKnowledgeBase.type) {
    ElMessage.warning('请选择知识库类型')
    return
  }
  
  try {
    const response = await fetch('/create_knowledgebase', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: newKnowledgeBase.name,
        description: newKnowledgeBase.description,
        type: newKnowledgeBase.type
      })
    })
    
    if (!response.ok) {
      throw new Error('创建知识库失败')
    }
    
    const result = await response.json()
    
    // 添加到知识库列表
    knowledgeBases.value.push({
      id: result.id,
      name: result.name,
      description: result.description,
      type: result.type,
      createdAt: result.createdAt
    })
    
    // 自动选择新创建的知识库
    addKnowledgeBase(result.id)
    
    // 重置表单
    newKnowledgeBase.name = ''
    newKnowledgeBase.description = ''
    newKnowledgeBase.type = 'text'
    createKnowledgeDialogVisible.value = false
    
    ElMessage.success('知识库创建成功')
  } catch (error) {
    console.error('创建知识库失败:', error)
    ElMessage.error('创建知识库失败，请稍后重试')
  }
}

// 查看知识库详情
const viewKnowledgeBase = async (kb: any) => {
  try {
    // 模拟API调用获取详情
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 示例文档列表
    const documents = kb.type === 'text' ? [
      { id: 'doc1', filename: '产品手册.pdf', size: 1024 * 1024 * 2, upload_time: '2025-03-16 10:30:45' },
      { id: 'doc2', filename: 'API文档.md', size: 1024 * 512, upload_time: '2025-03-16 14:20:12' },
      { id: 'doc3', filename: '安装指南.docx', size: 1024 * 768, upload_time: '2025-03-17 09:15:33' }
    ] : [
      { id: 'doc4', filename: '产品展示图1.jpg', size: 1024 * 512, upload_time: '2025-04-02 11:24:15' },
      { id: 'doc5', filename: '宣传海报.png', size: 1024 * 1024, upload_time: '2025-04-03 15:42:18' },
      { id: 'doc6', filename: '品牌Logo.png', size: 1024 * 256, upload_time: '2025-04-05 10:10:38' }
    ]
    
    // 获取知识库类型中文名称
    const typeDisplayName = kb.type === 'text' ? '文本知识库' : kb.type === 'image' ? '图片知识库' : kb.type
    
    // 显示知识库详情
    ElMessageBox.alert(
      `<div>
        <h3>知识库: ${kb.name}</h3>
        <p><strong>类型:</strong> ${typeDisplayName}</p>
        <p><strong>描述:</strong> ${kb.description || '无'}</p>
        <p><strong>创建时间:</strong> ${kb.createdAt}</p>
        <h4>文件列表:</h4>
        ${documents.length > 0 ? 
          `<ul>
            ${documents.map(doc => `
              <li>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                  <span>${doc.filename}</span>
                  <a href="javascript:void(0)" @click="previewDocument(kb.id, doc.id)" style="margin-left: 10px; color: #409eff;">预览</a>
                  <span>${Math.round(doc.size/1024)}KB</span>
                </div>
                <small style="color: #909399">上传时间: ${doc.upload_time}</small>
              </li>`).join('')}
          </ul>` : 
          '<p>暂无文件</p>'
        }
      </div>`,
      '知识库详情',
      {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '确定',
        customClass: 'kb-detail-dialog'
      }
    )
  } catch (error) {
    console.error('获取知识库详情失败:', error)
    ElMessage.error('获取知识库详情失败，请稍后重试')
  }
}

// 处理知识库选择变化
const handleKnowledgeBaseChange = (kbId: string) => {
  const kb = knowledgeBases.value.find(item => item.id === kbId)
  if (kb) {
    selectedKnowledgeBaseType.value = kb.type
    // 清空上传文件列表
    uploadFiles.value = []
  }
}

// 处理文本文件上传
const handleTextFileChange = (file: any) => {
  // 文本类型验证
  const allowedTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/markdown']
  const allowedExtensions = ['.pdf', '.txt', '.docx', '.md']
  
  const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
  const isAllowedType = allowedTypes.includes(file.raw.type) || 
                         allowedExtensions.includes(fileExtension)
                      
  // 文件大小验证 (10MB)
  const isLessThan10M = file.raw.size / 1024 / 1024 < 10
  
  if (!isAllowedType) {
    ElMessage.error('不支持的文件类型，请上传PDF、TXT、DOCX或MD文件')
    return false
  }
  
  if (!isLessThan10M) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }
  
  uploadFiles.value.push(file.raw)
  return false // 阻止自动上传
}

// 处理图片文件上传
const handleImageFileChange = (file: any) => {
  // 图片类型验证
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  
  // 文件大小验证 (5MB)
  const isLessThan5M = file.raw.size / 1024 / 1024 < 5
  
  if (!allowedTypes.includes(file.raw.type)) {
    ElMessage.error('不支持的图片格式，请上传JPG、PNG、GIF或WEBP图片')
    return false
  }
  
  if (!isLessThan5M) {
    ElMessage.error('图片大小不能超过5MB')
    return false
  }
  
  uploadFiles.value.push(file.raw)
  return false // 阻止自动上传
}

// 上传文件到知识库
const uploadKnowledgeFiles = async () => {
  if (!selectedUploadKnowledgeBaseId.value) {
    ElMessage.warning('请选择知识库')
    return
  }
  
  if (uploadFiles.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }
  
  try {
    const formData = new FormData()
    
    // 添加所有文件
    uploadFiles.value.forEach(file => {
      formData.append('files', file)
    })
    
    // 添加知识库类型
    formData.append('type', selectedKnowledgeBaseType.value)
    
    const response = await fetch(`/knowledgebase/${selectedUploadKnowledgeBaseId.value}/upload`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('上传文件失败')
    }
    
    const result = await response.json()
    
    // 重置表单
    uploadFiles.value = []
    selectedUploadKnowledgeBaseId.value = ''
    selectedKnowledgeBaseType.value = ''
    uploadKnowledgeDialogVisible.value = false
    
    // 刷新知识库列表
    await fetchKnowledgeBases(true)
    
    ElMessage.success(`上传成功，共${result.uploaded_count}个文件`)
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败，请稍后重试')
  }
}

// 删除知识库
const deleteKnowledgeBase = async (kb: any) => {
  try {
    const response = await fetch('/deleteKnowledgeBase', {
      method: 'POST',
      body: JSON.stringify({ id: kb.id })
    });
    
    if (!response.ok || response.status !== 200) {
      throw new Error('删除知识库失败')
    }

    const result = await response.json()

    if (result.success) {
      // 删除成功后更新知识库列表
      knowledgeBases.value = knowledgeBases.value.filter(k => k.id !== kb.id)
      removeKnowledgeBase(kb.id)
      ElMessage.success('知识库删除成功')
    } else {
      ElMessage.error('删除知识库失败，请稍后重试')
    }

  } catch {
    ElMessage.error('删除知识库失败，请稍后重试')
  }
}

// 获取知识库列表
const fetchKnowledgeBases = async (forceRefresh = false) => {
  if (knowledgeBasesLoaded.value && !forceRefresh) return
  
  try {
    
    const response = await fetch('/fetch_knowledgebases', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error('获取知识库列表失败')
    }
    
    const data = await response.json()
    knowledgeBases.value = data.knowledgeBases || []
    knowledgeBasesLoaded.value = true
  } catch (error) {
    console.error('获取知识库列表失败:', error)
    ElMessage.error('获取知识库列表失败，请稍后重试')
  }
}

// 监听知识库配置步骤激活
watch(() => props.agentData, () => {
  console.log('Agent数据变化')
}, { deep: true })

// 监听active属性变化
watch(() => props.active, (isActive) => {
  if (isActive && !knowledgeBasesLoaded.value) {
    fetchKnowledgeBases()
  }
}, { immediate: true })
</script>

<style scoped>
.knowledge-base-config {
  width: 100%;
}

.description {
  color: #606266;
  margin-bottom: 20px;
}

.search-container {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.selected-knowledge-bases {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.selected-knowledge-bases h4 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
}

.knowledge-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.knowledge-tag {
  padding: 6px 10px;
  font-size: 14px;
}

.knowledge-base-actions {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.knowledge-base-list {
  margin-bottom: 20px;
}

.knowledge-base-list h4 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
}

.el-form-item-description {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

:deep(.el-dialog__body) {
  padding-top: 10px;
}

:deep(.el-upload-list) {
  margin-top: 10px;
}

:deep(.el-upload--picture-card) {
  --el-upload-picture-card-size: 120px;
}
</style>