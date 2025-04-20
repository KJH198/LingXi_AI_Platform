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
      >
        <el-table-column prop="name" label="工作流名称" min-width="200">
          <template #default="scope">
            <span class="workflow-name">{{ scope.row.name }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="selectWorkflow(scope.row)"
            >
              使用
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
      workflows.value = result.data
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
  ElMessage.success(`已恢复工作流：${workflow.name}`)
  
  // 跳转到工作流设计器，携带工作流ID
  router.push({
    path: '/workflow-editor',
    query: { id: workflowId }
  })
}

// 创建新工作流
const createNewWorkflow = () => {
  // 清除之前选择的工作流
  localStorage.removeItem('selectedWorkflowId')
  localStorage.removeItem('selectedWorkflowName')
  
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
    fetchWorkflows()
  }
}, { immediate: true }) // 立即执行一次，如果初始值为 true 则加载数据
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
</style>