<template>
  <div class="editor-container">
    <div class="editor-header">
      <h2>代码编辑器</h2>
      <div class="header-actions">
        <el-button type="primary" @click="saveCode">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
        <el-button @click="closeEditor">
          <el-icon><Close /></el-icon>
          关闭
        </el-button>
      </div>
    </div>
    
    <div class="editor-content">
      <el-select v-model="codeType" class="code-type-select">
        <el-option label="JavaScript" value="javascript" />
        <el-option label="Python" value="python" />
      </el-select>
      
      <div class="code-editor-wrapper">
        <textarea
          v-model="code"
          class="code-editor"
          :style="{ 'font-family': codeType === 'python' ? 'monospace' : 'Consolas, Monaco, monospace' }"
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check, Close } from '@element-plus/icons-vue'

const route = useRoute()
const code = ref('')
const codeType = ref('javascript')

// 监听父窗口的消息
onMounted(() => {
  // 从 URL 参数获取代码类型和节点 ID
  codeType.value = route.query.type || 'javascript'
  
  // 监听父窗口的消息
  window.addEventListener('message', (event) => {
    if (event.origin !== window.location.origin) return
    
    if (event.data.type === 'init-code') {
      code.value = event.data.code || ''
    }
  })
  
  // 通知父窗口编辑器已加载
  window.opener?.postMessage({
    type: 'editor-ready'
  }, window.location.origin)
})

// 保存代码
const saveCode = () => {
  if (!code.value.trim()) {
    ElMessage.warning('请输入代码内容')
    return
  }
  
  // 发送代码到父窗口
  window.opener?.postMessage({
    type: 'code-update',
    code: code.value,
    codeType: codeType.value
  }, window.location.origin)
  
  ElMessage.success('代码已保存')
}

// 关闭编辑器
const closeEditor = () => {
  window.close()
}
</script>

<style scoped>
.editor-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.editor-header {
  padding: 15px 20px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.editor-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.editor-content {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.code-type-select {
  width: 200px;
}

.code-editor-wrapper {
  flex: 1;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.code-editor {
  width: 100%;
  height: 100%;
  padding: 20px;
  border: none;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  background: #1e1e1e;
  color: #d4d4d4;
  tab-size: 4;
}

.code-editor:focus {
  outline: none;
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

:deep(.el-button--primary) {
  background: #409EFF;
  border-color: #409EFF;
  color: #fff;
}

:deep(.el-button--primary:hover) {
  background: #66b1ff;
  border-color: #66b1ff;
}

:deep(.el-button:not(.el-button--primary)) {
  background: #f4f4f5;
  border-color: #d9d9d9;
  color: #606266;
}

:deep(.el-button:not(.el-button--primary):hover) {
  background: #e9e9eb;
  border-color: #c6c6c6;
  color: #606266;
}

:deep(.el-icon) {
  font-size: 16px;
}
</style> 