<template>
  <div class="community-container">
    <h1>社区页面</h1>
    <el-button type="primary" @click="handleLogout">退出登录</el-button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const handleLogout = () => {
  ElMessage.success('退出成功')
  router.push('/login')
}
</script>

<style scoped>
.community-container {
  padding: 20px;
}
</style> 