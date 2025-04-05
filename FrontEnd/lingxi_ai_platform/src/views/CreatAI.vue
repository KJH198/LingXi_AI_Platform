<template>
  <div class="workflow-container">
    <div class="workflow-header">
      <h2>工作流设计器</h2>
      <div class="header-actions">
        <el-button type="primary" @click="saveWorkflow">保存</el-button>
        <el-button @click="clearWorkflow">清空</el-button>
      </div>
    </div>
    
    <div class="workflow-content">
      <VueFlow
        v-model="elements"
        :default-viewport="{ x: 0, y: 0, zoom: 1.5 }"
        :min-zoom="0.2"
        :max-zoom="4"
        class="flow-container"
        @connect="onConnect"
        @node-click="onNodeClick"
        @node-drag-stop="onNodeDragStop"
      >
        <Background pattern-color="#aaa" gap="8" />
        <Controls />
        <MiniMap />
        
        <Panel position="top-right" class="node-panel">
          <el-button-group>
            <el-button @click="addNode('input')" type="primary">
              <el-icon><Upload /></el-icon>
              输入节点
            </el-button>
            <el-button @click="addNode('process')" type="success">
              <el-icon><Operation /></el-icon>
              处理节点
            </el-button>
            <el-button @click="addNode('output')" type="warning">
              <el-icon><Download /></el-icon>
              输出节点
            </el-button>
          </el-button-group>
        </Panel>

        <Panel position="bottom-right" class="info-panel">
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="节点数量">
              {{ nodeCount }}
            </el-descriptions-item>
            <el-descriptions-item label="连接数量">
              {{ edgeCount }}
            </el-descriptions-item>
          </el-descriptions>
        </Panel>
      </VueFlow>

      <!-- 节点配置抽屉 -->
      <el-drawer
        v-model="drawerVisible"
        title="节点配置"
        direction="rtl"
        size="400px"
      >
        <el-form :model="nodeForm" label-width="80px">
          <el-form-item label="节点名称">
            <el-input v-model="nodeForm.name" />
          </el-form-item>
          <el-form-item label="节点类型">
            <el-select v-model="nodeForm.type" disabled>
              <el-option label="输入节点" value="input" />
              <el-option label="处理节点" value="process" />
              <el-option label="输出节点" value="output" />
            </el-select>
          </el-form-item>
          <el-form-item label="节点描述">
            <el-input
              v-model="nodeForm.description"
              type="textarea"
              :rows="3"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="updateNode">更新</el-button>
            <el-button type="danger" @click="deleteNode">删除</el-button>
          </el-form-item>
        </el-form>
      </el-drawer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { Panel } from '@vue-flow/core'
import { ElMessage } from 'element-plus'
import { Upload, Operation, Download } from '@element-plus/icons-vue'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

// 工作流元素
const elements = ref([])
const drawerVisible = ref(false)
const selectedNode = ref(null)

// 节点表单
const nodeForm = ref({
  name: '',
  type: '',
  description: ''
})

// 统计信息
const nodeCount = computed(() => elements.value.filter(el => el.type === 'custom').length)
const edgeCount = computed(() => elements.value.filter(el => el.type === 'smoothstep').length)

// 添加节点
const addNode = (type) => {
  const id = `${type}-${Date.now()}`
  const position = { x: Math.random() * 400, y: Math.random() * 400 }
  
  elements.value.push({
    id,
    type: 'custom',
    position,
    data: {
      label: `${type}节点`,
      type,
      description: ''
    }
  })
}

// 更新节点
const updateNode = () => {
  if (!selectedNode.value) return
  
  const node = elements.value.find(el => el.id === selectedNode.value)
  if (node) {
    node.data = {
      ...node.data,
      label: nodeForm.value.name || node.data.label,
      description: nodeForm.value.description
    }
    ElMessage.success('节点更新成功')
  }
}

// 删除节点
const deleteNode = () => {
  if (!selectedNode.value) return
  
  elements.value = elements.value.filter(el => 
    el.id !== selectedNode.value && 
    !(el.source === selectedNode.value || el.target === selectedNode.value)
  )
  selectedNode.value = null
  drawerVisible.value = false
  ElMessage.success('节点删除成功')
}

// 节点点击事件
const onNodeClick = (event, node) => {
  selectedNode.value = node.id
  nodeForm.value = {
    name: node.data.label,
    type: node.data.type,
    description: node.data.description || ''
  }
  drawerVisible.value = true
}

// 节点拖拽结束事件
const onNodeDragStop = (event, node) => {
  // 可以在这里添加节点位置保存逻辑
  console.log('节点位置更新:', node.position)
}

// 连接事件
const onConnect = (params) => {
  elements.value.push({
    id: `edge-${params.source}-${params.target}`,
    source: params.source,
    target: params.target,
    type: 'smoothstep',
    animated: true
  })
}

// 保存工作流
const saveWorkflow = () => {
  const workflowData = {
    nodes: elements.value.filter(el => el.type === 'custom'),
    edges: elements.value.filter(el => el.type === 'smoothstep')
  }
  console.log('工作流数据:', workflowData)
  ElMessage.success('工作流保存成功')
}

// 清空工作流
const clearWorkflow = () => {
  elements.value = []
  selectedNode.value = null
  drawerVisible.value = false
  ElMessage.warning('工作流已清空')
}
</script>

<style scoped>
.workflow-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.workflow-header {
  padding: 15px 20px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.workflow-content {
  flex: 1;
  position: relative;
  padding: 20px;
}

.flow-container {
  height: 100%;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.node-panel {
  background: #fff;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.info-panel {
  background: #fff;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

:deep(.vue-flow__node) {
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #fff;
  text-align: center;
  border-width: 1px;
  border-style: solid;
}

:deep(.vue-flow__node[data-type="input"]) {
  background: #409eff;
  border-color: #409eff;
}

:deep(.vue-flow__node[data-type="process"]) {
  background: #67c23a;
  border-color: #67c23a;
}

:deep(.vue-flow__node[data-type="output"]) {
  background: #e6a23c;
  border-color: #e6a23c;
}

:deep(.vue-flow__edge-path) {
  stroke: #b1b1b7;
  stroke-width: 2;
}

:deep(.vue-flow__edge.animated path) {
  stroke-dasharray: 5;
  animation: dashdraw 0.5s linear infinite;
}

@keyframes dashdraw {
  from {
    stroke-dashoffset: 10;
  }
}
</style>
