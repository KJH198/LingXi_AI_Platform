
<template>
    <div class="drafts-container">
      <el-page-header @back="goBack" title="我的智能体草稿"></el-page-header>
      
      <div class="drafts-content">
        <el-empty v-if="loading" description="加载中...">
          <template #image>
            <el-icon :size="60"><Loading /></el-icon>
          </template>
        </el-empty>
        
        <el-empty v-else-if="drafts.length === 0" description="暂无草稿"></el-empty>
        
        <div v-else class="drafts-grid">
          <el-card v-for="draft in drafts" :key="draft.id" class="draft-card" shadow="hover">
            <div class="draft-header">
              <h3>{{ draft.name }}</h3>
              <el-dropdown @command="handleCommand($event, draft)">
                <el-button type="text" icon="more"></el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit">编辑</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            
            <div class="draft-content">
              <p class="draft-desc">{{ draft.description || '暂无描述' }}</p>
              
              <div class="draft-info">
                <div class="draft-model">
                  <span class="label">模型:</span> 
                  <span>{{ getModelName(draft.model_id) || '未选择' }}</span>
                </div>
                
                <div class="draft-time">
                  <el-icon><Timer /></el-icon>
                  <span>{{ formatTime(draft.updated_at) }}</span>
                </div>
              </div>
            </div>
            
            <div class="draft-footer">
              <el-button type="primary" @click="editDraft(draft.id)">继续编辑</el-button>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { Timer, Loading } from '@element-plus/icons-vue'
  
  const router = useRouter()
  const drafts = ref([])
  const loading = ref(true)
  
  // 获取草稿列表
  const fetchDrafts = async () => {
    try {
      loading.value = true
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        router.push('/login')
        return
      }
      
      const response = await fetch('/user/agent/draft', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('获取草稿列表失败')
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        drafts.value = result.data
      } else {
        throw new Error(result.message || '获取草稿列表失败')
      }
    } catch (error) {
      console.error('获取草稿列表失败:', error)
      ElMessage.error('获取草稿列表失败，请稍后重试')
    } finally {
      loading.value = false
    }
  }
  
  // 返回上一页
  const goBack = () => {
    router.go(-1)
  }
  
  // 获取模型名称
  const getModelName = (modelId) => {
    const models = {
      'gpt-4': 'GPT-4',
      'claude-3': 'Claude 3',
      'llama-3': 'LLaMA 3',
      'qwen-max': '通义千问'
    }
    return models[modelId] || modelId
  }
  
  // 格式化时间
  const formatTime = (timeString) => {
    if (!timeString) return '未知时间'
    const date = new Date(timeString)
    return date.toLocaleString()
  }
  
  // 处理下拉菜单命令
  const handleCommand = (command, draft) => {
    if (command === 'edit') {
      editDraft(draft.id)
    } else if (command === 'delete') {
      deleteDraft(draft.id)
    }
  }
  
  // 编辑草稿
  const editDraft = (draftId) => {
    router.push(`/edit-agent/draft/${draftId}`)
  }
  
  // 发布草稿
  const publishDraft = (draftId) => {
    // 设置标志，表示这是从草稿直接发布
    localStorage.setItem('publishFromDraft', 'true')
    // 跳转到发布页面
    router.push(`/edit-agent/publish/${draftId}`)
  }
  
  // 删除草稿
  const deleteDraft = async (draftId) => {
    try {
      await ElMessageBox.confirm(
        '确定要删除这个草稿吗？删除后将无法恢复。',
        '删除草稿',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        return
      }
      
      const response = await fetch(`/user/agent/draft/${draftId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('删除草稿失败')
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        ElMessage.success('草稿已删除')
        fetchDrafts() // 重新加载草稿列表
      } else {
        throw new Error(result.message || '删除草稿失败')
      }
    } catch (error) {
      if (error === 'cancel') return
      
      console.error('删除草稿失败:', error)
      ElMessage.error('删除草稿失败，请稍后重试')
    }
  }
  
  onMounted(() => {
    fetchDrafts()
  })
  </script>
  
  <style scoped>
  .drafts-container {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .drafts-content {
    margin-top: 20px;
  }
  
  .drafts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }
  
  .draft-card {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .draft-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .draft-header h3 {
    margin: 0;
    font-size: 18px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .draft-content {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .draft-desc {
    flex: 1;
    color: #606266;
    font-size: 14px;
    margin-bottom: 10px;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  
  .draft-info {
    margin-bottom: 10px;
  }
  
  .draft-model {
    font-size: 13px;
    color: #606266;
    margin-bottom: 5px;
  }
  
  .label {
    color: #909399;
  }
  
  .draft-time {
    font-size: 12px;
    color: #909399;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  
  .draft-footer {
    display: flex;
    gap: 10px;
  }
  </style>