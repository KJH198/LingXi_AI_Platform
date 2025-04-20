<template>
  <div class="workflow-list-container">
    <div class="header">
      <h2>工作流配置</h2>
      <el-button type="primary" @click="createNewWorkflow">
        <el-icon><Plus /></el-icon>
        新建工作流
      </el-button>
    </div>

    <el-card shadow="hover" class="search-card">
      <div class="search-container">
        <el-input 
          v-model="searchQuery" 
          placeholder="搜索工作流" 
          prefix-icon="Search" 
          clearable 
          @clear="fetchWorkflows"
          @input="handleSearchInput"
        />
        <el-button type="primary" @click="fetchWorkflows">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
    </el-card>

    <div class="workflow-table-container">
      <el-table
        v-loading="loading"
        :data="workflows"
        style="width: 100%"
        border
        stripe
        highlight-current-row
      >
        <el-table-column prop="name" label="工作流名称" min-width="150">
          <template #default="scope">
            <span class="workflow-name">{{ scope.row.name }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="createdAt" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.createdAt) }}
          </template>
        </el-table-column>

        <el-table-column prop="updatedAt" label="更新时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.updatedAt) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="selectWorkflow(scope.row)"
            >
              选择
            </el-button>
            <el-button 
              type="default" 
              size="small" 
              @click="previewWorkflow(scope.row)"
            >
              预览
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="confirmDeleteWorkflow(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <el-empty 
        description="暂无工作流" 
        v-if="workflows.length === 0 && !loading"
      >
        <el-button type="primary" @click="createNewWorkflow">新建工作流</el-button>
      </el-empty>
    </div>

    <!-- 工作流预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="工作流预览"
      width="80%"
      destroy-on-close
    >
      <div v-loading="previewLoading" class="preview-content">
        <div v-if="previewData" class="workflow-preview">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="工作流名称">{{ previewData.name }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(previewData.createdAt) }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ formatDate(previewData.updatedAt) }}</el-descriptions-item>
            <el-descriptions-item label="节点数量">{{ previewData.nodes?.length || 0 }}</el-descriptions-item>
            <el-descriptions-item label="连接数量">{{ previewData.edges?.length || 0 }}</el-descriptions-item>
          </el-descriptions>

          <div class="nodes-preview" v-if="previewData.nodes && previewData.nodes.length > 0">
            <h3>节点列表</h3>
            <el-table :data="previewData.nodes" border stripe>
              <el-table-column prop="id" label="节点ID" width="100" />
              <el-table-column prop="type" label="节点类型" width="120">
                <template #default="scope">
                  <el-tag :type="getNodeTypeTagType(scope.row.type)">
                    {{ getNodeTypeLabel(scope.row.type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="data.label" label="节点名称" />
              <el-table-column prop="data.description" label="节点描述" />
            </el-table>
          </div>
        </div>
        <el-empty description="无法加载预览内容" v-if="!previewData && !previewLoading"></el-empty>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="previewDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="selectWorkflow(currentPreviewWorkflow)">
            选择此工作流
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { Search, Plus } from '@element-plus/icons-vue'

// 路由实例
const router = useRouter()

// 数据状态
const workflows = ref([])
const loading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 预览对话框
const previewDialogVisible = ref(false)
const previewLoading = ref(false)
const previewData = ref(null)
const currentPreviewWorkflow = ref(null)

// 获取工作流列表
const fetchWorkflows = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const response = await fetch(`/api/workflow/list?page=${currentPage.value}&pageSize=${pageSize.value}&search=${searchQuery.value}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('获取工作流列表失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      workflows.value = result.data.workflows
      total.value = result.data.total
    } else {
      throw new Error(result.message || '获取工作流列表失败')
    }
  } catch (error) {
    console.error('获取工作流列表失败:', error)
    ElMessage.error('获取工作流列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 搜索输入防抖
let searchTimeout = null
const handleSearchInput = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchWorkflows()
  }, 500)
}

// 分页处理
const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  fetchWorkflows()
}

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
  fetchWorkflows()
}

// 选择工作流
const selectWorkflow = (workflow) => {
  const workflowId = workflow.id
  
  // 关闭预览对话框（如果打开的话）
  previewDialogVisible.value = false
  
  // 触发父组件的更新事件
  emit('update:workflowId', workflowId)
  
  // 显示成功消息
  ElMessage.success(`已选择工作流：${workflow.name}`)
}

// 创建新工作流
const createNewWorkflow = () => {
  // 跳转到工作流设计器页面，不传递工作流ID
  router.push('/create-ai')
  
  // 触发父组件的更新事件，传null表示新建
  emit('update:workflowId', null)
}

// 预览工作流
const previewWorkflow = async (workflow) => {
  previewDialogVisible.value = true
  previewLoading.value = true
  currentPreviewWorkflow.value = workflow
  previewData.value = null
  
  try {
    const token = localStorage.getItem('token')
    
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const response = await fetch(`/api/workflow/${workflow.id}/preview`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('获取工作流预览失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      previewData.value = result.data
    } else {
      throw new Error(result.message || '获取工作流预览失败')
    }
  } catch (error) {
    console.error('获取工作流预览失败:', error)
    ElMessage.error('获取工作流预览失败，请稍后重试')
  } finally {
    previewLoading.value = false
  }
}

// 确认删除工作流
const confirmDeleteWorkflow = (workflow) => {
  ElMessageBox.confirm(
    `确定要删除工作流"${workflow.name}"吗？此操作将永久删除该工作流，且无法恢复。`,
    '删除工作流',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteWorkflow(workflow.id)
  }).catch(() => {
    // 用户取消删除
  })
}

// 删除工作流
const deleteWorkflow = async (workflowId) => {
  try {
    const token = localStorage.getItem('token')
    
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const response = await fetch(`/api/workflow/${workflowId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('删除工作流失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      ElMessage.success('工作流删除成功')
      fetchWorkflows() // 刷新列表
    } else {
      throw new Error(result.message || '删除工作流失败')
    }
  } catch (error) {
    console.error('删除工作流失败:', error)
    ElMessage.error('删除工作流失败，请稍后重试')
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '暂无'
  
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取节点类型标签
const getNodeTypeLabel = (type) => {
  switch (type) {
    case 'input': return '输入节点'
    case 'process': return '处理节点'
    case 'output': return '输出节点'
    default: return type
  }
}

// 获取节点类型标签样式
const getNodeTypeTagType = (type) => {
  switch (type) {
    case 'input': return 'primary'
    case 'process': return 'success'
    case 'output': return 'warning'
    default: return 'info'
  }
}

// 定义 props 和 emits
const props = defineProps({
  workflowId: {
    type: String,
    default: null
  },
  active: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:workflowId'])

// 监听 active 属性变化，当步骤激活时加载数据
watch(() => props.active, (newVal) => {
  console.log('WorkflowList active 属性变化:', newVal)
  if (newVal) {
    fetchWorkflows()
  }
}, { immediate: true }) // 立即执行一次，如果初始值为 true 则加载数据
</script>

<style scoped>
.workflow-list-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 600px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.search-card {
  margin-bottom: 20px;
}

.search-container {
  display: flex;
  gap: 12px;
}

.search-container .el-input {
  flex: 1;
}

.workflow-table-container {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.workflow-name {
  font-weight: 500;
  color: #303133;
}

.preview-content {
  min-height: 300px;
  padding: 20px 0;
}

.workflow-preview {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.nodes-preview {
  margin-top: 20px;
}

.nodes-preview h3 {
  margin-bottom: 12px;
  font-size: 16px;
  color: #303133;
}

:deep(.el-descriptions__label) {
  width: 120px;
  font-weight: 500;
}

:deep(.el-descriptions__content) {
  font-size: 14px;
}

:deep(.el-tag) {
  font-weight: 500;
}

:deep(.el-empty) {
  padding: 40px 0;
}
</style>