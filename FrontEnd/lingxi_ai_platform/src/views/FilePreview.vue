<template>
  <div class="file-preview-container">
    <div v-if="loading" class="preview-loading">
      <el-skeleton :rows="15" animated />
    </div>
    
    <!-- PDF预览 -->
    <div v-else-if="fileType === 'pdf'" class="pdf-preview">
      <iframe v-if="directUrl" :src="directUrl" width="100%" height="600" frameborder="0"></iframe>
      <div v-else ref="pdfContainer" class="pdf-container"></div>
    </div>
    
    <!-- 图片预览 -->
    <div v-else-if="fileType === 'image'" class="image-preview">
      <img :src="directUrl" :alt="fileName" style="max-width: 100%;">
    </div>
    
    <!-- 文本预览 -->
    <div v-else-if="fileType === 'text'" class="text-preview">
      <pre>{{ fileContent }}</pre>
    </div>
    
    <!-- HTML预览 (Markdown或DOCX转换后) -->
    <div v-else-if="fileType === 'html'" class="html-preview">
      <div v-html="fileContent"></div>
    </div>
    
    <!-- 不支持的文件类型 -->
    <div v-else class="unsupported-preview">
      <el-empty description="不支持预览此类型的文件" />
      <el-button v-if="directUrl" type="primary" @click="downloadFile">下载文件</el-button>
    </div>
    
    <!-- 预览控制栏 -->
    <div class="preview-toolbar">
      <el-button-group>
        <el-button v-if="hasRawContent" @click="toggleRawContent">
          {{ showRawContent ? '查看渲染内容' : '查看原始内容' }}
        </el-button>
        <el-button v-if="directUrl" @click="downloadFile">下载</el-button>
      </el-button-group>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';

// 配置marked
marked.setOptions({
  highlight: function(code, lang) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
    return hljs.highlight(code, { language }).value;
  },
  langPrefix: 'hljs language-'
});

// Props
const props = defineProps({
  fileId: {
    type: String,
    required: true
  },
  knowledgeBaseId: {
    type: String,
    required: true
  },
  fileName: {
    type: String,
    default: ''
  },
  fileSize: {
    type: Number,
    default: 0
  }
});

// 状态
const loading = ref(true);
const fileType = ref(''); // 'pdf', 'image', 'text', 'html'
const fileContent = ref('');
const rawContent = ref('');
const directUrl = ref('');
const error = ref(null);
const pdfContainer = ref(null);
const showRawContent = ref(false);

// 计算属性
const hasRawContent = computed(() => rawContent.value && fileContent.value !== rawContent.value);
const displayContent = computed(() => showRawContent.value ? rawContent.value : fileContent.value);

// 获取文件类型
const getFileTypeFromName = (fileName) => {
  const ext = fileName.split('.').pop().toLowerCase();
  if (['pdf'].includes(ext)) return 'pdf';
  if (['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(ext)) return 'image';
  if (['txt', 'log', 'csv'].includes(ext)) return 'text';
  if (['md', 'docx'].includes(ext)) return 'html';
  return 'unknown';
};

// 切换原始内容/渲染内容
const toggleRawContent = () => {
  showRawContent.value = !showRawContent.value;
};

// 下载文件
const downloadFile = () => {
  if (directUrl.value) {
    const link = document.createElement('a');
    link.href = directUrl.value;
    link.download = props.fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

// 加载文件
const loadFile = async () => {
  try {
    loading.value = true;
    
    // 根据文件名确定初始文件类型
    fileType.value = getFileTypeFromName(props.fileName);
    
    // 构建预览URL
    const previewUrl = `/knowledge_base/knowledgebase/${props.knowledgeBaseId}/file/${props.fileId}/preview/`;
    
    // 对于PDF和图片，直接使用URL加载
    if (fileType.value === 'pdf' || fileType.value === 'image') {
      directUrl.value = `/knowledge_base/knowledgebase/${props.knowledgeBaseId}/file/${props.fileId}/content/`;
      
      // 添加认证Token (如果API需要认证)
      const token = localStorage.getItem('token');
      if (token) {
        // 对于简单的情况，可以用URL参数传递token
        // 更安全的方式是使用fetch API获取blob并创建本地URL
        const response = await fetch(directUrl.value, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!response.ok) {
          throw new Error('你无权查看此文件');
        }
        
        const blob = await response.blob();
        directUrl.value = URL.createObjectURL(blob);
      }
    } else {
      // 对于文本和HTML内容，通过API获取
      const token = localStorage.getItem('token');
      const response = await fetch(previewUrl, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('你无权查看此文件');
      }
      
      const result = await response.json();
      
      if (result.code === 200) {
        fileType.value = result.data.type;
        fileContent.value = result.data.content;
        
        // 保存原始内容以便切换显示
        if (result.data.raw) {
          rawContent.value = result.data.raw;
        } else if (result.data.text) {
          rawContent.value = result.data.text;
        }
      } else {
        throw new Error(result.message || '你无权查看此文件');
      }
    }
  } catch (err) {
    console.error('加载文件预览失败:', err);
    error.value = err.message;
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
};

// 初始加载
onMounted(() => {
  loadFile();
});

// 监听文件ID变化，重新加载
watch(() => props.fileId, (newId, oldId) => {
  if (newId !== oldId) {
    loadFile();
  }
});
</script>

<style scoped>
.file-preview-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 300px;
}

.preview-loading {
  padding: 20px;
  background-color: #f8f8f8;
  border-radius: 4px;
}

.pdf-container {
  height: 600px;
  overflow: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.text-preview {
  padding: 16px;
  background-color: #f8f8f8;
  border-radius: 4px;
  overflow: auto;
  max-height: 600px;
}

.text-preview pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'Courier New', Courier, monospace;
}

.html-preview {
  padding: 16px;
  overflow: auto;
  max-height: 600px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.preview-toolbar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* 添加一些基础的HTML内容样式 */
.html-preview :deep(h1), 
.html-preview :deep(h2), 
.html-preview :deep(h3) {
  margin-top: 16px;
  margin-bottom: 8px;
}

.html-preview :deep(p) {
  margin-bottom: 16px;
}

.html-preview :deep(ul), 
.html-preview :deep(ol) {
  padding-left: 24px;
}

.html-preview :deep(pre) {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>