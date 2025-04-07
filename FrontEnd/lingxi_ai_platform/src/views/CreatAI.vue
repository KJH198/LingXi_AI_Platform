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
        
        <template #node-input="nodeProps">
          <div 
            class="input-node"
            :style="{
              backgroundColor: '#f0f9ff',
              borderColor: '#409EFF'
            }"
          >
            <Handle type="source" position="bottom" :style="{ background: '#409EFF' }" />
            <el-icon :size="20" color="#409EFF">
              <Upload />
            </el-icon>
            <div class="node-label" style="color: #409EFF">
              {{ nodeProps.data.label }}
            </div>
          </div>
        </template>

        <template #node-process="nodeProps">
          <div 
            class="process-node"
            :style="{
              backgroundColor: nodeProps.data.bgColor,
              borderColor: nodeProps.data.color
            }"
          >
            <Handle type="target" position="top" :style="{ background: nodeProps.data.color }" />
            <el-icon :size="20" :style="{ color: nodeProps.data.color }">
              <component :is="nodeProps.data.icon" />
            </el-icon>
            <div class="node-label" :style="{ color: nodeProps.data.color }">
              {{ nodeProps.data.label }}
            </div>
            <Handle type="source" position="bottom" :style="{ background: nodeProps.data.color }" />
          </div>
        </template>

        <template #node-output="nodeProps">
          <div 
            class="output-node"
            :style="{
              backgroundColor: '#fdf6ec',
              borderColor: '#E6A23C'
            }"
          >
            <Handle type="target" position="top" :style="{ background: '#E6A23C' }" />
            <el-icon :size="20" color="#E6A23C">
              <Download />
            </el-icon>
            <div class="node-label" style="color: #E6A23C">
              {{ nodeProps.data.label }}
            </div>
          </div>
        </template>

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
          <el-form-item v-if="nodeForm.type === 'process'" label="处理类型">
            <el-select v-model="nodeForm.processType">
              <el-option label="代码" value="code" />
              <el-option label="选择器" value="selector" />
              <el-option label="循环" value="loop" />
              <el-option label="意图识别" value="intent" />
              <el-option label="批处理" value="batch" />
              <el-option label="变量聚合" value="aggregate" />
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

    <!-- 处理节点类型选择对话框 -->
    <el-dialog
      v-model="processTypeDialogVisible"
      title="选择处理类型"
      width="50%"
      :close-on-click-modal="false"
    >
      <div class="process-type-container">
        <el-row :gutter="20">
          <el-col :span="8" v-for="type in processTypes" :key="type.value">
            <el-card 
              :class="['process-type-card', { 'is-selected': selectedProcessType === type.value }]"
              @click="selectedProcessType = type.value"
              shadow="hover"
            >
              <div class="process-type-content">
                <el-icon :size="30" class="process-type-icon">
                  <component :is="type.icon" />
                </el-icon>
                <h3>{{ type.label }}</h3>
                <p class="process-type-desc">{{ type.description }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="processTypeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAddProcessNode">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { VueFlow, useVueFlow, Handle } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { Panel } from '@vue-flow/core'
import { ElMessage } from 'element-plus'
import { 
  Upload, 
  Operation, 
  Download,
  Edit,
  Select,
  Refresh,
  Connection,
  DataLine,
  Collection
} from '@element-plus/icons-vue'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

// 工作流元素
const elements = ref([])
const drawerVisible = ref(false)
const selectedNode = ref(null)
const processTypeDialogVisible = ref(false)
const selectedProcessType = ref('code')
const pendingProcessNode = ref(null)

// 节点表单
const nodeForm = ref({
  name: '',
  type: '',
  description: '',
  processType: 'code'
})

// 统计信息
const nodeCount = computed(() => elements.value.filter(el => el.type === 'custom').length)
const edgeCount = computed(() => elements.value.filter(el => el.type === 'smoothstep').length)

const processTypes = [
  {
    value: 'code',
    label: '代码处理',
    icon: 'Edit',
    description: '执行自定义代码逻辑',
    color: '#409EFF',  // 蓝色
    bgColor: '#ecf5ff'
  },
  {
    value: 'selector',
    label: '选择器',
    icon: 'Select',
    description: '根据条件选择不同的处理路径',
    color: '#67C23A',  // 绿色
    bgColor: '#f0f9eb'
  },
  {
    value: 'loop',
    label: '循环',
    icon: 'Refresh',
    description: '循环处理数据',
    color: '#E6A23C',  // 橙色
    bgColor: '#fdf6ec'
  },
  {
    value: 'intent',
    label: '意图识别',
    icon: 'Connection',
    description: '识别用户意图并分类',
    color: '#F56C6C',  // 红色
    bgColor: '#fef0f0'
  },
  {
    value: 'batch',
    label: '批处理',
    icon: 'DataLine',
    description: '批量处理数据',
    color: '#909399',  // 灰色
    bgColor: '#f4f4f5'
  },
  {
    value: 'aggregate',
    label: '变量聚合',
    icon: 'Collection',
    description: '聚合多个变量数据',
    color: '#9B59B6',  // 紫色
    bgColor: '#f9f0ff'
  }
]

// 添加节点
const addNode = (type) => {
  if (type === 'process') {
    processTypeDialogVisible.value = true
    const id = `${type}-${Date.now()}`
    const position = { x: Math.random() * 400, y: Math.random() * 400 }
    pendingProcessNode.value = { id, position }
  } else {
    const id = `${type}-${Date.now()}`
    const position = { x: Math.random() * 400, y: Math.random() * 400 }
    
    elements.value.push({
      id,
      type,
      position,
      data: {
        label: `${type}节点`,
        type,
        description: ''
      }
    })
  }
}

// 确认添加处理节点
const confirmAddProcessNode = () => {
  if (pendingProcessNode.value) {
    const selectedType = processTypes.find(type => type.value === selectedProcessType.value)
    
    elements.value.push({
      id: pendingProcessNode.value.id,
      type: 'process',
      position: pendingProcessNode.value.position,
      data: {
        label: selectedType.label,
        type: 'process',
        description: selectedType.description,
        processType: selectedType.value,
        icon: selectedType.icon,
        color: selectedType.color,
        bgColor: selectedType.bgColor
      }
    })
    
    processTypeDialogVisible.value = false
    pendingProcessNode.value = null
  }
}

// 更新节点
const updateNode = () => {
  if (!selectedNode.value) return
  
  const node = elements.value.find(el => el.id === selectedNode.value)
  if (node) {
    const processTypeLabels = {
      'code': '代码处理',
      'selector': '选择器',
      'loop': '循环',
      'intent': '意图识别',
      'batch': '批处理',
      'aggregate': '变量聚合'
    }
    
    node.data = {
      ...node.data,
      label: nodeForm.value.processType ? processTypeLabels[nodeForm.value.processType] : nodeForm.value.name || node.data.label,
      description: nodeForm.value.description,
      processType: nodeForm.value.processType
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
    description: node.data.description || '',
    processType: node.data.processType || 'code'
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
  min-width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 15px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border: 2px solid;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="code"]) {
  background: #ecf5ff;
  border-color: #409EFF;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="selector"]) {
  background: #f0f9eb;
  border-color: #67C23A;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="loop"]) {
  background: #fdf6ec;
  border-color: #E6A23C;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="intent"]) {
  background: #fef0f0;
  border-color: #F56C6C;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="batch"]) {
  background: #f4f4f5;
  border-color: #909399;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="aggregate"]) {
  background: #f9f0ff;
  border-color: #9B59B6;
}

:deep(.vue-flow__node[data-type="process"] .vue-flow__node-label) {
  font-size: 14px;
  font-weight: bold;
  margin-top: 5px;
}

:deep(.vue-flow__node[data-type="process"] .process-type-icon) {
  font-size: 20px;
  margin-bottom: 5px;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="code"] .process-type-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="code"] .vue-flow__node-label) {
  color: #409EFF;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="selector"] .process-type-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="selector"] .vue-flow__node-label) {
  color: #67C23A;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="loop"] .process-type-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="loop"] .vue-flow__node-label) {
  color: #E6A23C;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="intent"] .process-type-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="intent"] .vue-flow__node-label) {
  color: #F56C6C;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="batch"] .process-type-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="batch"] .vue-flow__node-label) {
  color: #909399;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="aggregate"] .process-type-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="aggregate"] .vue-flow__node-label) {
  color: #9B59B6;
}

.process-type-container {
  padding: 20px;
}

.process-type-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.process-type-card:hover {
  transform: translateY(-5px);
}

.process-type-card.is-selected {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

.process-type-content {
  text-align: center;
  padding: 20px;
}

.process-type-icon {
  color: #409EFF;
  margin-bottom: 10px;
}

.process-type-desc {
  color: #666;
  font-size: 12px;
  margin-top: 10px;
}

.input-node,
.process-node,
.output-node {
  padding: 10px 15px;
  border-radius: 8px;
  border: 2px solid;
  min-width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: relative;
}

.node-label {
  font-size: 14px;
  font-weight: bold;
  margin-top: 5px;
}

:deep(.vue-flow__handle) {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid #fff;
}

:deep(.vue-flow__handle-top) {
  top: -4px;
}

:deep(.vue-flow__handle-bottom) {
  bottom: -4px;
}
</style>
