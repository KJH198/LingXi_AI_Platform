<template>
  <div class="agent-list-container">
    <div class="page-header">
      <h2>选择智能体</h2>
      <el-button @click="goBack">
        <el-icon><Back /></el-icon>
        返回
      </el-button>
    </div>

    <el-tabs v-model="activeTab" class="agent-tabs">
      <el-tab-pane label="我的智能体" name="my">
        <el-table
          :data="myAgents"
          style="width: 100%"
          @row-click="handleSelectAgent"
          :row-class-name="getRowClassName"
        >
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="createTime" label="创建时间" width="180" />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                link
                @click.stop="handleSelectAgent(row)"
              >
                选择
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="我关注的" name="followed">
        <el-table
          :data="followedAgents"
          style="width: 100%"
          @row-click="handleSelectAgent"
          :row-class-name="getRowClassName"
        >
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="createTime" label="创建时间" width="180" />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                link
                @click.stop="handleSelectAgent(row)"
              >
                选择
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 当前激活的标签页
const activeTab = ref(route.query.type === 'followed' ? 'followed' : 'my')

// 智能体列表数据
const myAgents = ref([])
const followedAgents = ref([])

// 获取智能体列表
const fetchAgents = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }

    // 获取我的智能体列表
    const myResponse = await fetch('/user/agents/list', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (myResponse.ok) {
      const result = await myResponse.json()
      if (result.code === 200) {
        myAgents.value = result.data
      }
    }

    // 获取关注的智能体列表
    const followedResponse = await fetch('/user/followed/agents', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (followedResponse.ok) {
      const result = await followedResponse.json()
      if (result.code === 200) {
        followedAgents.value = result.data
      }
    }
  } catch (error) {
    console.error('获取智能体列表失败:', error)
    ElMessage.error('获取智能体列表失败')
  }
}

// 处理选择智能体
const handleSelectAgent = (row) => {
  // 将选中的智能体信息存储到localStorage
  localStorage.setItem('selectedAgent', JSON.stringify({
    id: row.id,
    name: row.name,
    type: activeTab.value
  }))
  
  // 返回上一页
  goBack()
}

// 返回上一页
const goBack = () => {
  const returnPath = route.query.returnPath || '/create-ai'
  router.push(returnPath)
}

// 获取行样式
const getRowClassName = ({ row }) => {
  return 'agent-table-row'
}

// 页面加载时获取数据
onMounted(() => {
  fetchAgents()
})
</script>

<style scoped>
.agent-list-container {
  padding: 20px;
  height: 100vh;
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.agent-tabs {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}

:deep(.el-tabs__item) {
  font-size: 16px;
  height: 40px;
  line-height: 40px;
}

:deep(.el-tabs__item.is-active) {
  font-weight: 500;
}

:deep(.el-table) {
  --el-table-border-color: #ebeef5;
  --el-table-header-bg-color: #f5f7fa;
}

:deep(.el-table th) {
  font-weight: 500;
  color: #606266;
  background-color: #f5f7fa;
}

:deep(.el-table td) {
  color: #606266;
}

:deep(.agent-table-row) {
  cursor: pointer;
  transition: background-color 0.3s;
}

:deep(.agent-table-row:hover) {
  background-color: #f5f7fa;
}

:deep(.el-button--primary.is-link) {
  font-weight: 500;
}

:deep(.el-button--primary.is-link:hover) {
  color: #66b1ff;
}
</style>
  