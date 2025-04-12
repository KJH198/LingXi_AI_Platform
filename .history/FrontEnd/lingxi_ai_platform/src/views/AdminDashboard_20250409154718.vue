<template>
  <div class="admin-dashboard">
    <!-- 顶部导航栏 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2>灵犀AI平台管理系统</h2>
          <el-menu mode="horizontal" :default-active="activeMenu">
            <el-menu-item index="1">用户管理</el-menu-item>
            <el-menu-item index="2">违规处理</el-menu-item>
            <el-menu-item index="3">行为管理</el-menu-item>
          </el-menu>
        </div>
        <div class="header-right">
          <el-button 
            type="warning" 
            @click="handleLogout"
            class="logout-button"
          >
            退出登录
          </el-button>
        </div>
      </el-header>

      <!-- 主要内容区 -->
                        <el-menu mode="horizontal" :default-active="activeMenu">
                    <el-menu-item index="1" @click="activeMenu = '1'">用户管理</el-menu-item>
                    <el-menu-item index="2" @click="activeMenu = '2'">违规处理</el-menu-item>
                    <el-menu-item index="3" @click="activeMenu = '3'">行为管理</el-menu-item>
                  </el-menu>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, UserFilled, Warning, Timer } from '@element-plus/icons-vue'

const router = useRouter()
const activeMenu = ref('1')
const searchUserId = ref('')
const currentUser = ref(null)
const loading = ref(false)

// 用户管理相关
const userSearchQuery = ref('')
const userList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalUsers = ref(0)

// 添加用户统计相关数据
const activeUsers = ref(0)
const bannedUsers = ref(0)

// 行为管理相关
const behaviorSearchQuery = ref('')
const loginRecords = ref([])
const totalRecords = ref(0)
const todayLogins = ref(0)
const avgLoginDuration = ref(0)
const abnormalLogins = ref(0)

// API 请求函数
const api = {
  // 获取用户列表
  async getUserList(params) {
    try {
      const queryString = new URLSearchParams(params).toString()
      const response = await fetch(`/user/adminGetUsers/${queryString}`)
      if (!response.ok) throw new Error('获取用户列表失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('获取用户列表失败')
      throw error
    }
  },

  // 搜索用户
  async searchUser(userId) {
    try {
      const response = await fetch(`/user/adminGetUsers/${userId}`)
      if (!response.ok) throw new Error('搜索用户失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('搜索用户失败')
      throw error
    }
  },

  // 封禁用户
  async banUser(userId, banData) {
    try {
      const response = await fetch(`/api/admin/users/${userId}/ban`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(banData)
      })
      if (!response.ok) throw new Error('封禁用户失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('封禁用户失败')
      throw error
    }
  },

  // 解封用户
  async unbanUser(userId) {
    try {
      const response = await fetch(`/api/admin/users/${userId}/unban`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error('解封用户失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('解封用户失败')
      throw error
    }
  }
}

const banForm = reactive({
  type: '',
  duration: 1,
  reason: ''
})

const banDialogVisible = ref(false)
const selectedUser = ref(null)

// 模拟用户列表数据
const mockUserList = [
  {
    id: '12345',
    username: 'test_user1',
    registerTime: '2024-03-27 10:00:00',
    violationType: 'medium',
    status: 'normal'
  },
  {
    id: '12346',
    username: 'test_user2',
    registerTime: '2024-03-26 09:15:00',
    violationType: 'severe',
    status: 'banned'
  },
  {
    id: '12347',
    username: 'test_user3',
    registerTime: '2024-03-25 14:30:00',
    violationType: 'light',
    status: 'normal'
  }
]

// 模拟用户数据
const mockUserData = {
  id: '12345',
  username: 'test_user',
  registerTime: '2024-03-27 10:00:00',
  status: 'normal',
  violationType: ''
}

// 模拟登录记录数据
const mockLoginRecords = [
  {
    userId: '12345',
    username: 'test_user1',
    loginTime: '2024-03-27 10:00:00',
    ipAddress: '192.168.1.1',
    device: 'Windows 10 Chrome',
    status: 'success'
  },
  {
    userId: '12346',
    username: 'test_user2',
    loginTime: '2024-03-27 09:30:00',
    ipAddress: '192.168.1.2',
    device: 'MacOS Safari',
    status: 'success'
  },
  {
    userId: '12347',
    username: 'test_user3',
    loginTime: '2024-03-27 08:45:00',
    ipAddress: '192.168.1.3',
    device: 'Android Chrome',
    status: 'abnormal'
  }
]

// API 请求函数
const behaviorApi = {
  // 获取登录记录
  async getLoginRecords(params) {
    try {
      const queryString = new URLSearchParams(params).toString()
      const response = await fetch(`/user/adminGetLoginRecords?${queryString}`)
      if (!response.ok) throw new Error('获取登录记录失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('获取登录记录失败')
      throw error
    }
  },

  // 获取登录统计信息
  async getLoginStats() {
    try {
      const response = await fetch('/user/adminGetLoginStats')
      if (!response.ok) throw new Error('获取登录统计信息失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('获取登录统计信息失败')
      throw error
    }
  }
}

// 修改用户搜索函数
const handleSearch = async () => {
  if (!searchUserId.value) {
    ElMessage.warning('请输入用户ID')
    return
  }
  loading.value = true
  try {
    // 使用模拟数据
    currentUser.value = mockUserData
    // TODO: 实际API调用
    // const data = await api.searchUser(searchUserId.value)
    // currentUser.value = data
  } catch (error) {
    console.error('搜索用户失败:', error)
  } finally {
    loading.value = false
  }
}

// 修改用户列表搜索函数
const handleUserSearch = async () => {
  loading.value = true
  try {
    // 使用模拟数据
    userList.value = mockUserList
    totalUsers.value = mockUserList.length
    activeUsers.value = 2 // 模拟活跃用户数
    bannedUsers.value = 9 // 模拟封禁用户数
    // TODO: 实际API调用
    // const params = {
    //   page: currentPage.value,
    //   pageSize: pageSize.value,
    //   query: userSearchQuery.value
    // }
    // const data = await api.getUserList(params)
    // userList.value = data.users
    // totalUsers.value = data.total
    // activeUsers.value = data.activeUsers
    // bannedUsers.value = data.bannedUsers
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 修改封禁处理函数
const handleBan = async () => {
  if (!banForm.type) {
    ElMessage.warning('请选择封禁类型')
    return
  }
  if (!banForm.reason) {
    ElMessage.warning('请输入封禁原因')
    return
  }
  if (banForm.type !== 'permanent' && (!banForm.duration || banForm.duration < 1)) {
    ElMessage.warning('请输入有效的封禁时长')
    return
  }

  try {
    const durationText = banForm.type === 'permanent' ? '永久' : `${banForm.duration}天`
    await ElMessageBox.confirm(
      `确定要封禁用户 ${selectedUser.value.username} ${durationText} 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value = true
    // 使用模拟数据
    selectedUser.value.status = 'banned'
    selectedUser.value.violationType = banForm.type
    ElMessage.success('封禁成功')
    banDialogVisible.value = false
    // TODO: 实际API调用
    // const banData = {
    //   type: banForm.type,
    //   duration: banForm.type === 'permanent' ? -1 : banForm.duration,
    //   reason: banForm.reason
    // }
    // await api.banUser(selectedUser.value.id, banData)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('封禁用户失败:', error)
    }
  } finally {
    loading.value = false
  }
}

// 修改解封用户函数
const handleUnbanUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要解除用户 ${user.username} 的封禁吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    )
    loading.value = true
    // 使用模拟数据
    user.status = 'normal'
    user.violationType = ''
    ElMessage.success('已解除封禁')
    // TODO: 实际API调用
    // await api.unbanUser(user.id)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('解封用户失败:', error)
    }
  } finally {
    loading.value = false
  }
}

// 修改分页处理函数
const handleSizeChange = (val) => {
  pageSize.value = val
  handleUserSearch()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  handleUserSearch()
}

// 初始化加载用户列表
onMounted(() => {
  handleUserSearch()
})

const handleLogout = () => {
  localStorage.removeItem('adminToken')
  localStorage.removeItem('userRole')
  router.push('/adminLogin')
}

const getViolationTagType = (type) => {
  const types = {
    light: 'warning',
    medium: 'warning',
    severe: 'danger',
    permanent: 'danger'
  }
  return types[type] || 'info'
}

const getViolationTypeText = (type) => {
  const texts = {
    light: '轻度违规',
    medium: '中度违规',
    severe: '严重违规',
    permanent: '永久封禁'
  }
  return texts[type] || '-'
}

// 查看用户详情
const handleViewUser = (user) => {
  ElMessage.info(`查看用户：${user.username}`)
  // TODO: 实现查看用户详情的功能
}

// 添加封禁类型变更处理函数
const handleBanTypeChange = (type) => {
  if (type && type !== 'permanent') {
    const defaultDurations = {
      light: 1,
      medium: 7,
      severe: 30
    }
    banForm.duration = defaultDurations[type]
  }
}

// 获取最大封禁时长
const getMaxDuration = (type) => {
  const maxDurations = {
    light: 3,
    medium: 14,
    severe: 90
  }
  return maxDurations[type] || 1
}

// 修改显示封禁弹窗函数
const showBanDialog = (user) => {
  selectedUser.value = user
  banForm.type = ''
  banForm.duration = 1
  banForm.reason = ''
  banDialogVisible.value = true
}

// 处理行为搜索
const handleBehaviorSearch = async () => {
  loading.value = true
  try {
    // 使用模拟数据
    loginRecords.value = mockLoginRecords
    totalRecords.value = mockLoginRecords.length
    todayLogins.value = 156
    avgLoginDuration.value = 45
    abnormalLogins.value = 12
    // TODO: 实际API调用
    // const params = {
    //   page: currentPage.value,
    //   pageSize: pageSize.value,
    //   query: behaviorSearchQuery.value
    // }
    // const data = await behaviorApi.getLoginRecords(params)
    // loginRecords.value = data.records
    // totalRecords.value = data.total
    // const stats = await behaviorApi.getLoginStats()
    // todayLogins.value = stats.todayLogins
    // avgLoginDuration.value = stats.avgLoginDuration
    // abnormalLogins.value = stats.abnormalLogins
  } catch (error) {
    console.error('获取登录记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 查看登录详情
const handleViewLoginDetail = (record) => {
  ElMessageBox.alert(
    `用户ID: ${record.userId}
用户名: ${record.username}
登录时间: ${record.loginTime}
IP地址: ${record.ipAddress}
设备信息: ${record.device}
登录状态: ${record.status === 'success' ? '正常' : '异常'}`,
    '登录详情',
    {
      confirmButtonText: '确定',
      type: 'info'
    }
  )
}

// 初始化加载登录记录
onMounted(() => {
  if (activeMenu.value === '3') {
    handleBehaviorSearch()
  }
})
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-left h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-management,
.violation-handling,
.behavior-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.card-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-box {
  display: flex;
  gap: 10px;
}

.search-input {
  width: 300px;
}

.user-info {
  margin-bottom: 30px;
}

.ban-actions {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.ban-actions h4 {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 20px;
  color: #303133;
}

.ban-description {
  font-size: 12px;
  color: #909399;
  margin-left: 10px;
}

.user-stats {
  margin-bottom: 20px;
}

.user-stats .el-col:nth-child(1) :deep(.el-card__header) {
  background: #f0f2f5;
}

.user-stats .el-col:nth-child(2) :deep(.el-card__header) {
  background: #73d13d;
}

.user-stats .el-col:nth-child(3) :deep(.el-card__header) {
  background: #ff7875;
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
}

.user-stats .el-col:nth-child(1) .stat-header {
  color: #606266;
}

.user-stats .el-col:nth-child(2) .stat-header,
.user-stats .el-col:nth-child(3) .stat-header {
  color: #fff;
}

.user-stats .el-col:nth-child(1) :deep(.el-icon) {
  color: #606266;
}

.user-stats .el-col:nth-child(2) :deep(.el-icon),
.user-stats .el-col:nth-child(3) :deep(.el-icon) {
  color: #fff;
}

.stat-content {
  display: flex;
  align-items: baseline;
  justify-content: center;
  padding: 20px 0;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-unit {
  margin-left: 4px;
  font-size: 13px;
  color: #909399;
}

:deep(.el-card__header) {
  padding: 12px 20px;
  border-bottom: none;
}

:deep(.el-card__body) {
  padding: 0;
}

.user-list {
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.empty-state {
  min-height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.logout-button {
  padding: 8px 20px;
  border-radius: 4px;
  font-size: 14px;
}

.duration-unit {
  margin-left: 10px;
  color: #666;
  font-size: 14px;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  font-weight: 600;
  color: #303133;
}

:deep(.el-table td) {
  color: #606266;
}

:deep(.el-button) {
  font-size: 14px;
}

:deep(.el-tag) {
  font-size: 13px;
}

.behavior-stats {
  margin-bottom: 20px;
}

.behavior-stats .el-col:nth-child(1) :deep(.el-card__header) {
  background: #f0f2f5;
}

.behavior-stats .el-col:nth-child(2) :deep(.el-card__header) {
  background: #73d13d;
}

.behavior-stats .el-col:nth-child(3) :deep(.el-card__header) {
  background: #ff7875;
}

.behavior-stats .el-col:nth-child(1) .stat-header {
  color: #606266;
}

.behavior-stats .el-col:nth-child(2) .stat-header,
.behavior-stats .el-col:nth-child(3) .stat-header {
  color: #fff;
}

.behavior-stats .el-col:nth-child(1) :deep(.el-icon) {
  color: #606266;
}

.behavior-stats .el-col:nth-child(2) :deep(.el-icon),
.behavior-stats .el-col:nth-child(3) :deep(.el-icon) {
  color: #fff;
}

.login-records {
  margin-top: 20px;
}
</style> 