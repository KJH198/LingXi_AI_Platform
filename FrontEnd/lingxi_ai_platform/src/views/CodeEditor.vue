<template>
  <div class="code-editor-container">
    <div class="editor-header">
      <h2>代码编辑器</h2>
      <div class="editor-actions">
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
      <el-input
        v-model="code"
        type="textarea"
        :rows="20"
        placeholder="请输入代码..."
        class="code-input"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Check, Close } from '@element-plus/icons-vue'

const route = useRoute()
const code = ref('')

onMounted(() => {
  // 从URL参数中获取代码和类型
  const encodedCode = route.query.code
  const codeType = route.query.type
  
  if (encodedCode) {
    // 确保换行符被正确解码
    code.value = decodeURIComponent(encodedCode).replace(/%0A/g, '\n')
  }
})

const saveCode = () => {
  // 发送消息给父窗口
  window.opener.postMessage({
    type: 'code-update',
    code: code.value
  }, window.location.origin)
  
  // 关闭窗口
  window.close()
}

const closeEditor = () => {
  window.close()
}
</script>

<style scoped>
.code-editor-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background-color: #1e1e1e;
  margin: 0;
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.editor-header {
  padding: 12px 20px;
  background-color: #252526;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.editor-header h2 {
  margin: 0;
  font-size: 18px;
  color: #cccccc;
  font-weight: 500;
}

.editor-actions {
  display: flex;
  gap: 8px;
}

.editor-content {
  flex: 1;
  padding: 0;
  overflow: hidden;
}

.code-input {
  height: 100%;
  width: 100%;
}

:deep(.code-input .el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  background-color: #1e1e1e;
  color: #d4d4d4;
  border: none;
  resize: none;
  padding: 16px;
  height: 100%;
}

:deep(.code-input .el-textarea__inner:focus) {
  border: none;
  box-shadow: none;
}

:deep(.code-input .el-textarea__inner::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:deep(.code-input .el-textarea__inner::-webkit-scrollbar-thumb) {
  background-color: #3c3c3c;
  border-radius: 4px;
}

:deep(.code-input .el-textarea__inner::-webkit-scrollbar-track) {
  background-color: #1e1e1e;
  border-radius: 4px;
}

:deep(.el-button) {
  padding: 8px 16px;
  font-size: 14px;
}

:deep(.el-button--primary) {
  background-color: #0e639c;
  border-color: #0e639c;
}

:deep(.el-button--primary:hover) {
  background-color: #1177bb;
  border-color: #1177bb;
}
</style> 