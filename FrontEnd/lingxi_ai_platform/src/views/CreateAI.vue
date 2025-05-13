<template>
  <div class="workflow-container">
    <div class="workflow-header">
      <h2>工作流设计器</h2>
      <div class="header-actions">
        <el-button type="success" @click="saveWorkflow">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
        <el-button type="warning" @click="clearWorkflow">
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
      </div>
    </div>
    
    <div class="workflow-content">
      <VueFlow
        v-model="elements"
        :default-viewport="{ x: 0, y: 0, zoom: 1.0 }"
        :min-zoom="0.2"
        :max-zoom="4"
        class="flow-container"
        @connect="handleConnect"
        @node-drag-stop="handleNodeDragStop"
        @node-click="handleNodeClick"
        :nodes-draggable="true"
        :nodes-connectable="true"
        :elements-selectable="true"
        @selection-change="onSelectionChange"
        :default-edge-options="{ 
          type: 'smoothstep', 
          animated: true,
          style: { stroke: '#409EFF' },
          markerEnd: {
            type: 'arrowclosed',
            width: 20,
            height: 20,
            color: '#409EFF'
          }
        }"
        :snap-to-grid="true"
        :snap-grid="[15, 15]"
        :pan-on-drag="true"
        :pan-on-scroll="true"
        :zoom-on-scroll="true"
        :prevent-scrolling="true"
        :pan-on-scroll-mode="'free'"
        :pan-on-drag-mode="'free'"
        :touch-action="'none'"
        @pane-click="onPaneClick"
      >
        <Background pattern-color="#aaa" gap="8" />
        <Controls />
        <MiniMap />
        
        <template #node-input="nodeProps">
          <div 
            class="input-node node-common"
            :style="{
              backgroundColor: '#f0f9ff',
              borderColor: '#409EFF'
            }"
          >
            <el-tooltip
              content="输入"
              placement="top"
              :show-after="500"
              :hide-after="0"
              :effect="'light'"
              popper-class="flow-handle-tooltip"
            >
              <Handle type="source" position="bottom" :style="{ background: '#409EFF' }" />
            </el-tooltip>
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
            v-if="nodeProps.data.processType === 'code'"
          >
            <div class="node-content">
              <el-tooltip
                content="处理节点输入"
                placement="top"
                :show-after="500"
                :hide-after="0"
                :effect="'light'"
                popper-class="flow-handle-tooltip"
              >
                <Handle type="target" position="top" :style="{ background: nodeProps.data.color }" />
              </el-tooltip>
              <div class="code-tooltip-wrapper">
                <el-tooltip
                  :content="nodeProps.data.codeContent ? nodeProps.data.codeContent.replace(/\n/g, '<br>') : '暂无代码内容'"
                  placement="top"
                  :show-after="500"
                  :hide-after="0"
                  :effect="'light'"
                  :raw-content="true"
                  popper-class="flow-node-tooltip"
                >
                  <div class="node-icon-label">
                    <el-icon :size="20" :style="{ color: nodeProps.data.color }">
                      <component :is="nodeProps.data.icon" />
                    </el-icon>
                    <div class="node-label" :style="{ color: nodeProps.data.color }">
                      {{ nodeProps.data.label }}
                    </div>
                  </div>
                </el-tooltip>
              </div>
              <el-tooltip
                content="处理节点输出"
                placement="bottom"
                :show-after="500"
                :hide-after="0"
                :effect="'light'"
                popper-class="flow-handle-tooltip"
              >
                <Handle type="source" position="bottom" :style="{ background: nodeProps.data.color }" />
              </el-tooltip>
            </div>
          </div>
          <div 
            class="process-node"
            :style="{
              backgroundColor: nodeProps.data.bgColor,
              borderColor: nodeProps.data.color
            }"
            v-else-if="nodeProps.data.processType === 'selector'"
          >
            <div class="node-content">
              <el-tooltip
                content="选择器输入"
                placement="top"
                :show-after="500"
                :hide-after="0"
                :effect="'light'"
                popper-class="flow-handle-tooltip"
              >
                <Handle type="target" position="top" :style="{ background: nodeProps.data.color }" />
              </el-tooltip>
              <el-icon :size="20" :style="{ color: nodeProps.data.color }">
                <component :is="nodeProps.data.icon" />
              </el-icon>
              <div class="node-label" :style="{ color: nodeProps.data.color }">
                {{ nodeProps.data.label }}
              </div>
              <div class="selector-handles">
                <el-tooltip
                  content="如果输出"
                  placement="bottom"
                  :show-after="500"
                  :hide-after="0"
                  :effect="'light'"
                  popper-class="flow-handle-tooltip"
                >
                  <Handle 
                    type="source" 
                    position="bottom" 
                    :style="{ 
                      background: nodeProps.data.color,
                      left: '33%'
                    }"
                    :id="'if'"
                  />
                </el-tooltip>
                <template v-for="(condition, index) in nodeProps.data.elseIfConditions" :key="index">
                  <el-tooltip
                    :content="`否则如果${index + 1}输出`"
                    placement="bottom"
                    :show-after="500"
                    :hide-after="0"
                    :effect="'light'"
                    popper-class="flow-handle-tooltip"
                  >
                    <Handle 
                      type="source" 
                      position="bottom" 
                      :style="{ 
                        background: nodeProps.data.color,
                        left: `${33 + (index + 1) * (33 / (nodeProps.data.elseIfConditions.length + 1))}%`
                      }"
                      :id="`elseif-${index}`"
                    />
                  </el-tooltip>
                </template>
                <el-tooltip
                  content="否则输出"
                  placement="bottom"
                  :show-after="500"
                  :hide-after="0"
                  :effect="'light'"
                  popper-class="flow-handle-tooltip"
                >
                  <Handle 
                    type="source" 
                    position="bottom" 
                    :style="{ 
                      background: nodeProps.data.color,
                      left: '66%'
                    }"
                    :id="'else'"
                  />
                </el-tooltip>
              </div>
            </div>
          </div>
          <div 
            class="process-node"
            :style="{
              backgroundColor: nodeProps.data.bgColor,
              borderColor: nodeProps.data.color
            }"
            v-else-if="nodeProps.data.processType === 'loop'"
          >
            <div class="node-content">
              <el-tooltip
                content="循环输入"
                placement="top"
                :show-after="500"
                :hide-after="0"
                :effect="'light'"
                popper-class="flow-handle-tooltip"
              >
                <Handle type="target" position="top" :style="{ background: nodeProps.data.color }" />
              </el-tooltip>
              <el-icon :size="20" :style="{ color: nodeProps.data.color }">
                <component :is="nodeProps.data.icon" />
              </el-icon>
              <div class="node-label" :style="{ color: nodeProps.data.color }">
                {{ nodeProps.data.label }}
              </div>
              <div class="loop-handles">
                <el-tooltip
                  content="循环输出"
                  placement="bottom"
                  :show-after="500"
                  :hide-after="0"
                  :effect="'light'"
                  popper-class="flow-handle-tooltip"
                >
                  <Handle 
                    type="source" 
                    position="bottom" 
                    :style="{ 
                      background: nodeProps.data.color,
                      left: '50%'
                    }"
                    :id="'default'"
                  />
                </el-tooltip>
              </div>
              <div class="loop-side-handles">
                <el-tooltip
                  content="循环入口"
                  placement="right"
                  :show-after="500"
                  :hide-after="0"
                  :effect="'light'"
                  popper-class="flow-handle-tooltip"
                >
                  <Handle 
                    type="source" 
                    position="right" 
                    :style="{ 
                      background: nodeProps.data.color,
                      top: '30%'
                    }"
                    :id="'loop-entry'"
                  />
                </el-tooltip>
                <el-tooltip
                  content="循环出口"
                  placement="right"
                  :show-after="500"
                  :hide-after="0"
                  :effect="'light'"
                  popper-class="flow-handle-tooltip"
                >
                  <Handle 
                    type="source" 
                    position="right" 
                    :style="{ 
                      background: nodeProps.data.color,
                      top: '70%'
                    }"
                    :id="'loop-exit'"
                  />
                </el-tooltip>
              </div>
            </div>
          </div>
          <div 
            class="process-node"
            :style="{
              backgroundColor: nodeProps.data.bgColor,
              borderColor: nodeProps.data.color
            }"
            v-else-if="nodeProps.data.processType === 'batch'"
          >
            <div class="node-content">
              <el-tooltip
                content="批处理输入"
                placement="top"
                :show-after="500"
                :hide-after="0"
                :effect="'light'"
                popper-class="flow-handle-tooltip"
              >
                <Handle type="target" position="top" :style="{ background: nodeProps.data.color }" />
              </el-tooltip>
              <el-icon :size="20" :style="{ color: nodeProps.data.color }">
                <component :is="nodeProps.data.icon" />
              </el-icon>
              <div class="node-label" :style="{ color: nodeProps.data.color }">
                {{ nodeProps.data.label }}
              </div>
              <div class="batch-handles">
                <el-tooltip
                  content="批处理输出"
                  placement="bottom"
                  :show-after="500"
                  :hide-after="0"
                  :effect="'light'"
                  popper-class="flow-handle-tooltip"
                >
                  <Handle 
                    type="source" 
                    position="bottom" 
                    :style="{ 
                      background: nodeProps.data.color,
                      left: '50%'
                    }"
                    :id="'default'"
                  />
                </el-tooltip>
              </div>
              <div class="batch-side-handles">
                <el-tooltip
                  content="批处理入口"
                  placement="left"
                  :show-after="500"
                  :hide-after="0"
                  :effect="'light'"
                  popper-class="flow-handle-tooltip"
                >
                  <Handle 
                    type="source" 
                    position="left" 
                    :style="{ 
                      background: nodeProps.data.color,
                      top: '30%'
                    }"
                    :id="'batch-entry'"
                  />
                </el-tooltip>
                <el-tooltip
                  content="批处理出口"
                  placement="left"
                  :show-after="500"
                  :hide-after="0"
                  :effect="'light'"
                  popper-class="flow-handle-tooltip"
                >
                  <Handle 
                    type="source" 
                    position="left" 
                    :style="{ 
                      background: nodeProps.data.color,
                      top: '70%'
                    }"
                    :id="'batch-exit'"
                  />
                </el-tooltip>
              </div>
            </div>
          </div>
          <div 
            class="process-node"
            :style="{
              backgroundColor: nodeProps.data.bgColor,
              borderColor: nodeProps.data.color
            }"
            v-else-if="nodeProps.data.processType === 'llm'"
          >
            <div class="node-content">
              <el-tooltip
                content="大模型输入"
                placement="top"
                :show-after="500"
                :hide-after="0"
                :effect="'light'"
                popper-class="flow-handle-tooltip"
              >
                <Handle type="target" position="top" :style="{ background: nodeProps.data.color }" />
              </el-tooltip>
              <el-icon :size="20" :style="{ color: nodeProps.data.color }">
                <component :is="nodeProps.data.icon" />
              </el-icon>
              <div class="node-label" :style="{ color: nodeProps.data.color }">
                {{ nodeProps.data.label }}
              </div>
              <el-tooltip
                content="大模型输出"
                placement="bottom"
                :show-after="500"
                :hide-after="0"
                :effect="'light'"
                popper-class="flow-handle-tooltip"
              >
                <Handle type="source" position="bottom" :style="{ background: nodeProps.data.color }" />
              </el-tooltip>
            </div>
          </div>
          <div 
            class="process-node"
            :style="{
              backgroundColor: nodeProps.data.bgColor,
              borderColor: nodeProps.data.color
            }"
            v-else
          >
            <div class="node-content">
              <el-tooltip
                content="聚合输入"
                placement="top"
                :show-after="500"
                :hide-after="0"
                :effect="'light'"
                popper-class="flow-handle-tooltip"
              >
                <Handle type="target" position="top" :style="{ background: nodeProps.data.color }" />
              </el-tooltip>
              <el-icon :size="20" :style="{ color: nodeProps.data.color }">
                <component :is="nodeProps.data.icon" />
              </el-icon>
              <div class="node-label" :style="{ color: nodeProps.data.color }">
                {{ nodeProps.data.label }}
              </div>
              <el-tooltip
                content="聚合输出"
                placement="bottom"
                :show-after="500"
                :hide-after="0"
                :effect="'light'"
                popper-class="flow-handle-tooltip"
              >
                <Handle type="source" position="bottom" :style="{ background: nodeProps.data.color }" />
              </el-tooltip>
            </div>
          </div>
        </template>

        <template #node-output="nodeProps">
          <div 
            class="output-node node-common"
            :style="{
              backgroundColor: '#f0f9ff',
              borderColor: '#409EFF'
            }"
          >
            <el-tooltip
              content="输出"
              placement="top"
              :show-after="500"
              :hide-after="0"
              :effect="'light'"
              popper-class="flow-handle-tooltip"
            >
              <Handle type="target" position="top" :style="{ background: '#409EFF' }" />
            </el-tooltip>
            <el-icon :size="20" color="#409EFF">
              <Download />
            </el-icon>
            <div class="node-label" style="color: #409EFF">
              {{ nodeProps.data.label }}
            </div>
          </div>
        </template>

        <template #node-workflow="nodeProps">
          <div 
            class="workflow-node"
            :style="{
              backgroundColor: '#f0f0ff',
              borderColor: '#7B68EE'
            }"
          >
            <el-tooltip
              content="智能体输入"
              placement="top"
              :show-after="500"
              :hide-after="0"
              :effect="'light'"
              popper-class="flow-handle-tooltip"
            >
              <Handle type="target" position="top" :style="{ background: '#7B68EE' }" />
            </el-tooltip>
            <el-icon :size="20" color="#7B68EE">
              <Share />
            </el-icon>
            <div class="node-label" style="color: #7B68EE">
              智能体
            </div>
            <el-tooltip
              content="智能体输出"
              placement="bottom"
              :show-after="500"
              :hide-after="0"
              :effect="'light'"
              popper-class="flow-handle-tooltip"
            >
              <Handle type="source" position="bottom" :style="{ background: '#7B68EE' }" />
            </el-tooltip>
          </div>
        </template>

        <template #node-dynamic-input="nodeProps">
          <div 
            class="dynamic-input-node node-common"
            :style="{
              backgroundColor: '#f0f9ff',
              borderColor: '#409EFF'
            }"
          >
            <el-tooltip
              content="动态输入"
              placement="top"
              :show-after="500"
              :hide-after="0"
              :effect="'light'"
              popper-class="flow-handle-tooltip"
            >
              <Handle type="source" position="bottom" :style="{ background: '#409EFF' }" />
            </el-tooltip>
            <el-icon :size="20" color="#409EFF">
              <Connection />
            </el-icon>
            <div class="node-label" style="color: #409EFF">
              {{ nodeProps.data.label }}
            </div>
          </div>
        </template>

        <template #node-monitor="nodeProps">
          <div 
            class="monitor-node node-common"
            :style="{
              backgroundColor: '#fff0f0',
              borderColor: '#F56C6C'
            }"
          >
            <el-tooltip
              content="监听输入"
              placement="top"
              :show-after="500"
              :hide-after="0"
              :effect="'light'"
              popper-class="flow-handle-tooltip"
            >
              <Handle type="target" position="top" :style="{ background: '#F56C6C' }" />
            </el-tooltip>
            <el-icon :size="20" color="#F56C6C">
              <View />
            </el-icon>
            <div class="node-label" style="color: #F56C6C">
              {{ nodeProps.data.label }}
            </div>
            <el-tooltip
              content="监听输出"
              placement="bottom"
              :show-after="500"
              :hide-after="0"
              :effect="'light'"
              popper-class="flow-handle-tooltip"
            >
              <Handle type="source" position="bottom" :style="{ background: '#F56C6C' }" />
            </el-tooltip>
          </div>
        </template>

        <Panel position="top-right" class="node-panel">
          <el-button-group>
            <el-button @click="addNode('input')" type="primary">
              <el-icon><Upload /></el-icon>
              输入节点
            </el-button>
            <el-button @click="addNode('dynamic-input')" type="primary">
              <el-icon><Connection /></el-icon>
              动态输入
            </el-button>
            <el-button @click="addNode('process')" type="success">
              <el-icon><Operation /></el-icon>
              处理节点
            </el-button>
            <el-button @click="addNode('workflow')" type="warning">
              <el-icon><Share /></el-icon>
              智能体节点
            </el-button>
            <el-button @click="addNode('monitor')" type="danger">
              <el-icon><View /></el-icon>
              监听节点
            </el-button>
            <el-button @click="addNode('output')" type="danger">
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
        :title="`${
        nodeForm.type === 'input' ? '输入' : 
        nodeForm.type === 'process' ? '处理' : 
        nodeForm.type === 'output' ? '输出' :
        nodeForm.type === 'workflow' ? '智能体' :
        nodeForm.type === 'monitor' ? '监听' :
        nodeForm.type === 'dynamic-input' ? '动态输入' :
        '未知'
        }节点配置`"
        direction="rtl"
        size="400px"
        :append-to-body="true"
        :modal-append-to-body="true"
        :destroy-on-close="false"
        :close-on-click-modal="true"
        :close-on-press-escape="true"
        :show-close="true"
        class="node-config-drawer"
        @close="handleDrawerClose"
      >
        <el-scrollbar height="calc(100vh - 57px)">
          <el-form 
            :model="nodeForm" 
            label-width="80px"
            class="node-form"
            ref="nodeFormRef"
          >
            <el-card shadow="never" class="form-card">
              <template #header>
                <div class="card-header">
                  <span>基本信息</span>
                </div>
              </template>
              <el-form-item label="节点名称" label-width="100px">
                <el-input v-model="nodeForm.name" placeholder="请输入节点名称" />
              </el-form-item>
              <el-form-item label="节点类型" label-width="100px">
                <el-select v-model="nodeForm.type" disabled>
                  <el-option label="输入节点" value="input" />
                  <el-option label="处理节点" value="process" />
                  <el-option label="输出节点" value="output" />
                </el-select>
              </el-form-item>
              <el-form-item label="节点描述" label-width="100px">
                <el-input
                  v-model="nodeForm.description"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入节点描述"
                />
              </el-form-item>
            </el-card>

            <!-- 输入节点配置 -->
            <template v-if="nodeForm.type === 'input'">
              <el-card shadow="never" class="form-card">
                <template #header>
                  <div class="card-header">
                    <span>输入配置</span>
                  </div>
                </template>
                <el-form-item label="输入类型" label-width="100px">
                  <el-select v-model="nodeForm.inputType">
                    <el-option label="文本" value="text" />
                    <el-option label="文件" value="file" />
                    <el-option label="API" value="api" />
                  </el-select>
                </el-form-item>
                <template v-if="nodeForm.inputType === 'text'">
                  <el-form-item label="默认值" label-width="100px">
                    <el-input v-model="nodeForm.defaultValue" type="textarea" :rows="3" />
                  </el-form-item>
                </template>
                <template v-if="nodeForm.inputType === 'file'">
                  <el-form-item label="文件类型" label-width="100px">
                    <el-select v-model="nodeForm.fileType">
                      <el-option label="文本文件" value="text" />
                      <el-option label="CSV文件" value="csv" />
                      <el-option label="JSON文件" value="json" />
                    </el-select>
                  </el-form-item>
                </template>
                <template v-if="nodeForm.inputType === 'api'">
                  <el-form-item label="API地址" label-width="100px">
                    <el-input v-model="nodeForm.apiUrl" />
                  </el-form-item>
                  <el-form-item label="请求方法" label-width="100px">
                    <el-select v-model="nodeForm.apiMethod">
                      <el-option label="GET" value="get" />
                      <el-option label="POST" value="post" />
                      <el-option label="PUT" value="put" />
                      <el-option label="DELETE" value="delete" />
                    </el-select>
                  </el-form-item>
                </template>
              </el-card>
            </template>

            <!-- 处理节点配置 -->
            <template v-if="nodeForm.type === 'process'">
              <el-card shadow="never" class="form-card">
                <template #header>
                  <div class="card-header">
                    <span>处理配置</span>
                  </div>
                </template>
                <el-form-item label="处理类型" label-width="100px">
                  <el-select v-model="nodeForm.processType">
                    <el-option label="代码处理" value="code" />
                    <el-option label="选择器" value="selector" />
                    <el-option label="循环" value="loop" />
                    <el-option label="大模型" value="llm" />
                    <el-option label="批处理" value="batch" />
                    <el-option label="变量聚合" value="aggregate" />
                  </el-select>
                </el-form-item>

                <!-- 代码处理配置 -->
                <template v-if="nodeForm.processType === 'code'">
                  <el-form-item label="代码类型" label-width="100px">
                    <el-select v-model="nodeForm.codeType">
                      <el-option label="JavaScript" value="javascript" />
                      <el-option label="Python" value="python" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="代码内容" label-width="100px">
                    <div class="code-editor-action">
                      <el-button 
                        type="primary" 
                        @click="openCodeEditor"
                        class="code-editor-btn"
                      >
                        <el-icon><Edit /></el-icon>
                        打开代码编辑器
                      </el-button>
                    </div>
                  </el-form-item>
                </template>

                <!-- 选择器配置 -->
                <template v-if="nodeForm.processType === 'selector'">
                  <el-form-item label="条件配置" label-width="100px">
                    <div class="condition-container">
                      <div class="condition-item">
                        <el-input v-model="nodeForm.ifCondition" placeholder="如果条件" />
                      </div>
                      <div v-for="(condition, index) in nodeForm.elseIfConditions" :key="index" class="condition-item">
                        <el-input v-model="condition.value" placeholder="否则如果条件" />
                        <el-button type="danger" @click="removeElseIfCondition(index)" circle>
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </div>
                      <div class="condition-item">
                        <el-input 
                          v-model="nodeForm.elseCondition" 
                          placeholder="否则" 
                          disabled
                          :value="'否则（默认执行路径）'"
                        />
                      </div>
                      <el-button type="primary" @click="addElseIfCondition" class="add-condition-btn">
                        <el-icon><Plus /></el-icon>
                        添加否则如果条件
                      </el-button>
                    </div>
                  </el-form-item>
                </template>

                <!-- 循环配置 -->
                <template v-if="nodeForm.processType === 'loop'">
                  <el-form-item label="循环类型" label-width="100px">
                    <el-select v-model="nodeForm.loopType">
                      <el-option label="固定次数" value="fixed" />
                      <el-option label="条件循环" value="conditional" />
                    </el-select>
                  </el-form-item>
                  <el-form-item v-if="nodeForm.loopType === 'fixed'" label="循环次数" label-width="100px">
                    <el-input-number v-model="nodeForm.loopCount" :min="1" :max="1000" />
                  </el-form-item>
                  <el-form-item v-if="nodeForm.loopType === 'conditional'" label="条件表达式" label-width="100px">
                    <el-input v-model="nodeForm.loopCondition" />
                  </el-form-item>
                </template>

                <!-- 批处理配置 -->
                <template v-if="nodeForm.processType === 'batch'">
                  <el-form-item label="批处理大小" label-width="100px">
                    <el-input-number v-model="nodeForm.batchSize" :min="1" :max="1000" />
                  </el-form-item>
                  <el-form-item label="并行处理" label-width="100px">
                    <el-switch v-model="nodeForm.parallel" />
                  </el-form-item>
                </template>

                <!-- 变量聚合配置 -->
                <template v-if="nodeForm.processType === 'aggregate'">
                  <el-form-item label="聚合方式" label-width="100px">
                    <el-select v-model="nodeForm.aggregateType">
                      <el-option label="求和" value="sum" />
                      <el-option label="平均值" value="avg" />
                      <el-option label="最大值" value="max" />
                      <el-option label="最小值" value="min" />
                      <el-option label="计数" value="count" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="聚合字段" label-width="100px">
                    <el-input v-model="nodeForm.aggregateField" />
                  </el-form-item>
                </template>
              </el-card>
            </template>

            <!-- 输出节点配置 -->
            <template v-if="nodeForm.type === 'output'">
              <el-card shadow="never" class="form-card">
                <template #header>
                  <div class="card-header">
                    <span>输出配置</span>
                  </div>
                </template>
                <el-form-item label="输出类型" label-width="100px">
                  <el-select v-model="nodeForm.outputType">
                    <el-option label="文本" value="text" />
                    <el-option label="文件" value="file" />
                    <el-option label="API" value="api" />
                  </el-select>
                </el-form-item>
                <template v-if="nodeForm.outputType === 'file'">
                  <el-form-item label="文件格式" label-width="100px">
                    <el-select v-model="nodeForm.fileFormat">
                      <el-option label="JSON" value="json" />
                      <el-option label="CSV" value="csv" />
                      <el-option label="TXT" value="txt" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="文件路径" label-width="100px">
                    <el-input v-model="nodeForm.filePath" />
                  </el-form-item>
                </template>
                <template v-if="nodeForm.outputType === 'api'">
                  <el-form-item label="API地址" label-width="100px">
                    <el-input v-model="nodeForm.apiUrl" />
                  </el-form-item>
                  <el-form-item label="请求方法" label-width="100px">
                    <el-select v-model="nodeForm.apiMethod">
                      <el-option label="GET" value="get" />
                      <el-option label="POST" value="post" />
                      <el-option label="PUT" value="put" />
                      <el-option label="DELETE" value="delete" />
                    </el-select>
                  </el-form-item>
                </template>
              </el-card>
            </template>

            <!-- 大模型配置 -->
            <template v-if="nodeForm.processType === 'llm'">
              <el-card shadow="never" class="form-card">
                <template #header>
                  <div class="card-header">
                    <span>大模型配置</span>
                  </div>
                </template>
                <el-form-item label="模型选择" label-width="100px">
                  <el-select v-model="nodeForm.llmModel">
                    <el-option label="LLaMA 3" value="LLaMA-3" />
                    <el-option label="Claude 3" value="claude-3" />
                    <el-option label="通义千问" value="Qwen" />
                    <el-option label="GPT-3.5 Turbo" value="gpt-3.5-turbo" />
                    <el-option label="GPT-4" value="gpt-4" />
                  </el-select>
                </el-form-item>
                <el-form-item label="提示词" label-width="100px">
                  <el-input
                    v-model="nodeForm.llmPrompt"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入提示词"
                  />
                </el-form-item>
              </el-card>
            </template>

            <!-- 监听节点配置 -->
            <template v-if="nodeForm.type === 'monitor'">
              <el-card shadow="never" class="form-card">
              </el-card>
            </template>

            <!-- 智能体节点配置 -->
            <template v-if="nodeForm.type === 'workflow'">
              <el-card shadow="never" class="form-card">
                <template #header>
                  <div class="card-header">
                    <span>智能体配置</span>
                  </div>
                </template>
                <div class="agent-buttons">
                  <el-button type="primary" @click="selectMyAgent">
                    <el-icon><Select /></el-icon>
                    选择可用的智能体
                  </el-button>
                </div>
              </el-card>
            </template>

            <!-- 动态输入节点配置 -->
            <template v-if="nodeForm.type === 'dynamic-input'">
              <el-card shadow="never" class="form-card">
                <template #header>
                  <div class="card-header">
                    <span>动态输入配置</span>
                  </div>
                </template>
                <el-form-item label="输入类型" label-width="100px">
                  <el-select v-model="nodeForm.inputType">
                    <el-option label="文本" value="text" />
                    <el-option label="文件" value="file" />
                    <el-option label="API" value="api" />
                  </el-select>
                </el-form-item>
                <el-form-item v-if="nodeForm.inputType === 'text'" label="默认值" label-width="100px">
                  <el-input v-model="nodeForm.defaultValue" placeholder="请输入默认值" />
                </el-form-item>
                <el-form-item v-if="nodeForm.inputType === 'file'" label="文件类型" label-width="100px">
                  <el-select v-model="nodeForm.fileType">
                    <el-option label="文本文件" value="text" />
                    <el-option label="CSV文件" value="csv" />
                    <el-option label="JSON文件" value="json" />
                  </el-select>
                </el-form-item>
                <el-form-item v-if="nodeForm.inputType === 'api'" label="API地址" label-width="100px">
                  <el-input v-model="nodeForm.apiUrl" placeholder="请输入API地址" />
                </el-form-item>
                <el-form-item v-if="nodeForm.inputType === 'api'" label="请求方法" label-width="100px">
                  <el-select v-model="nodeForm.apiMethod">
                    <el-option label="GET" value="get" />
                    <el-option label="POST" value="post" />
                  </el-select>
                </el-form-item>
              </el-card>
            </template>

            <div class="form-actions">
              <el-button type="success" @click="updateNode">
                <el-icon><Check /></el-icon>
                保存
              </el-button>
              <el-button @click="handleDrawerClose">
                <el-icon><Close /></el-icon>
                取消修改
              </el-button>
              <el-button type="danger" @click="deleteNode">
                <el-icon><Delete /></el-icon>
                删除节点
              </el-button>
            </div>
          </el-form>
        </el-scrollbar>
      </el-drawer>
    </div>

    <!-- 处理节点类型选择对话框 -->
    <el-dialog
      v-model="processTypeDialogVisible"
      title="选择处理类型"
      width="50%"
      :close-on-click-modal="true"
      class="process-type-dialog"
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
          <el-button-group>
            <el-button @click="processTypeDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmAddProcessNode">确定</el-button>
          </el-button-group>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VueFlow, useVueFlow, Handle } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { Panel } from '@vue-flow/core'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Upload, 
  Operation, 
  Download,
  Edit,
  Select,
  Refresh,
  Connection,
  DataLine,
  Collection,
  Check,
  Close,
  Delete,
  Plus,
  ChatDotRound,
  Share,
  View,
  Document
} from '@element-plus/icons-vue'

// 引入 Vue Flow 样式
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
const workflowName = ref('')

// 获取路由实例
const route = useRoute()
const router = useRouter()

// 节点表单
const nodeForm = ref({
  name: '',
  type: '',
  description: '',
  // 输入节点配置
  inputType: 'text',
  defaultValue: '',
  fileType: 'text',
  apiUrl: '',
  apiMethod: 'get',
  // 处理节点配置
  processType: 'code',
  codeType: 'javascript',
  codeContent: '',
  conditionType: 'equals',
  conditionValue: '',
  loopType: 'fixed',
  loopCount: 1,
  loopCondition: '',
  batchSize: 32,
  parallel: true,
  aggregateType: 'sum',
  aggregateField: '',
  // 输出节点配置
  outputType: 'text',
  fileFormat: 'json',
  filePath: '',
  // 选择器配置
  ifCondition: '',
  elseIfConditions: [],
  elseCondition: '否则（默认执行路径）',
  // 大模型配置
  llmModel: 'Qwen',
  llmPrompt: '',
  // 监听节点配置
  monitorType: 'all',
  // 智能体配置
  myAgents: [],
  followedAgents: [],
  myAgentId: null,
  myAgentName: '',
  followedAgentId: null,
  followedAgentName: '',
})

// 添加表单引用
const nodeFormRef = ref(null)
// 添加原始节点数据备份
const originalNodeData = ref(null)

// 统计信息
const nodeCount = computed(() => elements.value.filter(el => 
  el.type === 'input' || 
  el.type === 'process' || 
  el.type === 'output'
).length)
const edgeCount = computed(() => elements.value.filter(el => el.type === 'smoothstep').length)

// 节点类型计数器
const nodeTypeCounters = ref({
  input: 0,
  'dynamic-input': 0,
  process: {
    code: 0,
    selector: 0,
    loop: 0,
    llm: 0,
    batch: 0,
    aggregate: 0
  },
  workflow: 0,
  monitor: 0,
  output: 0
})

const processTypes = [
  {
    value: 'code',
    label: '代码处理',
    icon: 'Document',
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
    color: '#9B59B6',  // 紫色
    bgColor: '#f9f0ff'
  },
  {
    value: 'llm',
    label: '大模型',
    icon: 'ChatDotRound',
    description: '调用大模型处理',
    color: '#9B59B6',
    bgColor: '#f9f0ff'
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
    color: '#7B68EE',  // 靛蓝色
    bgColor: '#f0f0ff'
  }
]

// 添加 useVueFlow hook
const { onPaneClick, updateNode: vueFlowUpdateNode, viewport } = useVueFlow()

// 智能体列表数据
const myAgentsList = ref([
  { id: 1, name: '智能体1' },
  { id: 2, name: '智能体2' },
  { id: 3, name: '智能体3' }
])

const followedAgentsList = ref([
  { id: 4, name: '关注智能体1' },
  { id: 5, name: '关注智能体2' },
  { id: 6, name: '关注智能体3' }
])

// 添加节点
const addNode = (type) => {
  const id = `${type}-${Date.now()}`
  const position = findAvailablePosition()
  
  if (type === 'input') {
    // 增加输入节点的计数器
    nodeTypeCounters.value.input++
    
    // 创建输入节点的默认配置
    const defaultInputConfig = {
      name: `输入 ${nodeTypeCounters.value.input}`,
      type: 'input',
      description: '输入节点',
      inputType: 'text',
      defaultValue: '',
      fileType: 'text',
      apiUrl: '',
      apiMethod: 'get'
    }
    
    elements.value.push({
      id,
      type,
      position,
      data: {
        ...defaultInputConfig,
        label: `输入 ${nodeTypeCounters.value.input}`,
        icon: 'Upload',
        color: '#409EFF',
        bgColor: '#f0f9ff'
      }
    })
  } else if (type === 'output') {
    // 增加输出节点的计数器
    nodeTypeCounters.value.output++
    
    // 创建输出节点的默认配置
    const defaultOutputConfig = {
      name: `输出 ${nodeTypeCounters.value.output}`,
      type: 'output',
      description: '输出节点',
      outputType: 'text',
      fileFormat: 'json',
      filePath: ''
    }
    
    elements.value.push({
      id,
      type,
      position,
      data: {
        ...defaultOutputConfig,
        label: `输出 ${nodeTypeCounters.value.output}`,
        icon: 'Download',
        color: '#E6A23C',
        bgColor: '#fdf6ec'
      }
    })
  } else if (type === 'process') {
    // 显示处理类型选择对话框
    processTypeDialogVisible.value = true
    pendingProcessNode.value = { id, position }
  } else if (type === 'llm') {
    // 增加大模型节点的计数器
    nodeTypeCounters.value.llm++
    
    elements.value.push({
      id,
      type,
      position,
      data: {
        label: `大模型 ${nodeTypeCounters.value.llm}`,
        name: `大模型 ${nodeTypeCounters.value.llm}`,  // 添加name字段，与label保持一致
        type: 'llm',
        description: '大模型节点',
        icon: 'ChatDotRound',
        color: '#9B59B6',
        bgColor: '#f9f0ff',
        llmModel: 'Qwen',
        llmPrompt: ''
      }
    })
  } else if (type === 'workflow') {
    // 增加工作流节点的计数器
    nodeTypeCounters.value.workflow++
    
    elements.value.push({
      id,
      type,
      position,
      data: {
        label: `工作流 ${nodeTypeCounters.value.workflow}`,
        type: 'workflow',
        description: '工作流节点',
        icon: 'Share',
        color: '#7B68EE',
        bgColor: '#f0f0ff'
      }
    })
  } else if (type === 'monitor') {
    // 增加监听节点的计数器
    nodeTypeCounters.value.monitor++
    
    elements.value.push({
      id,
      type,
      position,
      data: {
        label: `监听节点 ${nodeTypeCounters.value.monitor}`,
        type: 'monitor',
        description: '监听节点',
        icon: 'View',
        color: '#F56C6C',
        bgColor: '#fff0f0',
        monitorType: 'all'
      }
    })
  } else if (type === 'dynamic-input') {
    // 增加动态输入节点的计数器
    nodeTypeCounters.value['dynamic-input']++
    
    elements.value.push({
      id,
      type,
      position,
      data: {
        label: `动态输入 ${nodeTypeCounters.value['dynamic-input']}`,
        type: 'dynamic-input',
        description: '动态输入节点',
        icon: 'Connection',
        color: '#409EFF',
        bgColor: '#f0f9ff'
      }
    })
  }
}

// 确认添加处理节点
const confirmAddProcessNode = () => {
  if (pendingProcessNode.value) {
    const selectedType = processTypes.find(type => type.value === selectedProcessType.value)
    
    // 增加对应处理节点类型的计数器
    nodeTypeCounters.value.process[selectedType.value]++
    
    // 创建默认配置对象
    const defaultConfig = {
      // 基础配置
      name: `${selectedType.label} ${nodeTypeCounters.value.process[selectedType.value]}`,
      type: 'process',
      description: selectedType.description,
      // 处理节点配置
      processType: selectedType.value,
      codeType: 'javascript',
      codeContent: '',
      conditionType: 'equals',
      conditionValue: '',
      loopType: 'fixed',
      loopCount: 1,
      loopCondition: '',
      batchSize: 32,
      parallel: true,
      aggregateType: 'sum',
      aggregateField: '',
      // 选择器配置
      ifCondition: selectedType.value === 'selector' ? '' : undefined,
      elseIfConditions: selectedType.value === 'selector' ? [] : undefined,
      elseCondition: selectedType.value === 'selector' ? '' : undefined,
      // 大模型配置
      llmModel: 'Qwen',
      llmPrompt: '',
      // 监听节点配置
      monitorType: 'all',
      // 智能体配置
      myAgents: [],
      followedAgents: []
    }
    
    elements.value.push({
      id: pendingProcessNode.value.id,
      type: 'process',
      position: pendingProcessNode.value.position,
      data: {
        ...defaultConfig,
        label: `${selectedType.label} ${nodeTypeCounters.value.process[selectedType.value]}`,
        icon: selectedType.icon,
        color: selectedType.color,
        bgColor: selectedType.bgColor
      }
    })
    
    processTypeDialogVisible.value = false
    pendingProcessNode.value = null
  }
}

// 查找可用位置
const findAvailablePosition = () => {
  const NODE_WIDTH = 150
  const NODE_HEIGHT = 100
  const GRID_SIZE = 20
  const PADDING = 50
  
  // 获取画布尺寸
  const flowContainer = document.querySelector('.flow-container')
  const containerWidth = flowContainer?.clientWidth || 800
  const containerHeight = flowContainer?.clientHeight || 600
  
  // 获取视口位置
  const viewportX = viewport.value.x
  const viewportY = viewport.value.y
  const viewportZoom = viewport.value.zoom
  
  // 计算可见区域
  const visibleWidth = containerWidth / viewportZoom
  const visibleHeight = containerHeight / viewportZoom
  const visibleLeft = -viewportX / viewportZoom
  const visibleTop = -viewportY / viewportZoom
  
  // 获取所有现有节点的位置
  const existingPositions = elements.value
    .filter(el => el.type !== 'smoothstep')
    .map(el => ({
      x: Math.round(el.position.x / GRID_SIZE) * GRID_SIZE,
      y: Math.round(el.position.y / GRID_SIZE) * GRID_SIZE
    }))
  
  // 从可见区域中心开始搜索
  let x = Math.round((visibleLeft + visibleWidth / 2) / GRID_SIZE) * GRID_SIZE
  let y = Math.round((visibleTop + visibleHeight / 2) / GRID_SIZE) * GRID_SIZE
  
  // 如果画布为空，直接返回中心位置
  if (existingPositions.length === 0) {
    return { x, y }
  }
  
  // 螺旋搜索算法
  let radius = 1
  let angle = 0
  const maxRadius = Math.max(visibleWidth, visibleHeight) / GRID_SIZE
  
  while (radius < maxRadius) {
    // 计算螺旋位置
    x = Math.round((visibleLeft + visibleWidth / 2 + Math.cos(angle) * radius * GRID_SIZE) / GRID_SIZE) * GRID_SIZE
    y = Math.round((visibleTop + visibleHeight / 2 + Math.sin(angle) * radius * GRID_SIZE) / GRID_SIZE) * GRID_SIZE
    
    // 检查是否在可见区域内
    if (x >= visibleLeft + PADDING && x <= visibleLeft + visibleWidth - NODE_WIDTH - PADDING &&
        y >= visibleTop + PADDING && y <= visibleTop + visibleHeight - NODE_HEIGHT - PADDING) {
      // 检查是否与现有节点重叠
      const isOverlapping = existingPositions.some(pos => {
        return Math.abs(pos.x - x) < NODE_WIDTH && Math.abs(pos.y - y) < NODE_HEIGHT
      })
      
      if (!isOverlapping) {
        return { x, y }
      }
    }
    
    // 增加角度和半径
    angle += Math.PI / 8
    if (angle >= Math.PI * 2) {
      angle = 0
      radius++
    }
  }
  
  // 如果找不到合适位置，返回可见区域中心
  return { 
    x: visibleLeft + visibleWidth / 2, 
    y: visibleTop + visibleHeight / 2 
  }
}

// 修改节点点击事件处理
const handleNodeClick = (event) => {
  const node = event.node
  if (!node || !node.id) return
  
  selectedNode.value = node.id
  
  // 从label中提取数字后缀
  const labelMatch = node.data?.label?.match(/(\d+)$/)
  const numberSuffix = labelMatch ? parseInt(labelMatch[1]) : 0
  
  // 如果是处理节点，更新对应类型的计数器
  if (node.data?.type === 'process' && node.data?.processType) {
    nodeTypeCounters.value.process[node.data.processType] = numberSuffix
  } else if (node.data?.type) {
    // 对于其他类型的节点，更新对应的计数器
    nodeTypeCounters.value[node.data.type] = numberSuffix
  }
  
  // 更新表单数据
  nodeForm.value = {
    name: node.data?.label || '',  // 使用完整的label作为名称
    type: node.data?.type || '',
    description: node.data?.description || '',
    // 输入节点配置
    inputType: node.data?.inputType || 'text',
    defaultValue: node.data?.defaultValue || '',
    fileType: node.data?.fileType || 'text',
    apiUrl: node.data?.apiUrl || '',
    apiMethod: node.data?.apiMethod || 'get',
    // 处理节点配置
    processType: node.data?.processType || 'code',
    codeType: node.data?.codeType || 'javascript',
    codeContent: node.data?.codeContent || '',
    conditionType: node.data?.conditionType || 'equals',
    conditionValue: node.data?.conditionValue || '',
    loopType: node.data?.loopType || 'fixed',
    loopCount: node.data?.loopCount || 1,
    loopCondition: node.data?.loopCondition || '',
    batchSize: node.data?.batchSize || 32,
    parallel: node.data?.parallel ?? true,
    aggregateType: node.data?.aggregateType || 'sum',
    aggregateField: node.data?.aggregateField || '',
    // 输出节点配置
    outputType: node.data?.outputType || 'text',
    fileFormat: node.data?.fileFormat || 'json',
    filePath: node.data?.filePath || '',
    // 选择器配置
    ifCondition: node.data?.ifCondition || '',
    elseIfConditions: node.data?.elseIfConditions || [],
    elseCondition: '否则（默认执行路径）',
    // 大模型配置
    llmModel: node.data?.llmModel || 'Qwen',
    llmPrompt: node.data?.llmPrompt || '',
    // 监听节点配置
    monitorType: node.data?.monitorType || 'all',
    // 智能体配置
    myAgents: node.data?.myAgents || [],
    followedAgents: node.data?.followedAgents || [],
    myAgentId: node.data?.myAgentId || null,
    myAgentName: node.data?.myAgentName || '',
    followedAgentId: node.data?.followedAgentId || null,
    followedAgentName: node.data?.followedAgentName || '',
  }
  
  // 保存原始数据
  originalNodeData.value = JSON.parse(JSON.stringify(nodeForm.value))
  
  drawerVisible.value = true
}

// 更新节点
const updateNode = async () => {
  if (!selectedNode.value) return
  
  const node = elements.value.find(el => el.id === selectedNode.value)
  if (!node || !node.data) return
  
  // 保存原始的颜色和背景色
  const originalColor = node.data.color
  const originalBgColor = node.data.bgColor
  
  // 使用表单中的名称作为新的标签
  const newLabel = nodeForm.value.name
  
  if (node.data.type === 'process') {
    // 如果是代码处理节点，保持原始颜色
    if (node.data.processType === 'code') {
      const newNodeData = {
        ...node.data,
        ...nodeForm.value,
        label: newLabel,  // 只使用label字段
        color: originalColor,
        bgColor: originalBgColor
      }
      
      vueFlowUpdateNode(node.id, {
        data: newNodeData
      })
    } else {
      // 其他处理节点类型的原有逻辑
      const processTypeLabels = {
        'selector': '选择器',
        'loop': '循环',
        'llm': '大模型',
        'batch': '批处理',
        'aggregate': '变量聚合'
      }

      const processTypeIcons = {
        'selector': 'Select',
        'loop': 'Refresh',
        'llm': 'ChatDotRound',
        'batch': 'DataLine',
        'aggregate': 'Collection',
        'code': 'Document'
      }

      const processTypeColors = {
        'selector': { color: '#67C23A', bgColor: '#f0f9eb' },
        'loop': { color: '#9B59B6', bgColor: '#f9f0ff' },
        'llm': { color: '#9B59B6', bgColor: '#f9f0ff' },
        'batch': { color: '#909399', bgColor: '#f4f4f5' },
        'aggregate': { color: '#7B68EE', bgColor: '#f0f0ff' },
        'code': { color: '#409EFF', bgColor: '#ecf5ff' }
      }
      
      // 创建一个新的节点数据对象，包含所有配置
      const newNodeData = {
        ...node.data,
        ...nodeForm.value,
        label: newLabel,  // 只使用label字段
        icon: processTypeIcons[nodeForm.value.processType],
        color: processTypeColors[nodeForm.value.processType].color,
        bgColor: processTypeColors[nodeForm.value.processType].bgColor,
        // 确保所有配置字段都被保存
        type: nodeForm.value.type,
        description: nodeForm.value.description,
        // 输入节点配置
        inputType: nodeForm.value.inputType,
        defaultValue: nodeForm.value.defaultValue,
        fileType: nodeForm.value.fileType,
        apiUrl: nodeForm.value.apiUrl,
        apiMethod: nodeForm.value.apiMethod,
        // 处理节点配置
        processType: nodeForm.value.processType,
        codeType: nodeForm.value.codeType,
        codeContent: nodeForm.value.codeContent,
        conditionType: nodeForm.value.conditionType,
        conditionValue: nodeForm.value.conditionValue,
        loopType: nodeForm.value.loopType,
        loopCount: nodeForm.value.loopCount,
        loopCondition: nodeForm.value.loopCondition,
        batchSize: nodeForm.value.batchSize,
        parallel: nodeForm.value.parallel,
        aggregateType: nodeForm.value.aggregateType,
        aggregateField: nodeForm.value.aggregateField,
        // 输出节点配置
        outputType: nodeForm.value.outputType,
        fileFormat: nodeForm.value.fileFormat,
        filePath: nodeForm.value.filePath,
        // 选择器配置
        ifCondition: nodeForm.value.ifCondition,
        elseIfConditions: nodeForm.value.elseIfConditions,
        elseCondition: '否则（默认执行路径）', // 固定值
        // 大模型配置
        llmModel: nodeForm.value.llmModel,
        llmPrompt: nodeForm.value.llmPrompt,
        // 监听节点配置
        monitorType: nodeForm.value.monitorType,
        // 智能体配置
        myAgents: nodeForm.value.myAgents,
        followedAgents: nodeForm.value.followedAgents,
        myAgentId: nodeForm.value.myAgentId,
        myAgentName: nodeForm.value.myAgentName,
        followedAgentId: nodeForm.value.followedAgentId,
        followedAgentName: nodeForm.value.followedAgentName,
      }
      
      // 使用 Vue Flow 的 updateNode 方法更新节点
      vueFlowUpdateNode(node.id, {
        data: newNodeData
      })
    }
  } else {
    // 对于非处理节点，同样需要保存所有配置
    const newNodeData = {
      ...node.data,
      ...nodeForm.value,
      label: newLabel,  // 只使用label字段
      color: originalColor,
      bgColor: originalBgColor
    }
    
    vueFlowUpdateNode(node.id, {
      data: newNodeData
    })
  }
  
  drawerVisible.value = false
  // 在updateNode函数末尾添加：
  originalNodeData.value = JSON.parse(JSON.stringify(nodeForm.value))
}

// 删除节点
const deleteNode = () => {
  if (!selectedNode.value) return
  
  // 先清空表单数据和原始数据，这样就不会触发未保存修改的检查
  nodeForm.value = {
    name: '',
    type: '',
    description: '',
    inputType: 'text',
    defaultValue: '',
    fileType: 'text',
    apiUrl: '',
    apiMethod: 'get',
    processType: 'code',
    codeType: 'javascript',
    codeContent: '',
    conditionType: 'equals',
    conditionValue: '',
    loopType: 'fixed',
    loopCount: 1,
    loopCondition: '',
    batchSize: 32,
    parallel: true,
    aggregateType: 'sum',
    aggregateField: '',
    outputType: 'text',
    fileFormat: 'json',
    filePath: '',
    ifCondition: '',
    elseIfConditions: [],
    elseCondition: '',
  }
  
  // 同时清空原始数据
  originalNodeData.value = JSON.parse(JSON.stringify(nodeForm.value))
  
  elements.value = elements.value.filter(el => 
    el.id !== selectedNode.value && 
    !(el.source === selectedNode.value || el.target === selectedNode.value)
  )
  selectedNode.value = null
  handleDrawerClose(true)
  ElMessage.success('节点删除成功')
}

// 处理抽屉关闭
const handleDrawerClose = (isDeleting = false) => {
  // 如果是删除节点操作，直接关闭抽屉
  if (isDeleting) {
    drawerVisible.value = false
    selectedNode.value = null
    return
  }

  // 创建一个新的对象，排除codeContent字段
  const originalWithoutCode = { ...originalNodeData.value }
  delete originalWithoutCode.codeContent
  
  const currentWithoutCode = { ...nodeForm.value }
  delete currentWithoutCode.codeContent
  
  // 只有在除了codeContent之外的其他字段有变化时才显示确认弹窗
  if (JSON.stringify(originalWithoutCode) !== JSON.stringify(currentWithoutCode)) {
    ElMessageBox.confirm(
      '您有未保存的修改，确定要放弃更改吗？',
      '提示',
      {
        confirmButtonText: '放弃更改',
        cancelButtonText: '继续编辑',
        type: 'warning'
      }
    ).then(() => {
      // 如果用户选择放弃更改，恢复原始数据
      nodeForm.value = JSON.parse(JSON.stringify(originalNodeData.value))
      
      // 更新节点数据，恢复原始状态
      if (selectedNode.value) {
        const node = elements.value.find(el => el.id === selectedNode.value)
        if (node && node.data) {
          const newNodeData = {
            ...node.data,
            ...originalNodeData.value,
            // 确保条件数组也被恢复
            elseIfConditions: originalNodeData.value.elseIfConditions || []
          }
          
          // 使用 Vue Flow 的 updateNode 方法更新节点
          vueFlowUpdateNode(node.id, {
            data: newNodeData
          })
        }
      }
      
      drawerVisible.value = false
      selectedNode.value = null
    }).catch(() => {
      // 用户点击继续编辑，保持抽屉打开
      drawerVisible.value = true
    })
  } else {
    drawerVisible.value = false
    selectedNode.value = null
  }
}

// 修改选择变化事件处理
const onSelectionChange = (params) => {
  if (params.nodes.length === 1) {
    const node = params.nodes[0]
    if (!node || !node.id) return
    
    selectedNode.value = node.id
    
    // 更新表单数据
    nodeForm.value = {
      name: node.data?.label || '',
      type: node.data?.type || '',
      description: node.data?.description || '',
      // 输入节点配置
      inputType: node.data?.inputType || 'text',
      defaultValue: node.data?.defaultValue || '',
      fileType: node.data?.fileType || 'text',
      apiUrl: node.data?.apiUrl || '',
      apiMethod: node.data?.apiMethod || 'get',
      // 处理节点配置
      processType: node.data?.processType || 'code',
      codeType: node.data?.codeType || 'javascript',
      codeContent: node.data?.codeContent || '',
      conditionType: node.data?.conditionType || 'equals',
      conditionValue: node.data?.conditionValue || '',
      loopType: node.data?.loopType || 'fixed',
      loopCount: node.data?.loopCount || 1,
      loopCondition: node.data?.loopCondition || '',
      batchSize: node.data?.batchSize || 32,
      parallel: node.data?.parallel ?? true,
      aggregateType: node.data?.aggregateType || 'sum',
      aggregateField: node.data?.aggregateField || '',
      // 输出节点配置
      outputType: node.data?.outputType || 'text',
      fileFormat: node.data?.fileFormat || 'json',
      filePath: node.data?.filePath || '',
      // 选择器配置
      ifCondition: node.data?.ifCondition || '',
      elseIfConditions: node.data?.elseIfConditions || [],
      elseCondition: node.data?.elseCondition || ''
    }
    
    // 保存原始数据
    originalNodeData.value = JSON.parse(JSON.stringify(nodeForm.value))
    
    drawerVisible.value = true
  } else {
    drawerVisible.value = false
    selectedNode.value = null
  }
}

// 节点拖拽结束事件
const handleNodeDragStop = (node) => {
  if (!node || !node.position) return
  console.log('节点位置更新:', node.position)
}

// 连接事件
const handleConnect = (params) => {
  // 检查源节点是否是选择器节点、循环节点或批处理节点
  const sourceNode = elements.value.find(el => el.id === params.source);
  if (sourceNode) {
    if (sourceNode.data.processType === 'loop') {
      // 如果是循环节点，需要检查连接点的ID
      const handleId = params.sourceHandle;
      if (!handleId || (handleId !== 'loop-entry' && handleId !== 'loop-exit' && handleId !== 'default')) {
        ElMessage.warning('请选择有效的循环连接点');
        return;
      }
      
      // 检查目标节点
      const targetNode = elements.value.find(el => el.id === params.target);
      if (targetNode) {
        // 如果源连接点是循环出口，不允许连接到循环入口
        if (handleId === 'loop-exit' && params.targetHandle === 'loop-entry') {
          ElMessage.warning('循环出口不能直接连接到循环入口');
          return;
        }
      }
    }
    if (sourceNode.data.processType === 'selector') {
      // 如果是选择器节点，需要检查连接点的ID
      const handleId = params.sourceHandle;
      if (!handleId) {
        ElMessage.warning('请选择有效的输出连接点');
        return;
      }
    } else if (sourceNode.data.processType === 'loop') {
      // 如果是循环节点，需要检查连接点的ID
      const handleId = params.sourceHandle;
      if (!handleId || (handleId !== 'loop-entry' && handleId !== 'loop-exit' && handleId !== 'default')) {
        ElMessage.warning('请选择有效的循环连接点');
        return;
      }
      
      // 检查目标节点是否是循环节点
      const targetNode = elements.value.find(el => el.id === params.target);
      if (targetNode && targetNode.data.processType === 'loop') {
        // 如果目标也是循环节点，检查连接点
        const targetHandleId = params.targetHandle;
        if (targetHandleId === 'loop-entry' || targetHandleId === 'loop-exit') {
          ElMessage.warning('循环节点之间不能直接连接入口或出口');
          return;
        }
      }
    } else if (sourceNode.data.processType === 'batch') {
      // 如果是批处理节点，需要检查连接点的ID
      const handleId = params.sourceHandle;
      if (!handleId || (handleId !== 'batch-entry' && handleId !== 'batch-exit' && handleId !== 'default')) {
        ElMessage.warning('请选择有效的批处理连接点');
        return;
      }
      
      // 检查目标节点是否是批处理节点
      const targetNode = elements.value.find(el => el.id === params.target);
      if (targetNode && targetNode.data.processType === 'batch') {
        // 如果目标也是批处理节点，检查连接点
        const targetHandleId = params.targetHandle;
        if (targetHandleId === 'batch-entry' || targetHandleId === 'batch-exit') {
          ElMessage.warning('批处理节点之间不能直接连接入口或出口');
          return;
        }
      }
    }
  }

  // 检查目标节点是否是循环节点或批处理节点
  const targetNode = elements.value.find(el => el.id === params.target);
  if (targetNode) {
    if (targetNode.data.processType === 'loop') {
      // 如果目标是循环节点，检查连接点
      const targetHandleId = params.targetHandle;
      if (targetHandleId === 'loop-entry') {
        ElMessage.warning('不能直接连接到循环节点的入口');
        return;
      }
    } else if (targetNode.data.processType === 'batch') {
      // 如果目标是批处理节点，检查连接点
      const targetHandleId = params.targetHandle;
      if (targetHandleId === 'batch-entry') {
        ElMessage.warning('不能直接连接到批处理节点的入口');
        return;
      }
    }
  }

  elements.value.push({
    id: `edge-${params.source}-${params.target}-${params.sourceHandle || ''}`,
    source: params.source,
    target: params.target,
    sourceHandle: params.sourceHandle,
    targetHandle: params.targetHandle,
    type: 'smoothstep',
    animated: true
  });
}

// 添加画布点击事件处理
onPaneClick(() => {
  drawerVisible.value = false
  selectedNode.value = null
})

// 保存工作流
const saveWorkflow = async () => {
  try {
    // 获取token
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }

    // 弹出命名对话框
    await ElMessageBox.prompt('请输入工作流名称', '保存工作流', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^.{1,50}$/,
      inputErrorMessage: '工作流名称长度应在1-50个字符之间',
      inputValue: workflowName.value
    }).then(({ value }) => {
      workflowName.value = value
    }).catch(() => {
      return // 用户取消保存
    })

    // 整理工作流数据
    const workflowData = {
      userId: localStorage.getItem('userId'),
      AgentId: localStorage.getItem('agentId') || 123,
      name: workflowName.value,
      // 添加视口状态
      viewport: {
        x: viewport.value.x,
        y: viewport.value.y,
        zoom: viewport.value.zoom
      },
      // 添加画布配置
      canvasConfig: {
        minZoom: 0.2,
        maxZoom: 4,
        snapToGrid: true,
        panOnDrag: true,
        panOnScroll: true,
        zoomOnScroll: true,
        preventScrolling: true,
        panOnScrollMode: 'free',
        panOnDragMode: 'free',
        touchAction: 'none'
      },
      // 保存所有节点，包括完整的数据
      nodes: elements.value.filter(el => 
        el.type === 'input' || 
        el.type === 'process' || 
        el.type === 'output' ||
        el.type === 'llm' ||
        el.type === 'workflow' ||
        el.type === 'monitor' ||
        el.type === 'dynamic-input'
      ).map(node => ({
        id: node.id,
        type: node.type,
        position: node.position,
        data: {
          // 基本信息
          name: node.data.label, // 使用 label 作为 name，因为它包含了数字后缀
          type: node.data.type,
          label: node.data.label,
          description: node.data.description,
          // 输入节点配置
          inputType: node.data.inputType,
          defaultValue: node.data.defaultValue,
          fileType: node.data.fileType,
          apiUrl: node.data.apiUrl,
          apiMethod: node.data.apiMethod,
          // 处理节点配置
          processType: node.data.processType,
          codeType: node.data.codeType,
          codeContent: node.data.codeContent,
          conditionType: node.data.conditionType,
          conditionValue: node.data.conditionValue,
          loopType: node.data.loopType,
          loopCount: node.data.loopCount,
          loopCondition: node.data.loopCondition,
          batchSize: node.data.batchSize,
          parallel: node.data.parallel,
          aggregateType: node.data.aggregateType,
          aggregateField: node.data.aggregateField,
          // 输出节点配置
          outputType: node.data.outputType,
          fileFormat: node.data.fileFormat,
          filePath: node.data.filePath,
          // 选择器配置
          ifCondition: node.data.ifCondition,
          elseIfConditions: node.data.elseIfConditions,
          elseCondition: node.data.elseCondition,
          // 大模型配置
          llmModel: node.data.llmModel,
          llmPrompt: node.data.llmPrompt,
          // 监听节点配置
          monitorType: node.data.monitorType,
          // 智能体配置
          myAgents: node.data.myAgents,
          followedAgents: node.data.followedAgents,
          // 动态输入配置
          dynamicInputType: node.data.inputType,
          dynamicDefaultValue: node.data.defaultValue,
          dynamicFileType: node.data.fileType,
          dynamicApiUrl: node.data.apiUrl,
          dynamicApiMethod: node.data.apiMethod,
          // 样式配置
          icon: node.data.icon,
          color: node.data.color,
          bgColor: node.data.bgColor
        }
      })),
      edges: elements.value.filter(el => el.type === 'smoothstep').map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.sourceHandle,
        targetHandle: edge.targetHandle,
        type: edge.type,
        animated: edge.animated
      }))
    }

    // 发送到后端
    const response = await fetch('/agent/workflowSave/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(workflowData)
    })

    console.log('保存工作流:', workflowData)

    if (!response.ok) {
      throw new Error('保存工作流失败')
    }

    const result = await response.json()
    if (result.code === 200) {
      ElMessage.success('工作流保存成功')
      router.push('/agent-editor')
    } else {
      throw new Error(result.message || '保存工作流失败')
    }
  } catch (error) {
    console.error('保存工作流失败:', error)
    ElMessage.error('保存工作流失败，请稍后重试')
  }
}

// 清空工作流
const clearWorkflow = () => {
  elements.value = []
  selectedNode.value = null
  drawerVisible.value = false
  ElMessage.warning('工作流已清空')
}

// 加载工作流
const loadWorkflow = async (workflowId) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }

    const response = await fetch(`/agent/workflowLoad/${workflowId}/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('加载工作流失败')
    }

    const result = await response.json()
    console.log('加载工作流:', result)
    if (response.status === 200) {
      const workflowData = result.workflow
      
      console.log('result.object:', result.object)
      // 设置工作流名称
      workflowName.value = workflowData.name
      
      // 清空当前画布
      elements.value = []
      
      // 恢复视口状态
      if (workflowData.viewport) {
        viewport.value = {
          x: workflowData.viewport.x,
          y: workflowData.viewport.y,
          zoom: workflowData.viewport.zoom
        }
      }
      
      // 恢复画布配置
      if (workflowData.canvasConfig) {
        console.log('画布配置已加载:', workflowData.canvasConfig)
      }
      
      // 添加节点
      workflowData.nodes.forEach(node => {
        // 根据节点类型和处理类型确定样式配置
        let icon = ''
        let color = ''
        let bgColor = ''

        if (node.type === 'input') {
          icon = 'Upload'
          color = '#409EFF'
          bgColor = '#f0f9ff'
        } else if (node.type === 'output') {
          icon = 'Download'
          color = '#E6A23C'
          bgColor = '#fdf6ec'
        } else if (node.type === 'process') {
          const processType = node.data.processType
          const processTypeConfig = processTypes.find(type => type.value === processType)
          if (processTypeConfig) {
            icon = processTypeConfig.icon
            color = processTypeConfig.color
            bgColor = processTypeConfig.bgColor
          }
        }

        elements.value.push({
          id: node.id,
          type: node.type,
          position: node.position,
          data: {
            // 基本信息
            name: node.data.label, // 使用 label 作为 name，因为它包含了数字后缀
            type: node.data.type,
            label: node.data.label,
            description: node.data.description,
            // 输入节点配置
            inputType: node.data.inputType,
            defaultValue: node.data.defaultValue,
            fileType: node.data.fileType,
            apiUrl: node.data.apiUrl,
            apiMethod: node.data.apiMethod,
            // 处理节点配置
            processType: node.data.processType,
            codeType: node.data.codeType,
            codeContent: node.data.codeContent,
            conditionType: node.data.conditionType,
            conditionValue: node.data.conditionValue,
            loopType: node.data.loopType,
            loopCount: node.data.loopCount,
            loopCondition: node.data.loopCondition,
            batchSize: node.data.batchSize,
            parallel: node.data.parallel,
            aggregateType: node.data.aggregateType,
            aggregateField: node.data.aggregateField,
            // 输出节点配置
            outputType: node.data.outputType,
            fileFormat: node.data.fileFormat,
            filePath: node.data.filePath,
            // 选择器配置
            ifCondition: node.data.ifCondition || '',
            elseIfConditions: node.data.elseIfConditions || [],
            elseCondition: node.data.elseCondition || '',
            // 大模型配置
            llmModel: node.data.llmModel || 'Qwen',
            llmPrompt: node.data.llmPrompt || '',
            // 监听节点配置
            monitorType: node.data.monitorType || 'all',
            // 智能体配置
            myAgents: node.data.myAgents || [],
            followedAgents: node.data.followedAgents || [],
            // 样式配置
            icon: icon,
            color: color,
            bgColor: bgColor
          }
        })
      })
      
      // 添加边
      workflowData.edges.forEach(edge => {
        elements.value.push({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          sourceHandle: edge.sourceHandle,
          targetHandle: edge.targetHandle,
          type: edge.type,
          animated: edge.animated
        })
      })
      
      ElMessage.success('工作流加载成功')
    } else {
      throw new Error(result.message || '加载工作流失败')
    }
  } catch (error) {
    console.error('加载工作流失败:', error)
    ElMessage.error('加载工作流失败，请稍后重试')
  }
}

// 打开代码编辑器
const openCodeEditor = () => {
  // 保存当前编辑状态
  const currentCode = nodeForm.value.codeContent
  const currentCodeType = nodeForm.value.codeType
  
  // 只传递必要的参数
  const params = new URLSearchParams({
    type: currentCodeType,
    nodeId: selectedNode.value
  })
  
  // 使用相对路径打开新窗口
  const editorUrl = `#/editor?${params.toString()}`
  const editorWindow = window.open(editorUrl, '_blank')
  
  // 等待编辑器窗口加载完成后，通过 postMessage 发送代码内容
  if (editorWindow) {
    editorWindow.onload = () => {
      editorWindow.postMessage({
        type: 'init-code',
        code: currentCode
      }, window.location.origin)
    }
  }
  
  // 监听消息事件，接收从编辑器返回的代码
  window.addEventListener('message', handleEditorMessage)
}

const handleEditorMessage = (event) => {
  // 验证消息来源
  if (event.origin !== window.location.origin) return
  
  // 处理编辑器返回的消息
  if (event.data.type === 'code-update') {
    // 更新表单数据
    nodeForm.value.codeContent = event.data.code
    
    // 直接更新节点数据
    if (selectedNode.value) {
      const node = elements.value.find(el => el.id === selectedNode.value)
      if (node && node.data) {
        const newNodeData = {
          ...node.data,
          codeContent: event.data.code
        }
        
        // 使用 Vue Flow 的 updateNode 方法更新节点
        vueFlowUpdateNode(node.id, {
          data: newNodeData
        })
      }
    }
    
    // 移除消息监听器
    window.removeEventListener('message', handleEditorMessage)
  }
}

// 添加选择器相关的方法
const addElseIfCondition = () => {
  nodeForm.value.elseIfConditions.push({ value: '' })
}

const removeElseIfCondition = (index) => {
  nodeForm.value.elseIfConditions.splice(index, 1)
}

// 在组件挂载时加载工作流（如果有workflowId）
onMounted(() => {
  const workflowId = route.query.id
  if (workflowId) {
    loadWorkflow(workflowId)
  }
  // 检查是否有从智能体列表页面返回的数据
  const selectedAgent = localStorage.getItem('selectedAgent')
  if (selectedAgent) {
    const agent = JSON.parse(selectedAgent)
    const nodeId = localStorage.getItem('currentWorkflowNodeId')
    
    if (nodeId) {
      const node = elements.value.find(el => el.id === nodeId)
      if (node) {
        if (agent.type === 'my') {
          nodeForm.value.myAgentId = agent.id
          nodeForm.value.myAgentName = agent.name
          nodeForm.value.followedAgentId = null
          nodeForm.value.followedAgentName = ''
        } else {
          nodeForm.value.followedAgentId = agent.id
          nodeForm.value.followedAgentName = agent.name
          nodeForm.value.myAgentId = null
          nodeForm.value.myAgentName = ''
        }
        
        // 更新节点数据
        const newNodeData = {
          ...node.data,
          myAgentId: nodeForm.value.myAgentId,
          myAgentName: nodeForm.value.myAgentName,
          followedAgentId: nodeForm.value.followedAgentId,
          followedAgentName: nodeForm.value.followedAgentName
        }
        
        vueFlowUpdateNode(node.id, {
          data: newNodeData
        })
      }
    }
    
    // 清除localStorage中的数据
    localStorage.removeItem('selectedAgent')
    localStorage.removeItem('currentWorkflowNodeId')
  }
})

// 添加智能体选择处理方法
const handleAgentSelect = (type) => {
  if (type === 'myAgents' && nodeForm.value.myAgents) {
    nodeForm.value.followedAgents = null
  } else if (type === 'followedAgents' && nodeForm.value.followedAgents) {
    nodeForm.value.myAgents = null
  }
}

watch(() => nodeForm.value.processType, (newType) => {
  const typeConfig = processTypes.find(type => type.value === newType)
  if (typeConfig) {
    // 只在未手动输入名称时自动更新
    if (!nodeForm.value.name || nodeForm.value.name === '' || nodeForm.value.name === originalNodeData.value.name) {
      nodeForm.value.name = `${typeConfig.label} ${nodeTypeCounters.value.process[newType]}`
    }
  }
})

// 添加选择智能体的方法
const selectMyAgent = () => {
  console.log('选择我的智能体')
  // 保存当前节点ID到localStorage
  localStorage.setItem('currentWorkflowNodeId', selectedNode.value)
  // 跳转到智能体列表页面
  router.push({
    path: '/usable-agent-list',
    query: {
      type: 'my',
      returnPath: '/create-ai'
    }
  })
}

const selectFollowedAgent = () => {
  console.log('选择我关注的智能体')
  // 保存当前节点ID到localStorage
  localStorage.setItem('currentWorkflowNodeId', selectedNode.value)
  // 跳转到智能体列表页面
  router.push({
    path: '/usable-agent-list',
    query: {
      type: 'followed',
      returnPath: '/create-ai'
    }
  })
}

// 添加监听路由变化的方法
onMounted(() => {
  // 检查是否有从智能体列表页面返回的数据
  const selectedAgent = localStorage.getItem('selectedAgent')
  if (selectedAgent) {
    const agent = JSON.parse(selectedAgent)
    const nodeId = localStorage.getItem('currentWorkflowNodeId')
    
    if (nodeId) {
      const node = elements.value.find(el => el.id === nodeId)
      if (node) {
        if (agent.type === 'my') {
          nodeForm.value.myAgentId = agent.id
          nodeForm.value.myAgentName = agent.name
          nodeForm.value.followedAgentId = null
          nodeForm.value.followedAgentName = ''
        } else {
          nodeForm.value.followedAgentId = agent.id
          nodeForm.value.followedAgentName = agent.name
          nodeForm.value.myAgentId = null
          nodeForm.value.myAgentName = ''
        }
        
        // 更新节点数据
        const newNodeData = {
          ...node.data,
          myAgentId: nodeForm.value.myAgentId,
          myAgentName: nodeForm.value.myAgentName,
          followedAgentId: nodeForm.value.followedAgentId,
          followedAgentName: nodeForm.value.followedAgentName
        }
        
        vueFlowUpdateNode(node.id, {
          data: newNodeData
        })
      }
    }
    
    // 清除localStorage中的数据
    localStorage.removeItem('selectedAgent')
    localStorage.removeItem('currentWorkflowNodeId')
  }
})
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
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.workflow-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

:deep(.header-actions .el-button) {
  min-width: 100px;
  height: 36px;
  border-radius: 4px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-weight: 500;
}

:deep(.header-actions .el-button--success) {
  background: #67C23A;
  border-color: #67C23A;
  color: #fff;
}

:deep(.header-actions .el-button--success:hover) {
  background: #85ce61;
  border-color: #85ce61;
}

:deep(.header-actions .el-button--warning) {
  background: #E6A23C;
  border-color: #E6A23C;
  color: #fff;
}

:deep(.header-actions .el-button--warning:hover) {
  background: #ebb563;
  border-color: #ebb563;
}

:deep(.header-actions .el-icon) {
  font-size: 16px;
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
  border: none;
  background: transparent;
  padding: 0;
}

:deep(.vue-flow__node[data-type="input"]),
:deep(.vue-flow__node[data-type="output"]) {
  background: transparent;
}

:deep(.vue-flow__node[data-type="input"] .el-icon),
:deep(.vue-flow__node[data-type="input"] .node-label),
:deep(.vue-flow__node[data-type="output"] .el-icon),
:deep(.vue-flow__node[data-type="output"] .node-label) {
  color: #409EFF;
}

:deep(.vue-flow__node[data-type="input"] .vue-flow__handle),
:deep(.vue-flow__node[data-type="output"] .vue-flow__handle) {
  background: #409EFF;
  border: 2px solid #fff;
}

:deep(.vue-flow__node[data-type="input"] .node-common),
:deep(.vue-flow__node[data-type="output"] .node-common) {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

.input-node,
.output-node {
  padding: 10px 15px;
  border-radius: 8px;
  border: 2px solid #409EFF;
  min-width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  background-color: #f0f9ff;
  touch-action: none;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  user-select: none;
  cursor: move;
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
  background: #fdf6ec;
  border-color: #E6A23C;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="selector"]) {
  background: #f0f9eb;
  border-color: #67C23A;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="loop"]) {
  background: #f9f0ff;
  border-color: #9B59B6;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="llm"]) {
  background: #f9f0ff;
  border-color: #9B59B6;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="batch"]) {
  background: #f4f4f5;
  border-color: #909399;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="aggregate"]) {
  background: #f0f0ff;
  border-color: #7B68EE;
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
  color: #E6A23C;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="selector"] .process-type-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="selector"] .vue-flow__node-label) {
  color: #67C23A;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="loop"] .process-type-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="loop"] .vue-flow__node-label) {
  color: #9B59B6;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="llm"] .process-type-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="llm"] .vue-flow__node-label) {
  color: '#9B59B6';
}

:deep(.vue-flow__node[data-type="process"][data-process-type="batch"] .process-type-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="batch"] .vue-flow__node-label) {
  color: #909399;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="aggregate"] .process-type-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="aggregate"] .vue-flow__node-label) {
  color: #7B68EE;
}

:deep(.vue-flow__node[data-type="llm"]) {
  background: #f9f0ff;
  border-color: #9B59B6;
}

:deep(.vue-flow__node[data-type="workflow"]) {
  background: #f0f0ff;
  border-color: #7B68EE;
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

.node-config-drawer {
  z-index: 2000;
}

:deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  background: #f5f7fa;
  color: #303133;
  font-weight: 500;
  border-radius: 8px 8px 0 0;
}

:deep(.el-drawer__body) {
  padding: 0;
  height: calc(100% - 57px);
  background: #f5f7fa;
}

:deep(.el-drawer.rtl) {
  width: 400px !important;
  border-radius: 8px 0 0 8px;
}

:deep(.el-drawer__wrapper) {
  transition: all 0.3s ease-in-out;
}

:deep(.el-drawer__container) {
  transition: all 0.3s ease-in-out;
}

.node-form {
  padding: 20px;
}

.form-card {
  margin-bottom: 20px;
  border-radius: 8px;
  border: none;
  background: #fff;
}

.form-card:last-child {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  color: #303133;
}

:deep(.el-card__header) {
  padding: 12px 20px;
  border-bottom: 1px solid #ebeef5;
  background: #f5f7fa;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

:deep(.el-input__inner),
:deep(.el-textarea__inner) {
  border-radius: 4px;
  transition: all 0.3s;
}

:deep(.el-input__inner:focus),
:deep(.el-textarea__inner:focus) {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

:deep(.el-button) {
  border-radius: 4px;
  transition: all 0.3s;
  padding: 10px 20px;
}

:deep(.el-button--primary) {
  background: #409EFF;
  border-color: #409EFF;
}

:deep(.el-button--primary:hover) {
  background: #66b1ff;
  border-color: #66b1ff;
}

:deep(.el-button--danger) {
  background: #F56C6C;
  border-color: #F56C6C;
}

:deep(.el-button--danger:hover) {
  background: #f78989;
  border-color: #f78989;
}

:deep(.el-select .el-input__inner) {
  padding-right: 30px;
}

:deep(.el-select .el-input__suffix) {
  right: 5px;
}

:deep(.el-select-dropdown__item) {
  padding: 0 20px;
  height: 34px;
  line-height: 34px;
}

:deep(.el-select-dropdown__item.selected) {
  color: #409EFF;
  font-weight: 700;
}

:deep(.el-switch) {
  height: 20px;
}

:deep(.el-switch__core) {
  width: 40px !important;
  height: 20px;
  border-radius: 10px;
}

:deep(.el-switch.is-checked .el-switch__core) {
  border-color: #409EFF;
  background-color: #409EFF;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

:deep(.el-button) {
  min-width: 100px;
  height: 36px;
  border-radius: 4px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

:deep(.el-button--success) {
  background: #67C23A;
  border-color: #67C23A;
  color: #fff;
}

:deep(.el-button--success:hover) {
  background: #85ce61;
  border-color: #85ce61;
}

:deep(.el-button--danger) {
  background: #F56C6C;
  border-color: #F56C6C;
  color: #fff;
}

:deep(.el-button--danger:hover) {
  background: #f78989;
  border-color: #f78989;
}

:deep(.el-button:not(.el-button--success):not(.el-button--danger)) {
  background: #f4f4f5;
  border-color: #d9d9d9;
  color: #606266;
}

:deep(.el-button:not(.el-button--success):not(.el-button--danger):hover) {
  background: #e9e9eb;
  border-color: #c6c6c6;
  color: #606266;
}

:deep(.el-icon) {
  font-size: 16px;
}

:deep(.process-type-dialog .el-dialog__footer) {
  padding: 20px;
  border-top: 1px solid #ebeef5;
  background: #f5f7fa;
  border-radius: 0 0 8px 8px;
  display: flex;
  justify-content: flex-end;
}

:deep(.process-type-dialog .el-dialog__footer .el-button-group) {
  display: flex;
  gap: 1px;
}

:deep(.process-type-dialog .el-dialog__footer .el-button-group .el-button) {
  min-width: 100px;
  height: 36px;
  border-radius: 0;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-weight: 500;
  margin: 0;
  padding: 0 20px;
}

:deep(.process-type-dialog .el-dialog__footer .el-button-group .el-button:first-child) {
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}

:deep(.process-type-dialog .el-dialog__footer .el-button-group .el-button:last-child) {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}

:deep(.process-type-dialog .el-dialog__footer .el-button-group .el-button--primary) {
  background: #409EFF;
  border-color: #409EFF;
  color: #fff;
}

:deep(.process-type-dialog .el-dialog__footer .el-button-group .el-button--primary:hover) {
  background: #66b1ff;
  border-color: #66b1ff;
}

:deep(.process-type-dialog .el-dialog__footer .el-button-group .el-button:not(.el-button--primary)) {
  background: #f4f4f5;
  border-color: #d9d9d9;
  color: #606266;
}

:deep(.process-type-dialog .el-dialog__footer .el-button-group .el-button:not(.el-button--primary):hover) {
  background: #e9e9eb;
  border-color: #c6c6c6;
  color: #606266;
}

.code-editor-action {
  display: flex;
  justify-content: flex-start;
  margin: 0;
}

.code-editor-btn {
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 4px;
  background-color: #409EFF;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
  height: 32px;
}

.code-editor-btn:hover {
  background-color: #66b1ff;
}

.code-editor-btn .el-icon {
  font-size: 16px;
}

.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

:deep(.el-tooltip__trigger) {
  width: 100%;
  height: 100%;
}

:deep(.el-tooltip__content) {
  max-width: 600px;
  max-height: 400px;
  overflow: auto;
  white-space: pre;
  word-break: normal;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 0;
  background-color: #1e1e1e;
  border: 1px solid #333;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.3);
  color: #d4d4d4;
  tab-size: 4;
}

:deep(.el-tooltip__content pre) {
  margin: 0;
  padding: 12px;
  background-color: #1e1e1e;
  color: #d4d4d4;
  white-space: pre;
  word-break: normal;
  tab-size: 4;
}

:deep(.el-tooltip__content code) {
  display: block;
  background-color: #1e1e1e;
  color: #d4d4d4;
  white-space: pre;
  word-break: normal;
  tab-size: 4;
}

:deep(.el-tooltip__content::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:deep(.el-tooltip__content::-webkit-scrollbar-track) {
  background: #1e1e1e;
  border-radius: 4px;
}

:deep(.el-tooltip__content::-webkit-scrollbar-thumb) {
  background: #3c3c3c;
  border-radius: 4px;
}

:deep(.el-tooltip__content::-webkit-scrollbar-thumb:hover) {
  background: #4c4c4c;
}

:deep(.el-tooltip__content::-webkit-scrollbar-corner) {
  background: #1e1e1e;
}

.condition-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.condition-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.add-condition-btn {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

:deep(.el-button--danger.is-circle) {
  padding: 6px;
  min-width: auto;
  height: auto;
}

.selector-handles {
  position: relative;
  width: 100%;
  height: 20px;
  margin-top: 10px;
}

:deep(.vue-flow__handle[data-handleid^="elseif"]) {
  transform: translateX(-50%);
}

:deep(.vue-flow__handle[data-handleid="if"]) {
  transform: translateX(-50%);
}

:deep(.vue-flow__handle[data-handleid="else"]) {
  transform: translateX(-50%);
}

.handle-label {
  position: absolute;
  font-size: 12px;
  color: #666;
  transform: translateX(-50%);
  white-space: nowrap;
  top: 15px;
  font-weight: bold;
}

.loop-handles {
  position: relative;
  width: 100%;
  height: 20px;
  margin-top: 10px;
}

.loop-side-handles {
  position: absolute;
  right: -4px;
  top: 0;
  bottom: 0;
  width: 8px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

:deep(.vue-flow__handle[data-handleid="loop-entry"]) {
  transform: translateY(-50%);
  right: -4px;
}

:deep(.vue-flow__handle[data-handleid="loop-exit"]) {
  transform: translateY(-50%);
  right: -4px;
}

:deep(.vue-flow__handle[data-handleid="default"]) {
  transform: translateX(-50%);
}

.loop-handle-label {
  position: absolute;
  font-size: 12px;
  color: #666;
  transform: translateX(-50%);
  white-space: nowrap;
  top: 15px;
  font-weight: bold;
}

.config-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.config-group-title {
  font-weight: bold;
  color: #606266;
}

.empty-config-tip {
  padding: 20px;
  text-align: center;
}

:deep(.el-empty__description) {
  margin-top: 10px;
}

:deep(.el-scrollbar__wrap) {
  overflow-x: hidden;
}

:deep(.el-scrollbar__bar.is-horizontal) {
  display: none;
}

:deep(.el-card__body) {
  padding: 0;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}

:deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

.batch-handles {
  position: relative;
  width: 100%;
  height: 20px;
  margin-top: 10px;
}

.batch-side-handles {
  position: absolute;
  left: -4px;
  top: 0;
  bottom: 0;
  width: 8px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

:deep(.vue-flow__handle[data-handleid="batch-entry"]) {
  transform: translateY(-50%);
  left: -4px;
}

:deep(.vue-flow__handle[data-handleid="batch-exit"]) {
  transform: translateY(-50%);
  left: -4px;
}

:deep(.vue-flow__handle[data-handleid="default"]) {
  transform: translateX(-50%);
}

/* 工作流画布中的 tooltip 样式 */
:deep(.flow-handle-tooltip) {
  z-index: 2000;
}

:deep(.flow-handle-tooltip .el-tooltip__trigger) {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid #fff;
  position: relative;
  cursor: pointer;
}

:deep(.flow-handle-tooltip .el-tooltip__popper) {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 12px;
  color: #606266;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

:deep(.flow-handle-tooltip .el-tooltip__popper.is-light) {
  background: #fff;
  border: 1px solid #ebeef5;
}

:deep(.flow-handle-tooltip .el-tooltip__popper.is-light[x-placement^="top"] .popper__arrow) {
  border-top-color: #ebeef5;
}

:deep(.flow-handle-tooltip .el-tooltip__popper.is-light[x-placement^="bottom"] .popper__arrow) {
  border-bottom-color: #ebeef5;
}

:deep(.flow-handle-tooltip .el-tooltip__popper.is-light[x-placement^="left"] .popper__arrow) {
  border-left-color: #ebeef5;
}

:deep(.flow-handle-tooltip .el-tooltip__popper.is-light[x-placement^="right"] .popper__arrow) {
  border-right-color: #ebeef5;
}

/* 节点代码内容的 tooltip 样式 */
:deep(.flow-node-tooltip) {
  z-index: 2000;
}

:deep(.flow-node-tooltip .el-tooltip__popper) {
  max-width: 600px;
  max-height: 400px;
  overflow: auto;
  white-space: pre;
  word-break: normal;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 0;
  background-color: #1e1e1e;
  border: 1px solid #333;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.3);
  color: #d4d4d4;
  tab-size: 4;
}

:deep(.flow-node-tooltip .el-tooltip__popper pre) {
  margin: 0;
  padding: 12px;
  background-color: #1e1e1e;
  color: #d4d4d4;
  white-space: pre;
  word-break: normal;
  tab-size: 4;
}

:deep(.flow-node-tooltip .el-tooltip__popper code) {
  display: block;
  background-color: #1e1e1e;
  color: #d4d4d4;
  white-space: pre;
  word-break: normal;
  tab-size: 4;
}

:deep(.flow-node-tooltip .el-tooltip__popper::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:deep(.flow-node-tooltip .el-tooltip__popper::-webkit-scrollbar-track) {
  background: #1e1e1e;
  border-radius: 4px;
}

:deep(.flow-node-tooltip .el-tooltip__popper::-webkit-scrollbar-thumb) {
  background: #3c3c3c;
  border-radius: 4px;
}

:deep(.flow-node-tooltip .el-tooltip__popper::-webkit-scrollbar-thumb:hover) {
  background: #4c4c4c;
}

:deep(.flow-node-tooltip .el-tooltip__popper::-webkit-scrollbar-corner) {
  background: #1e1e1e;
}

/* 修复连接点定位问题 */
:deep(.vue-flow__handle) {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid #fff;
  position: absolute;
  z-index: 1;
}

:deep(.vue-flow__handle-top) {
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
}

:deep(.vue-flow__handle-bottom) {
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
}

:deep(.vue-flow__handle-left) {
  left: -4px;
  top: 50%;
  transform: translateY(-50%);
}

:deep(.vue-flow__handle-right) {
  right: -4px;
  top: 50%;
  transform: translateY(-50%);
}

/* 确保连接点容器正确定位 */
.selector-handles,
.loop-handles,
.batch-handles {
  position: relative;
  width: 100%;
  height: 20px;
  margin-top: 10px;
}

.loop-side-handles,
.batch-side-handles {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 8px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.loop-side-handles {
  right: -4px;
}

.batch-side-handles {
  left: -4px;
}

.code-tooltip-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.code-tooltip-wrapper:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.node-icon-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

:deep(.vue-flow__node[data-type="input"]) {
  background: #f0f9ff;
  border-color: #409EFF;
}

:deep(.vue-flow__node[data-type="output"]) {
  background: #f0f9ff;
  border-color: #409EFF;
}

:deep(.vue-flow__node[data-type="input"] .el-icon),
:deep(.vue-flow__node[data-type="input"] .node-label),
:deep(.vue-flow__node[data-type="output"] .el-icon),
:deep(.vue-flow__node[data-type="output"] .node-label) {
  color: #409EFF;
}

:deep(.vue-flow__node[data-type="input"] .vue-flow__handle),
:deep(.vue-flow__node[data-type="output"] .vue-flow__handle) {
  background: #409EFF;
  border: 2px solid #fff;
}

:deep(.vue-flow__node[data-type="input"] .vue-flow__handle-top),
:deep(.vue-flow__node[data-type="output"] .vue-flow__handle-top) {
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
}

:deep(.vue-flow__node[data-type="input"] .vue-flow__handle-bottom),
:deep(.vue-flow__node[data-type="output"] .vue-flow__handle-bottom) {
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
}

.node-common {
  padding: 10px 15px;
  border-radius: 8px;
  border: 2px solid #409EFF;
  min-width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  background-color: #f0f9ff;
  touch-action: none;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  user-select: none;
  cursor: move;
}

.input-node,
.output-node,
.process-node,
.llm-node,
.workflow-node {
  padding: 10px 15px;
  border-radius: 8px;
  border: 2px solid;
  min-width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  touch-action: none;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  user-select: none;
  cursor: move;
}

:deep(.vue-flow__node[data-type="input"]) {
  background: #f0f9ff;
  border-color: #409EFF;
}

:deep(.vue-flow__node[data-type="output"]) {
  background: #f0f9ff;
  border-color: #409EFF;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="code"]) {
  background: #fdf6ec;
  border-color: #E6A23C;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="selector"]) {
  background: #f0f9eb;
  border-color: #67C23A;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="loop"]) {
  background: #f9f0ff;
  border-color: #9B59B6;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="llm"]) {
  background: #f9f0ff;
  border-color: #9B59B6;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="batch"]) {
  background: #f4f4f5;
  border-color: #909399;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="aggregate"]) {
  background: #f0f0ff;
  border-color: #7B68EE;
}

:deep(.vue-flow__node[data-type="workflow"]) {
  background: #f0f0ff;
  border-color: #7B68EE;
}

:deep(.vue-flow__node[data-type="input"] .el-icon),
:deep(.vue-flow__node[data-type="input"] .node-label) {
  color: #409EFF;
}

:deep(.vue-flow__node[data-type="output"] .el-icon),
:deep(.vue-flow__node[data-type="output"] .node-label) {
  color: #409EFF;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="code"] .el-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="code"] .node-label) {
  color: #E6A23C;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="selector"] .el-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="selector"] .node-label) {
  color: #67C23A;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="loop"] .el-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="loop"] .node-label) {
  color: #9B59B6;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="llm"] .el-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="llm"] .node-label) {
  color: #9B59B6;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="batch"] .el-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="batch"] .node-label) {
  color: #909399;
}

:deep(.vue-flow__node[data-type="process"][data-process-type="aggregate"] .el-icon),
:deep(.vue-flow__node[data-type="process"][data-process-type="aggregate"] .node-label) {
  color: #7B68EE;
}

:deep(.vue-flow__node[data-type="workflow"] .el-icon),
:deep(.vue-flow__node[data-type="workflow"] .node-label) {
  color: #7B68EE;
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

:deep(.vue-flow__node[data-type="input"] .vue-flow__handle),
:deep(.vue-flow__node[data-type="output"] .vue-flow__handle) {
  background: #409EFF;
}

:deep(.vue-flow__node[data-type="process"] .vue-flow__handle) {
  background: currentColor;
}

:deep(.vue-flow__node[data-type="llm"] .vue-flow__handle) {
  background: #9B59B6;
}

:deep(.vue-flow__node[data-type="workflow"] .vue-flow__handle) {
  background: #7B68EE;
}

.dynamic-input-node,
.monitor-node {
  padding: 10px 15px;
  border-radius: 8px;
  border: 2px solid;
  min-width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  touch-action: none;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  user-select: none;
  cursor: move;
}

:deep(.vue-flow__node[data-type="dynamic-input"]) {
  background: #f0f9ff;
  border-color: #409EFF;
}

:deep(.vue-flow__node[data-type="monitor"]) {
  background: #fff0f0;
  border-color: #F56C6C;
}

:deep(.vue-flow__node[data-type="dynamic-input"] .el-icon),
:deep(.vue-flow__node[data-type="dynamic-input"] .node-label) {
  color: #409EFF;
}

:deep(.vue-flow__node[data-type="monitor"] .el-icon),
:deep(.vue-flow__node[data-type="monitor"] .node-label) {
  color: #F56C6C;
}

:deep(.vue-flow__node[data-type="dynamic-input"] .vue-flow__handle) {
  background: #409EFF;
}

:deep(.vue-flow__node[data-type="monitor"] .vue-flow__handle) {
  background: #F56C6C;
}

.agent-select-container {
  display: flex;
  align-items: center;
  width: 100%;
}

.agent-select-container :deep(.el-input) {
  width: 100%;
}

.agent-select-container :deep(.el-input__wrapper) {
  padding-right: 0;
}

.agent-select-container :deep(.el-input-group__append) {
  padding: 0;
  background-color: transparent;
}

.agent-select-container :deep(.el-button) {
  border-radius: 0 4px 4px 0;
  margin: 0;
  height: 100%;
  padding: 0 15px;
}

.agent-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.agent-buttons :deep(.el-button) {
  min-width: 100px;
  height: 36px;
  border-radius: 4px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-weight: 500;
}

.agent-buttons :deep(.el-button--primary) {
  background: #409EFF;
  border-color: #409EFF;
  color: #fff;
}

.agent-buttons :deep(.el-button--primary:hover) {
  background: #66b1ff;
  border-color: #66b1ff;
}
</style>
