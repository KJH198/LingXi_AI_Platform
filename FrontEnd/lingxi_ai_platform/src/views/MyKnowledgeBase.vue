<template>
    <div class="my-kb-container">
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-button 
              @click="router.push('/community')" 
              type="primary" 
              plain
              size="medium"
              icon="ArrowLeft"
            >
              返回社区
            </el-button>
            <h2>我的知识库</h2>
          </div>
          <el-button type="primary" @click="createKnowledgeDialogVisible = true">
            <el-icon class="el-icon--left"><Plus /></el-icon>创建新知识库
          </el-button>
        </el-header>

        <!-- 添加标签页 -->
        <el-tabs v-model="activeTab" class="kb-tabs">
          <el-tab-pane label="我创建的" name="created"></el-tab-pane>
          <el-tab-pane label="我关注的" name="followed"></el-tab-pane>
        </el-tabs>
  
        <el-main>
          <!-- 我创建的知识库 -->
          <template v-if="activeTab === 'created'">
            <!-- 知识库列表 -->
            <div class="kb-grid" v-if="knowledgeBases.length > 0">
              <el-card v-for="kb in knowledgeBases" :key="kb.id" class="kb-card" shadow="hover">
                <div class="kb-content">
                  <!-- 知识库标题和图标 -->
                  <div class="kb-header">
                    <div class="kb-icon">
                      <el-icon size="24"><Folder /></el-icon>
                    </div>
                    <h3 class="kb-name" @click="viewKnowledgeBase(kb)">{{ kb.name }}</h3>
                  </div>
                  
                  <!-- 知识库描述 -->
                  <p class="kb-description">{{ kb.description }}</p>
                  
                  <!-- 知识库统计 -->
                  <div class="kb-stats">
                    <div class="kb-stat">
                      <el-icon><Document /></el-icon>
                      <span>{{ kb.fileCount }} 个文件</span>
                    </div>
                    <div class="kb-stat">
                      <el-icon><View /></el-icon>
                      <span>{{ kb.views }} 次浏览</span>
                    </div>
                    <div class="kb-stat">
                      <el-icon><Star /></el-icon>
                      <span>{{ kb.followers }} 人关注</span>
                    </div>
                  </div>
                  
                  <!-- 最后更新时间 -->
                  <div class="kb-update-time">
                    <el-icon><Timer /></el-icon>
                    <span>更新于 {{ kb.lastUpdated }}</span>
                  </div>
                  
                  <!-- 知识库操作 -->
                  <div class="kb-actions">
                    <el-button type="primary" size="small" @click="viewKnowledgeBase(kb)">
                      <el-icon class="el-icon--left"><View /></el-icon>查看
                    </el-button>
                    <el-button type="success" size="small" @click="openUploadDialogForKb(kb)">
                      <el-icon class="el-icon--left"><UploadFilled /></el-icon>上传文件
                    </el-button>
                    <el-button type="danger" size="small" @click="deleteKnowledgeBase(kb)">
                      <el-icon class="el-icon--left"><Delete /></el-icon>删除
                    </el-button>
                    <el-button type="info" size="small" @click="shareKnowledgeBase(kb)">
                      <el-icon class="el-icon--left"><Share /></el-icon>分享
                    </el-button>
                  </div>
                </div>
              </el-card>
            </div>
  
            <!-- 空状态展示 -->
            <el-empty 
              v-else 
              description="暂无知识库" 
              :image-size="200"
            >
              <el-button type="primary" @click="createKnowledgeDialogVisible = true">
                <el-icon class="el-icon--left"><Plus /></el-icon>创建第一个知识库
              </el-button>
            </el-empty>
  
            <!-- 分页 -->
            <div class="pagination" v-if="knowledgeBases.length > 0">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[12, 24, 36, 48]"
                layout="total, sizes, prev, pager, next"
                :total="total"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
                background
              />
            </div>
          </template>
  
          <!-- 我关注的知识库 -->
          <template v-else>
            <el-skeleton :rows="3" animated v-if="loadingFollowed" />
            
            <!-- 知识库列表 -->
            <div class="kb-grid" v-if="followedKnowledgeBases.length > 0">
              <el-card v-for="kb in followedKnowledgeBases" :key="kb.id" class="kb-card" shadow="hover">
                <div class="kb-content">
                  <!-- 知识库标题和图标 -->
                  <div class="kb-header">
                    <div class="kb-icon">
                      <el-icon size="24"><Folder /></el-icon>
                    </div>
                    <h3 class="kb-name" @click="viewKnowledgeBase(kb)">{{ kb.name }}</h3>
                  </div>
                  
                  <!-- 知识库描述 -->
                  <p class="kb-description">{{ kb.description }}</p>
                  
                  <!-- 知识库统计 -->
                  <div class="kb-stats">
                    <div class="kb-stat">
                      <el-icon><Document /></el-icon>
                      <span>{{ kb.fileCount }} 个文件</span>
                    </div>
                    <div class="kb-stat">
                      <el-icon><View /></el-icon>
                      <span>{{ kb.views }} 次浏览</span>
                    </div>
                    <div class="kb-stat">
                      <el-icon><Star /></el-icon>
                      <span>{{ kb.followers }} 人关注</span>
                    </div>
                  </div>
                  
                  <!-- 创建者信息 -->
                  <div class="kb-creator" v-if="kb.creator">
                    <el-icon><User /></el-icon>
                    <span>创建者: {{ kb.creator.username }}</span>
                  </div>
                  
                  <!-- 知识库操作 -->
                  <div class="kb-actions">
                    <el-button type="primary" size="small" @click="viewKnowledgeBase(kb)">
                      <el-icon class="el-icon--left"><View /></el-icon>查看
                    </el-button>
                    <el-button type="danger" size="small" @click="unfollowKnowledgeBase(kb)">
                      <el-icon class="el-icon--left"><Star /></el-icon>取消关注
                    </el-button>
                  </div>
                </div>
              </el-card>
            </div>
  
            <!-- 空状态展示 -->
            <el-empty 
              v-else-if="!loadingFollowed" 
              description="暂无关注的知识库" 
              :image-size="200"
            >
              <el-button type="primary" @click="router.push('/community')">
                去社区发现知识库
              </el-button>
            </el-empty>
  
            <!-- 分页 -->
            <div class="pagination" v-if="followedKnowledgeBases.length > 0">
              <el-pagination
                v-model:current-page="followedCurrentPage"
                v-model:page-size="followedPageSize"
                :page-sizes="[12, 24, 36, 48]"
                layout="total, sizes, prev, pager, next"
                :total="followedTotal"
                @size-change="handleFollowedSizeChange"
                @current-change="handleFollowedCurrentChange"
                background
              />
            </div>
          </template>
        </el-main>
      </el-container>
      
      <!-- 分享知识库对话框 -->
      <el-dialog
        v-model="shareDialogVisible"
        title="分享知识库"
        width="400px"
      >
        <div class="share-dialog-content">
          <p>将以下链接分享给他人，即可访问该知识库：</p>
          <el-input
            v-model="shareUrl"
            readonly
            :suffix-icon="Check"
            @click="copyShareUrl"
          />
          <p class="share-tip">点击上方链接即可复制</p>
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="shareDialogVisible = false">关闭</el-button>
            <el-button type="primary" @click="copyAndClose">复制并关闭</el-button>
          </span>
        </template>
      </el-dialog>

      <!-- 上传文件对话框 -->
      <el-dialog
        v-model="uploadDialogVisible"
        :title="`上传文件到知识库: ${currentKnowledgeBase.name || ''}`"
        width="550px"
      >
        <el-form label-position="top">
          <el-alert
            type="info"
            description="支持上传txt, pdf, docx, md等文本文件，单个文件大小不超过10MB"
            show-icon
            :closable="false"
            style="margin-bottom: 20px"
          />
          
          <el-form-item label="选择文件">
            <el-upload
              ref="uploadRef"
              class="upload-container"
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :limit="10"
              multiple
              :file-list="uploadFileList"
              drag
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            </el-upload>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="uploadDialogVisible = false">取消</el-button>
            <el-button 
              type="primary" 
              @click="uploadFiles" 
              :disabled="!uploadFileList.length"
              :loading="uploading"
            >
              上传
            </el-button>
          </span>
        </template>
      </el-dialog>

      <!-- 知识库详情对话框 -->
      <el-dialog
        v-model="knowledgeBaseDetailVisible"
        :title="`知识库详情: ${currentKnowledgeBase.name || ''}`"
        width="650px"
      >
        <el-skeleton :rows="6" animated v-if="loadingDetail" />
        
        <div v-else class="kb-detail-container">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="描述">
              {{ currentKnowledgeBase.description || '无描述' }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ currentKnowledgeBase.createdAt }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="currentKnowledgeBase.status === 'approved' ? 'success' : 'warning'">
                {{ currentKnowledgeBase.status === 'approved' ? '已通过审核' : 
                  currentKnowledgeBase.status === 'pending' ? '审核中' : '未通过审核' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
          
          <div class="kb-files">
            <div class="kb-files-header">
              <h4>文件列表</h4>
              <el-button type="primary" size="small" @click="openUploadDialog">
                <el-icon class="el-icon--left"><Plus /></el-icon>上传文件
              </el-button>
            </div>
            
            <div v-if="knowledgeBaseFiles.length === 0" class="empty-files">
              <el-empty description="暂无文件" />
            </div>
            <el-table v-else :data="knowledgeBaseFiles" style="width: 100%">
              <el-table-column prop="filename" label="文件名" />
              <el-table-column label="大小">
                <template #default="scope">
                  {{ Math.round(scope.row.size / 1024) }} KB
                </template>
              </el-table-column>
              <el-table-column prop="upload_time" label="上传时间" />
              <el-table-column label="状态">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 'approved' ? 'success' : 'warning'">
                    {{ scope.row.status === 'approved' ? '已通过审核' : 
                 scope.row.status === 'pending' ? '审核中' : '未通过审核' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button link type="primary" size="small" @click="previewFile(scope.row)">
                    预览
                  </el-button>
                  <el-button link type="danger" size="small" @click="deleteFile(scope.row)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-dialog>

      <!-- 文件预览对话框 -->
      <el-dialog
        v-model="filePreviewVisible"
        :title="`文件预览: ${currentPreviewFile?.filename || ''}`"
        width="700px"
      >
        <el-skeleton :rows="15" animated v-if="previewLoading" />
        
        <div v-else-if="previewContent" class="file-preview">
          <pre>{{ previewContent }}</pre>
        </div>
        
        <div v-else class="empty-preview">
          <el-empty description="无法预览文件内容" />
        </div>
      </el-dialog>

      <!-- 创建知识库对话框 -->
      <el-dialog
        v-model="createKnowledgeDialogVisible"
        title="创建知识库"
        width="50%"
      >
        <el-form :model="newKnowledgeBase" label-width="80px">
          <el-form-item label="名称" required>
            <el-input v-model="newKnowledgeBase.name" placeholder="请输入知识库名称"></el-input>
          </el-form-item>
          <el-form-item label="类型" required>
            <el-select v-model="newKnowledgeBase.type" placeholder="请选择知识库类型">
              <el-option label="文本知识库" value="text"></el-option>
              <el-option label="图片知识库" value="image"></el-option>
            </el-select>
            <div class="el-form-item-description">
              <small v-if="newKnowledgeBase.type === 'text'">文本知识库支持PDF、TXT、DOCX、MD等格式文件</small>
              <small v-else-if="newKnowledgeBase.type === 'image'">图片知识库支持JPG、PNG、GIF等图片格式</small>
            </div>
          </el-form-item>
          <el-form-item label="描述">
            <el-input
              v-model="newKnowledgeBase.description"
              type="textarea"
              :rows="3"
              placeholder="请输入知识库描述"
            ></el-input>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="createKnowledgeDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="createKnowledgeBase" :loading="creating">创建</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { 
    ArrowLeft, 
    Edit, 
    Delete, 
    View, 
    Star, 
    Share, 
    Plus, 
    Document, 
    Folder, 
    Timer,
    Check,
    UploadFilled,
    User
  } from '@element-plus/icons-vue'
  
  const router = useRouter()
  const knowledgeBases = ref([])
  const currentPage = ref(1)
  const pageSize = ref(12)
  const total = ref(0)
  
  // 分享对话框
  const shareDialogVisible = ref(false)
  const shareUrl = ref('')

  // 上传文件对话框
  const uploadDialogVisible = ref(false)
  const uploadFileList = ref([])
  const uploading = ref(false)
  const uploadRef = ref(null)

  // 知识库详情对话框
  const knowledgeBaseDetailVisible = ref(false)
  const currentKnowledgeBase = reactive({})
  const loadingDetail = ref(false)
  const knowledgeBaseFiles = ref([])

  // 文件预览对话框
  const filePreviewVisible = ref(false)
  const currentPreviewFile = ref(null)
  const previewLoading = ref(false)
  const previewContent = ref('')
  
  // 创建知识库对话框
  const createKnowledgeDialogVisible = ref(false);
  const creating = ref(false);
  const newKnowledgeBase = reactive({
    name: '',
    description: '',
    type: 'text' // 默认为文本类型
  });

  // 活动标签页
  const activeTab = ref('created')
  const followedKnowledgeBases = ref([])
  const followedCurrentPage = ref(1)
  const followedPageSize = ref(12)
  const followedTotal = ref(0)
  const loadingFollowed = ref(false)

  // 获取用户知识库列表
  const fetchKnowledgeBases = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        router.push('/login')
        return
      }
  
      // 构建请求参数
      const params = new URLSearchParams({
        page: currentPage.value.toString(),
        size: pageSize.value.toString()
      })
      
      // 发送请求
      const response = await fetch(`/knowledge_base/my-list?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error('获取知识库列表失败')
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        knowledgeBases.value = result.data.items.map(item => ({
          id: item.id,
          name: item.name,
          description: item.description,
          fileCount: item.fileCount,
          views: item.views || 0,
          followers: item.followers || 0,
          lastUpdated: item.lastUpdated
        }))
        total.value = result.data.total || 0
      } else {
        throw new Error(result.message || '获取知识库列表失败')
      }
    } catch (error) {
      console.error('获取知识库列表失败:', error)
      ElMessage.error('获取知识库列表失败，请稍后重试')
      
      // 开发阶段模拟数据可以保留，但生产环境应移除
    }
  }
  
  // 获取关注的知识库列表
  const fetchFollowedKnowledgeBases = async () => {
    try {
      loadingFollowed.value = true
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        router.push('/login')
        return
      }
  
      // 构建请求参数
      const params = new URLSearchParams({
        page: followedCurrentPage.value.toString(),
        size: followedPageSize.value.toString()
      })
      
      // 发送请求
      const response = await fetch(`/user/followed/knowledge-bases?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error('获取关注的知识库列表失败')
      }
      
      const result = await response.json()
      
      if (result.code === 200) {
        followedKnowledgeBases.value = result.data.items.map(item => ({
          id: item.id,
          name: item.name,
          description: item.description,
          fileCount: item.fileCount || 0,
          views: item.views || 0,
          followers: item.followers || 0,
          lastUpdated: item.lastUpdated,
          creator: item.creator
        }))
        followedTotal.value = result.data.total || 0
      } else {
        throw new Error(result.message || '获取关注的知识库列表失败')
      }
    } catch (error) {
      console.error('获取关注的知识库列表失败:', error)
      ElMessage.error('获取关注的知识库列表失败，请稍后重试')
      
      // 开发阶段模拟数据
      followedKnowledgeBases.value = [
        {
          id: 101,
          name: '人工智能入门',
          description: '包含AI基础知识、算法、应用案例等内容',
          fileCount: 25,
          views: 1200,
          followers: 450,
          lastUpdated: '2023-10-15',
          creator: { username: '技术专家A' }
        },
        {
          id: 102,
          name: '机器学习资料库',
          description: '收集了各类机器学习模型、技术文档和实践案例',
          fileCount: 48,
          views: 2800,
          followers: 1200,
          lastUpdated: '2023-11-05',
          creator: { username: '数据科学家B' }
        }
      ]
      followedTotal.value = followedKnowledgeBases.value.length
    } finally {
      loadingFollowed.value = false
    }
  }
  
  // 查看知识库
  const viewKnowledgeBase = (kb) => {
    router.push(`/knowledge-base/${kb.id}`)
  }
  
  // 编辑知识库
  const editKnowledgeBase = (kb) => {
    router.push(`/knowledge-base-editor/${kb.id}`)
  }
  
  // 删除知识库
  const deleteKnowledgeBase = (kb) => {
    ElMessageBox.confirm(
      `确定要删除知识库 "${kb.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        distinguishCancelAndClose: true,
        closeOnClickModal: false
      }
    ).then(async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          ElMessage.error('请先登录')
          router.push('/login')
          return
        }
  
        // 调用后端API删除知识库
        const response = await fetch(`/knowledge_base/delete_knowledgebase/${kb.id}/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (!response.ok) {
          throw new Error('删除知识库失败')
        }
        
        const result = await response.json()
        
        if (result.code === 200) {
          ElMessage.success('知识库删除成功')
          // 重新加载知识库列表
          fetchKnowledgeBases()
        } else {
          throw new Error(result.message || '删除知识库失败')
        }
      } catch (error) {
        console.error('删除知识库失败:', error)
        ElMessage.error('删除失败，请稍后重试')
      }
    }).catch(() => {})
  }
  
  // 分享知识库
  const shareKnowledgeBase = (kb) => {
    shareUrl.value = `${window.location.origin}/knowledge-base/${kb.id}`
    shareDialogVisible.value = true
  }
  
  // 复制分享链接
  const copyShareUrl = () => {
    navigator.clipboard.writeText(shareUrl.value)
      .then(() => {
        ElMessage({
          message: '链接已复制到剪贴板',
          type: 'success',
          duration: 1500
        })
      })
      .catch(() => {
        ElMessage.error('复制失败，请手动复制')
      })
  }
  
  // 复制并关闭对话框
  const copyAndClose = () => {
    copyShareUrl()
    shareDialogVisible.value = false
  }

  // 打开上传文件对话框
  const openUploadDialog = () => {
    uploadDialogVisible.value = true
  }

  // 从列表直接打开上传对话框
  const openUploadDialogForKb = (kb) => {
    // 设置当前知识库
    Object.assign(currentKnowledgeBase, kb);
    
    // 重置上传文件列表
    uploadFileList.value = [];
    
    // 打开上传对话框
    uploadDialogVisible.value = true;
  }

  // 处理文件选择
  const handleFileChange = (file, fileList) => {
    uploadFileList.value = fileList
  }

  // 处理文件移除
  const handleFileRemove = (file, fileList) => {
    uploadFileList.value = fileList
  }

  // 上传文件
  const uploadFiles = async () => {
    try {
      uploading.value = true
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        router.push('/login')
        return
      }

      const formData = new FormData()
      uploadFileList.value.forEach(file => {
        formData.append('files', file.raw)
      })

      const response = await fetch(`/knowledge_base/knowledgebase/${currentKnowledgeBase.id}/upload/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (!response.ok) {
        throw new Error('上传文件失败')
      }

      const result = await response.json()

      ElMessage.success('文件上传成功')
      uploadDialogVisible.value = false
      uploadFileList.value = []
    } catch (error) {
      console.error('上传文件失败:', error)
      ElMessage.error('上传文件失败，请稍后重试')
    } finally {
      uploading.value = false
    }
  }

  // 获取知识库详情
  const fetchKnowledgeBaseDetail = async (id) => {
    try {
      loadingDetail.value = true
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        router.push('/login')
        return
      }

      const response = await fetch(`/knowledge_base/${id}/detail/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('获取知识库详情失败')
      }

      const result = await response.json()

      if (result.code === 200) {
        Object.assign(currentKnowledgeBase, result.data)
        knowledgeBaseFiles.value = result.data.files || []
        knowledgeBaseDetailVisible.value = true
      } else {
        throw new Error(result.message || '获取知识库详情失败')
      }
    } catch (error) {
      console.error('获取知识库详情失败:', error)
      ElMessage.error('获取知识库详情失败，请稍后重试')
    } finally {
      loadingDetail.value = false
    }
  }

  // 预览文件
  const previewFile = async (file) => {
    try {
      previewLoading.value = true
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        router.push('/login')
        return
      }

      const response = await fetch(`/knowledge_base/file/${file.id}/preview/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('预览文件失败')
      }

      const result = await response.json()

      if (result.code === 200) {
        currentPreviewFile.value = file
        previewContent.value = result.data.content || ''
        filePreviewVisible.value = true
      } else {
        throw new Error(result.message || '预览文件失败')
      }
    } catch (error) {
      console.error('预览文件失败:', error)
      ElMessage.error('预览文件失败，请稍后重试')
    } finally {
      previewLoading.value = false
    }
  }

  // 删除文件
  const deleteFile = async (file) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        ElMessage.error('请先登录')
        router.push('/login')
        return
      }

      const response = await fetch(`/knowledge_base/file/${file.id}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('删除文件失败')
      }

      const result = await response.json()

      if (result.code === 200) {
        ElMessage.success('文件删除成功')
        fetchKnowledgeBaseDetail(currentKnowledgeBase.id)
      } else {
        throw new Error(result.message || '删除文件失败')
      }
    } catch (error) {
      console.error('删除文件失败:', error)
      ElMessage.error('删除文件失败，请稍后重试')
    }
  }
  
  // 创建知识库
  const createKnowledgeBase = async () => {
    if (!newKnowledgeBase.name) {
      ElMessage.warning('请输入知识库名称');
      return;
    }
    
    if (!newKnowledgeBase.type) {
      ElMessage.warning('请选择知识库类型');
      return;
    }
    
    try {
      creating.value = true;
      
      // 获取认证 token
      const token = localStorage.getItem('token');
      if (!token) {
        ElMessage.error('请先登录');
        router.push('/login');
        return;
      }
      
      const response = await fetch('/knowledge_base/create_knowledgebase/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: newKnowledgeBase.name,
          description: newKnowledgeBase.description,
          type: newKnowledgeBase.type
        })
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          ElMessage.error('认证失败，请重新登录');
          router.push('/login');
          return;
        }
        throw new Error('创建知识库失败', response);
      }
      
      const result = await response.json();

      newKnowledgeBase.name = '';
      newKnowledgeBase.description = '';
      newKnowledgeBase.type = 'text';
      createKnowledgeDialogVisible.value = false;
        
      // 刷新知识库列表
      await fetchKnowledgeBases();
        
      ElMessage.success('知识库创建成功');
    } catch (error) {
      console.error('创建知识库失败:', error);
      ElMessage.error('创建知识库失败，请稍后重试');
    } finally {
      creating.value = false;
    }
  };

  // 修改空状态展示的按钮点击事件
  const createNewKnowledgeBase = () => {
    createKnowledgeDialogVisible.value = true;
  };

  // 分页处理
  const handleSizeChange = (val) => {
    pageSize.value = val
    fetchKnowledgeBases()
  }
  
  const handleCurrentChange = (val) => {
    currentPage.value = val
    fetchKnowledgeBases()
  }

  // 关注的知识库分页处理
  const handleFollowedSizeChange = (val) => {
    followedPageSize.value = val
    fetchFollowedKnowledgeBases()
  }
  
  const handleFollowedCurrentChange = (val) => {
    followedCurrentPage.value = val
    fetchFollowedKnowledgeBases()
  }
  
  // 标签页切换处理
  watch(() => activeTab.value, (newVal) => {
    if (newVal === 'followed') {
      fetchFollowedKnowledgeBases()
    } else {
      // 留在原页签时不重新加载，避免不必要的请求
      if (knowledgeBases.value.length === 0) {
        fetchKnowledgeBases()
      }
    }
  })
  
  onMounted(() => {
    fetchKnowledgeBases()
    fetchFollowedKnowledgeBases() // 初始加载关注的知识库
  })
  </script>
  
  <style scoped>
  .my-kb-container {
    padding: 24px;
    background-color: #f5f7fa;
    min-height: 100vh;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding: 0;
  }
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .header-left h2 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: #303133;
  }
  
  .kb-tabs {
    margin-bottom: 24px;
  }
  
  .kb-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 24px;
    margin-bottom: 24px;
  }
  
  .kb-card {
    height: 100%;
    transition: all 0.3s ease;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .kb-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
  }
  
  .kb-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .kb-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ebeef5;
  }
  
  .kb-icon {
    width: 48px;
    height: 48px;
    background-color: #ecf5ff;
    color: #409eff;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
  }
  
  .kb-card:hover .kb-icon {
    transform: scale(1.1);
    background-color: #409eff;
    color: white;
  }
  
  .kb-name {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    cursor: pointer;
    transition: color 0.3s ease;
  }
  
  .kb-name:hover {
    color: #409EFF;
  }
  
  .kb-description {
    color: #606266;
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .kb-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-top: 4px;
  }
  
  .kb-stat {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    color: #606266;
    background-color: #f5f7fa;
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.3s ease;
  }
  
  .kb-stat:hover {
    background-color: #ecf5ff;
    color: #409eff;
  }
  
  .kb-update-time {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    color: #909399;
    margin-top: auto;
  }
  
  .kb-actions {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-top: auto;
    padding-top: 16px;
    border-top: 1px solid #ebeef5;
    width: 100%;
  }
  
  .kb-actions .el-button {
    width: 100%;
    justify-content: center;
    margin: 0;
    padding: 8px 15px;
  }
  
  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 32px;
  }
  
  .share-dialog-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .share-tip {
    font-size: 12px;
    color: #909399;
    text-align: center;
    margin: 0;
  }
  
  .kb-detail-container {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }
  
  .kb-files {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .kb-files-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 12px;
    border-bottom: 1px solid #ebeef5;
  }
  
  .kb-files-header h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }
  
  .empty-files {
    text-align: center;
    padding: 32px 0;
  }
  
  .file-preview {
    white-space: pre-wrap;
    word-wrap: break-word;
    background-color: #f5f7fa;
    padding: 24px;
    border-radius: 8px;
    overflow: auto;
    max-height: 500px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
    font-size: 14px;
    line-height: 1.6;
  }
  
  .empty-preview {
    text-align: center;
    padding: 32px 0;
  }
  
  .el-form-item-description {
    color: #909399;
    font-size: 12px;
    margin-top: 4px;
    line-height: 1.4;
  }
  
  /* 上传组件样式优化 */
  .upload-container {
    border: 2px dashed #dcdfe6;
    border-radius: 8px;
    transition: all 0.3s ease;
  }
  
  .upload-container:hover {
    border-color: #409eff;
  }
  
  .el-upload-dragger {
    width: 100%;
    height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
  }
  
  .el-upload-dragger .el-icon--upload {
    font-size: 48px;
    color: #409eff;
  }
  
  .el-upload__text {
    font-size: 16px;
    color: #606266;
  }
  
  .el-upload__text em {
    color: #409eff;
    font-style: normal;
  }
  
  /* 响应式布局 */
  @media screen and (max-width: 768px) {
    .my-kb-container {
      padding: 16px;
    }
    
    .kb-grid {
      grid-template-columns: 1fr;
    }
    
    .kb-actions {
      grid-template-columns: 1fr;
    }
    
    .kb-stats {
      gap: 8px;
    }
    
    .kb-stat {
      font-size: 12px;
      padding: 2px 6px;
    }
  }

.kb-tabs {
  margin-bottom: 20px;
}

.kb-creator {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
  margin-top: 8px;
}

  </style>