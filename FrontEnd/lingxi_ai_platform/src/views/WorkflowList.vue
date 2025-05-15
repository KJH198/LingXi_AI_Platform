<template>
  <div class="workflow-list-container">
    <div class="header">
      <h2>工作流配置</h2>
      <el-button type="primary" @click="createNewWorkflow">
        <el-icon><Plus /></el-icon>
        新建工作流
      </el-button>
    </div>

    <div class="workflow-table-container">
      <el-table
        v-loading="loading"
        :data="workflows"
        style="width: 100%"
        border
        stripe
        highlight-current-row
        :row-class-name="tableRowClassName"
      >
      <el-table-column prop="name" label="工作流名称" min-width="200">
        <template #default="scope">
          <div class="workflow-name-container">
            <span class="workflow-name">{{ scope.row.name }}</span>
            <el-tag 
              size="small" 
              type="success" 
              v-if="String(scope.row.id) === String(currentSelectedWorkflowId)"
            >
              当前使用
            </el-tag>
          </div>
        </template>
      </el-table-column>

        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button 
              :type="String(scope.row.id) === String(currentSelectedWorkflowId) ? 'success' : 'primary'" 
              size="small" 
              @click="selectWorkflow(scope.row)"
            >
              {{ String(scope.row.id) === String(currentSelectedWorkflowId) ? '已选择' : '使用' }}
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="restoreWorkflow(scope.row)"
            >
              编辑
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

      <el-empty 
        description="暂无工作流" 
        v-if="workflows.length === 0 && !loading"
      >
        <el-button type="primary" @click="createNewWorkflow">新建工作流</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'

// 路由实例
const router = useRouter()

// 数据状态
const workflows = ref([])
const loading = ref(false)
const total = ref(0)

const currentSelectedWorkflowId = ref(localStorage.getItem('selectedWorkflowId') || null)

const tableRowClassName = ({ row }) => {
  if (row.id === currentSelectedWorkflowId.value) {
    return 'selected-workflow-row'
  }
  return ''
}
// 获取工作流列表
const fetchWorkflows = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const response = await fetch('/agent/workflows/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      if (response.status === 401) {
        ElMessage.error('认证失败，请重新登录')
        return
      }
      throw new Error('获取工作流列表失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200 && result.data) {
      // 获取当前选择的工作流ID
      const selectedWorkflowId = currentSelectedWorkflowId.value
      
      if (selectedWorkflowId) {
        // 先用接口返回的工作流列表
        let workflowList = result.data
        // 记录已存在的工作流ID
        const workflowListIds = workflowList.map(wf => String(wf.id))
        
        // 如果选中的工作流不在列表中，获取其详情
        if (!workflowListIds.includes(String(selectedWorkflowId))) {
          try {
            const wfResponse = await fetch(`/agent/workflow/${selectedWorkflowId}/`, {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            })
            if (wfResponse.ok) {
              const wfData = await wfResponse.json()
              if (wfData.code === 200 && wfData.data) {
                // 将选中的工作流添加到列表最前面
                workflowList = [wfData.data, ...workflowList]
              }
            }
          } catch (error) {
            console.error(`获取工作流 ${selectedWorkflowId} 详情失败:`, error)
          }
        }
        
        workflows.value = workflowList
      } else {
        workflows.value = result.data
      }
    } else {
      throw new Error(result.message || '获取工作流数据失败')
    }
    
    total.value = workflows.value.length

  } catch (error) {
    console.error('获取工作流列表失败:', error)
    ElMessage.error('获取工作流列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 选择工作流
const selectWorkflow = (workflow) => {
  if (!workflow || !workflow.id) {
    ElMessage.warning('无效的工作流数据')
    return
  }
  
  const workflowId = workflow.id
  
  // 将选中的工作流ID和名称保存到本地存储
  localStorage.setItem('selectedWorkflowId', workflowId)
  localStorage.setItem('selectedWorkflowName', workflow.name)
  
  // 更新当前选中的工作流ID
  currentSelectedWorkflowId.value = workflowId

  // 触发父组件的更新事件
  emit('update:workflowId', workflowId)
  
  // 显示成功消息
  ElMessage.success(`已选择工作流：${workflow.name}`)
}

// 恢复工作流
const restoreWorkflow = (workflow) => {
  if (!workflow || !workflow.id) {
    ElMessage.warning('无效的工作流数据')
    return
  }
  
  const workflowId = workflow.id
  console.log('工作流id:', workflowId)
  
  // 从localStorage恢复上次选择的工作流
  localStorage.setItem('selectedWorkflowId', workflowId)
  localStorage.setItem('selectedWorkflowName', workflow.name)
  
  // 触发父组件的更新事件
  emit('update:workflowId', workflowId)
  
  // 显示成功消息
  // ElMessage.success(`正在加载工作流：${workflow.name}`)
  
  // 跳转到工作流设计器，携带工作流ID
  router.push({
    path: '/create-ai',
    query: { id: workflowId }
  })
}

// 创建新工作流
const createNewWorkflow = () => {

  
  // 触发父组件的更新事件，传null表示新建
  emit('update:workflowId', null)
  
  // 跳转到工作流设计器页面，不传递工作流ID
  router.push('/create-ai')
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
    
    const response = await fetch(`/agent/deleteworkflow/${workflowId}`, {
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
    
    if (result.code === 200 || response.status === 200) {
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
    fetchWorkflows().then(() => {
      // 获取当前工作流ID - 优先使用父组件传入的值
      currentSelectedWorkflowId.value = props.workflowId || localStorage.getItem('selectedWorkflowId') || null
      console.log('恢复选中的工作流ID:', currentSelectedWorkflowId.value)
    })
  }
}, { immediate: true })

// 添加对 workflowId prop 的监听，确保当父组件传递新值时更新选中状态
watch(() => props.workflowId, (newVal) => {
  if (newVal) {
    currentSelectedWorkflowId.value = newVal
    console.log('通过 props 更新选中的工作流ID:', currentSelectedWorkflowId.value)
  }
}, { immediate: true })
</script>

<style scoped>
.workflow-list-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 400px;
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

.workflow-table-container {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.workflow-name {
  font-weight: 500;
  color: #303133;
}

:deep(.el-empty) {
  padding: 40px 0;
}

/* 添加选中行的样式 */
:deep(.selected-workflow-row) {
  background-color: #ecf5ff !important;
  font-weight: bold;
}

/* 当鼠标悬停在选中行上时保持高亮样式 */
:deep(.selected-workflow-row:hover > td) {
  background-color: #d9ecff !important;
}

.workflow-name-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.workflow-name {
  font-weight: 500;
  color: #303133;
}
</style>