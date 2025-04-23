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
        <el-table-column fixed="right" label="操作" width="200">
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
            <el-button 
              link 
              type="danger" 
              size="small" 
              @click="deleteKnowledgeBase(scope.row)"
            >
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

// 类型定义
interface AgentDataType {
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

interface KnowledgeBaseType {
  id: string;
  name: string;
  description: string;
  type: string;
  status?: string;
  createdAt: string;
  updatedAt?: string;
  isOwner?: boolean;
}

interface KnowledgeBaseFileType {
  id: string;
  filename: string;
  size: number;
  upload_time: string;
  status: string;
}

interface NewKnowledgeBaseType {
  name: string;
  description: string;
  type: string;
}

// Props 和 Emits
const props = defineProps<{
  agentData: AgentDataType;
  active: boolean;
}>();

const emit = defineEmits(['update:knowledgeBases']);

// 知识库列表
const knowledgeBases = ref<KnowledgeBaseType[]>([]);

// 知识库详情对话框相关状态
const knowledgeBaseDetailVisible = ref(false);
const currentKnowledgeBase = ref<KnowledgeBaseType>({
  id: '',
  name: '',
  description: '',
  type: '',
  status: '',
  createdAt: ''
});
const knowledgeBaseFiles = ref<KnowledgeBaseFileType[]>([]);
const loadingDetail = ref(false);

// 文件预览相关状态
const filePreviewVisible = ref(false);
const currentPreviewFile = ref<KnowledgeBaseFileType | null>(null);
const previewContent = ref('');
const previewLoading = ref(false);

// 添加缓存标记
const knowledgeBasesLoaded = ref(false);

// 搜索与过滤
const searchQuery = ref('');
const typeFilter = ref('');

const searchKnowledgeBases = (): void => {
  console.log('搜索知识库:', searchQuery.value);
  // 实际应用中可以在这里调用API或过滤数据
};

const filterKnowledgeBases = (): void => {
  console.log('过滤知识库类型:', typeFilter.value);
  // 实际应用中可以在这里调用API或过滤数据
};

// 对话框控制
const createKnowledgeDialogVisible = ref(false);
const uploadKnowledgeDialogVisible = ref(false);

// 创建新知识库数据
const newKnowledgeBase = reactive<NewKnowledgeBaseType>({
  name: '',
  description: '',
  type: 'text' // 默认为文本类型
});

// 上传文件相关
const selectedUploadKnowledgeBaseId = ref('');
const selectedKnowledgeBaseType = ref('');
const uploadFiles = ref<File[]>([]);

// 获取已选择知识库的详细信息
const selectedKnowledgeBasesInfo = computed(() => {
  return props.agentData.knowledgeBases
    .map(id => knowledgeBases.value.find(kb => kb.id === id))
    .filter(kb => kb !== undefined) as KnowledgeBaseType[];
});

// 计算属性：是否可以上传
const canUpload = computed(() => {
  if (!selectedUploadKnowledgeBaseId.value) return false;
  return uploadFiles.value.length > 0;
});

// 检查知识库是否被选择
const isKnowledgeBaseSelected = (id: string): boolean => {
  return props.agentData.knowledgeBases.includes(id);
};

// 添加或移除知识库
const toggleKnowledgeBase = (kb: KnowledgeBaseType): void => {
  if (isKnowledgeBaseSelected(kb.id)) {
    removeKnowledgeBase(kb.id);
  } else {
    addKnowledgeBase(kb.id);
  }
};

const addKnowledgeBase = (id: string): void => {
  if (!props.agentData.knowledgeBases.includes(id)) {
    const newKnowledgeBases = [...props.agentData.knowledgeBases, id];
    emit('update:knowledgeBases', newKnowledgeBases);
  }
};

const removeKnowledgeBase = (id: string): void => {
  const newKnowledgeBases = props.agentData.knowledgeBases.filter(kbId => kbId !== id);
  emit('update:knowledgeBases', newKnowledgeBases);
};

// 创建知识库
const createKnowledgeBase = async (): Promise<void> => {
  if (!newKnowledgeBase.name) {
    ElMessage.warning('请输入知识库名称');
    return;
  }
  
  if (!newKnowledgeBase.type) {
    ElMessage.warning('请选择知识库类型');
    return;
  }
  
  try {
    // 获取认证 token
    const token = localStorage.getItem('token');
    if (!token) {
      ElMessage.error('请先登录');
      return;
    }
    
    const response = await fetch('/knowledge_base/create_knowledgebase/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`  // 添加认证 token
      },
      body: JSON.stringify({
        name: newKnowledgeBase.name,
        description: newKnowledgeBase.description,
        type: newKnowledgeBase.type
      })
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        ElMessage.error('认证失败，请重新登录');
        return;
      }
      throw new Error('创建知识库失败');
    }
    
    const result = await response.json();
    
    // 添加到知识库列表
    knowledgeBases.value.push({
      id: result.id,
      name: result.name,
      description: result.description,
      type: result.type,
      createdAt: result.createdAt
    });
    
    // 自动选择新创建的知识库
    addKnowledgeBase(result.id);
    
    // 重置表单
    newKnowledgeBase.name = '';
    newKnowledgeBase.description = '';
    newKnowledgeBase.type = 'text';
    createKnowledgeDialogVisible.value = false;
    
    ElMessage.success('知识库创建成功');
  } catch (error) {
    console.error('创建知识库失败:', error);
    ElMessage.error('创建知识库失败，请稍后重试');
  }
};

// 查看知识库详情
const viewKnowledgeBase = async (kb: KnowledgeBaseType): Promise<void> => {
  try {
    loadingDetail.value = true;
    knowledgeBaseDetailVisible.value = true;
    
    // 先设置基本信息，让对话框有内容显示
    currentKnowledgeBase.value = kb;
    knowledgeBaseFiles.value = [];
    
    // 获取认证 token
    const token = localStorage.getItem('token');
    if (!token) {
      ElMessage.error('请先登录');
      return;
    }
    
    const response = await fetch(`/knowledge_base/knowledgebase/${kb.id}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`  // 添加认证 token
      }
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        ElMessage.error('认证失败，请重新登录');
        return;
      }
      throw new Error('获取知识库详情失败');
    }
    
    const data = await response.json();
    
    // 更新知识库详情和文件列表
    console.log('知识库详情:', data);
    currentKnowledgeBase.value = {
      id: data.id,
      name: data.name,
      description: data.description,
      type: data.type,
      status: data.status,
      createdAt: data.createdAt
    };
    knowledgeBaseFiles.value = data.files || [];
  } catch (error) {
    console.error('获取知识库详情失败:', error);
    ElMessage.error('获取知识库详情失败，请稍后重试');
  } finally {
    loadingDetail.value = false;
  }
};

// 预览文件
const previewFile = async (file: KnowledgeBaseFileType): Promise<void> => {
  try {
    previewLoading.value = true;
    filePreviewVisible.value = true;
    currentPreviewFile.value = file;
    previewContent.value = '';
    
    // 获取认证 token
    const token = localStorage.getItem('token');
    if (!token) {
      ElMessage.error('请先登录');
      return;
    }
    
    const response = await fetch(`/knowledge_base/knowledgebase/${currentKnowledgeBase.value.id}/file/${file.id}/content/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`  // 添加认证 token
      }
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        ElMessage.error('认证失败，请重新登录');
        return;
      }
      throw new Error('获取文件内容失败');
    }
    
    const result = await response.json();
    
    if (result.code === 200) {
      previewContent.value = result.data.content;
    } else {
      throw new Error(result.message || '获取文件内容失败');
    }
  } catch (error) {
    console.error('预览文件失败:', error);
    ElMessage.error('预览文件失败，请稍后重试');
  } finally {
    previewLoading.value = false;
  }
};

// 删除文件
const deleteFile = async (file: KnowledgeBaseFileType): Promise<void> => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件"${file.filename}"吗？删除后将无法恢复。`,
      '删除文件',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    // 获取认证 token
    const token = localStorage.getItem('token');
    if (!token) {
      ElMessage.error('请先登录');
      return;
    }
    
    const response = await fetch(`/knowledge_base/knowledgebase/${currentKnowledgeBase.value.id}/delete_file/${file.id}/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`  // 添加认证 token
      }
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        ElMessage.error('认证失败，请重新登录');
        return;
      }
      throw new Error('删除文件失败');
    }
    
    const result = await response.json();
    
    if (result.code === 200) {
      ElMessage.success('文件删除成功');
      
      // 更新文件列表
      knowledgeBaseFiles.value = knowledgeBaseFiles.value.filter(f => f.id !== file.id);
      
      // 如果删除后文件列表为空，刷新知识库列表
      if (knowledgeBaseFiles.value.length === 0) {
        fetchKnowledgeBases(true);
      }
    } else {
      throw new Error(result.message || '删除文件失败');
    }
  } catch (error) {
    if (error === 'cancel') return;
    
    console.error('删除文件失败:', error);
    ElMessage.error('删除文件失败，请稍后重试');
  }
};

// 处理知识库选择变化
const handleKnowledgeBaseChange = (kbId: string): void => {
  const kb = knowledgeBases.value.find(item => item.id === kbId);
  if (kb) {
    selectedKnowledgeBaseType.value = kb.type;
    // 清空上传文件列表
    uploadFiles.value = [];
  }
};

// 处理文本文件上传
const handleTextFileChange = (file: any): boolean => {
  // 文本类型验证
  const allowedTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/markdown'];
  const allowedExtensions = ['.pdf', '.txt', '.docx', '.md'];
  
  const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
  const isAllowedType = allowedTypes.includes(file.raw.type) || 
                         allowedExtensions.includes(fileExtension);
                      
  // 文件大小验证 (10MB)
  const isLessThan10M = file.raw.size / 1024 / 1024 < 10;
  
  if (!isAllowedType) {
    ElMessage.error('不支持的文件类型，请上传PDF、TXT、DOCX或MD文件');
    return false;
  }
  
  if (!isLessThan10M) {
    ElMessage.error('文件大小不能超过10MB');
    return false;
  }
  
  uploadFiles.value.push(file.raw);
  return false; // 阻止自动上传
};

// 处理图片文件上传
const handleImageFileChange = (file: any): boolean => {
  // 图片类型验证
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  
  // 文件大小验证 (5MB)
  const isLessThan5M = file.raw.size / 1024 / 1024 < 5;
  
  if (!allowedTypes.includes(file.raw.type)) {
    ElMessage.error('不支持的图片格式，请上传JPG、PNG、GIF或WEBP图片');
    return false;
  }
  
  if (!isLessThan5M) {
    ElMessage.error('图片大小不能超过5MB');
    return false;
  }
  
  uploadFiles.value.push(file.raw);
  return false; // 阻止自动上传
};

// 上传文件到知识库
const uploadKnowledgeFiles = async (): Promise<void> => {
  if (!selectedUploadKnowledgeBaseId.value) {
    ElMessage.warning('请选择知识库');
    return;
  }
  
  if (uploadFiles.value.length === 0) {
    ElMessage.warning('请选择要上传的文件');
    return;
  }
  
  try {
    // 获取认证 token
    const token = localStorage.getItem('token');
    if (!token) {
      ElMessage.error('请先登录');
      return;
    }
    
    const formData = new FormData();
    const uploaded_count = uploadFiles.value.length;

    // 添加所有文件
    uploadFiles.value.forEach(file => {
      formData.append('files', file);
    });
    
    // 添加知识库类型
    formData.append('type', selectedKnowledgeBaseType.value);
    formData.append('knowledgeBaseId', selectedUploadKnowledgeBaseId.value);
    
    const response = await fetch(`/knowledge_base/knowledgebase/${selectedUploadKnowledgeBaseId.value}/upload/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`  // 添加认证 token
        // 注意：这里不要设置 'Content-Type'，因为 FormData 会自动设置为 multipart/form-data
      },
      body: formData
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        ElMessage.error('认证失败，请重新登录');
        return;
      }
      throw new Error('上传文件失败');
    }
    
    const result = await response.json();
    
    // 重置表单
    uploadFiles.value = [];
    selectedUploadKnowledgeBaseId.value = '';
    selectedKnowledgeBaseType.value = '';
    uploadKnowledgeDialogVisible.value = false;
    
    // 刷新知识库列表
    await fetchKnowledgeBases(true);
    
    ElMessage.success(`上传成功，共${uploaded_count}个文件`);
  } catch (error) {
    console.error('上传失败:', error);
    ElMessage.error('上传失败，请稍后重试');
  }
};

// 删除知识库
const deleteKnowledgeBase = async (kb: KnowledgeBaseType): Promise<void> => {
  try {
    await ElMessageBox.confirm(
      `确定要删除知识库"${kb.name}"吗？删除后将无法恢复，且将从所有使用该知识库的智能体中移除。`,
      '删除知识库',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    // 获取认证 token
    const token = localStorage.getItem('token');
    if (!token) {
      ElMessage.error('请先登录');
      return;
    }
    
    const response = await fetch(`/knowledge_base/delete_knowledgebase/${kb.id}/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`  // 添加认证 token
      }
    });
    
    if (!response.ok || response.status !== 200) {
      if (response.status === 401) {
        ElMessage.error('认证失败，请重新登录');
        return;
      }
      throw new Error('删除知识库失败');
    }

    const result = await response.json();

    if (result.code === 200) {
      // 删除成功后更新知识库列表
      knowledgeBases.value = knowledgeBases.value.filter(k => k.id !== kb.id);
      removeKnowledgeBase(kb.id);
      ElMessage.success('知识库删除成功');
    } else {
      throw new Error(result.message || '删除知识库失败');
    }

  } catch (error) {
    if (error === 'cancel') return;
    
    console.error('删除知识库失败:', error);
    ElMessage.error('删除知识库失败，请稍后重试');
  }
};

// 获取知识库列表
const fetchKnowledgeBases = async (forceRefresh = false): Promise<void> => {
  if (knowledgeBasesLoaded.value && !forceRefresh) return;
  
  try {
    // 获取认证 token
    const token = localStorage.getItem('token');
    if (!token) {
      ElMessage.error('请先登录');
      return;
    }
    
    const response = await fetch('/knowledge_base/fetch_knowledgebases/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`  // 添加认证 token
      }
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        ElMessage.error('认证失败，请重新登录');
        return;
      }
      throw new Error('获取知识库列表失败');
    }
    
    const data = await response.json();
    console.log('知识库列表:', data);
    knowledgeBases.value = data || [];
    console.log('知识库列表:', knowledgeBases.value);
    knowledgeBasesLoaded.value = true;
  } catch (error) {
    console.error('获取知识库列表失败:', error);
    ElMessage.error('获取知识库列表失败，请稍后重试');
  }
};

// 监听知识库配置步骤激活
watch(() => props.agentData, () => {
  console.log('Agent数据变化');
}, { deep: true });

// 监听active属性变化
watch(() => props.active, (isActive) => {
  if (isActive && !knowledgeBasesLoaded.value) {
    fetchKnowledgeBases();
  }
}, { immediate: true });
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

/* 知识库详情样式 */
.kb-detail-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.kb-files {
  margin-top: 20px;
}

.kb-files h4 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
}

.empty-files {
  background-color: #f8f8f8;
  padding: 20px;
  border-radius: 4px;
  text-align: center;
}

/* 文件预览样式 */
.file-preview {
  max-height: 500px;
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
</style>