<template>
  <div class="my-post-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2>我的帖子</h2>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="router.push('/community')">返回社区</el-button>
        </div>
      </el-header>

      <el-main>
        <div class="post-list">
          <el-card v-for="post in myPosts" :key="post.id" class="post-card">
            <template #header>
              <div class="post-header">
                <div class="post-title">
                  <h3>{{ post.title }}</h3>
                  <span class="time">{{ post.createTime }}</span>
                </div>
                <div class="post-actions">
                  <el-button type="text" @click="editPost(post)">编辑</el-button>
                  <el-button type="text" @click="deletePost(post)">删除</el-button>
                </div>
              </div>
            </template>
            <div class="post-content">
              <p>{{ post.content }}</p>
            </div>
            <div class="post-footer">
              <span class="likes">
                <el-icon><Star /></el-icon>
                {{ post.likes }}
              </span>
              <span class="comments">
                <el-icon><ChatDotRound /></el-icon>
                {{ post.comments }}
              </span>
            </div>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Star, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const myPosts = ref([])

// 获取用户帖子列表
const fetchMyPosts = async () => {
  try {
    // TODO: 调用后端API获取用户帖子列表
    // 这里使用模拟数据
    myPosts.value = [
      {
        id: 1,
        title: '我的第一篇帖子',
        content: '这是帖子的内容...',
        createTime: '2024-04-15 10:00:00',
        likes: 10,
        comments: 5
      },
      {
        id: 2,
        title: '分享一个有趣的AI应用',
        content: '最近发现了一个很棒的AI工具...',
        createTime: '2024-04-14 15:30:00',
        likes: 25,
        comments: 8
      },
      {
        id: 3,
        title: 'AI绘画技巧分享',
        content: '今天想和大家分享一些AI绘画的实用技巧...',
        createTime: '2024-04-13 09:15:00',
        likes: 42,
        comments: 12
      },
      {
        id: 4,
        title: '关于大语言模型的一些思考',
        content: '最近在研究大语言模型的发展趋势...',
        createTime: '2024-04-12 16:45:00',
        likes: 18,
        comments: 7
      },
      {
        id: 5,
        title: 'AI辅助编程体验',
        content: '使用AI辅助编程工具已经有一段时间了...',
        createTime: '2024-04-11 11:20:00',
        likes: 35,
        comments: 9
      }
    ]
  } catch (error) {
    ElMessage.error('获取帖子列表失败')
  }
}

// 编辑帖子
const editPost = (post) => {
  // TODO: 实现编辑帖子功能
  ElMessage.info('编辑帖子功能开发中')
}

// 删除帖子
const deletePost = async (post) => {
  try {
    // TODO: 调用后端API删除帖子
    ElMessage.success('删除成功')
    await fetchMyPosts() // 刷新列表
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchMyPosts()
})
</script>

<style scoped>
.my-post-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.post-list {
  max-width: 800px;
  margin: 0 auto;
}

.post-card {
  margin-bottom: 20px;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-title h3 {
  margin: 0;
  font-size: 18px;
}

.time {
  color: #999;
  font-size: 14px;
  margin-left: 10px;
}

.post-content {
  margin: 15px 0;
  line-height: 1.6;
}

.post-footer {
  display: flex;
  gap: 20px;
  color: #666;
}

.post-footer .el-icon {
  margin-right: 5px;
}
</style>
