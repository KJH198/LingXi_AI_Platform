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
      <el-main>
        <!-- 用户管理面板 -->
        <div v-if="activeMenu === '1'" class="user-management">
          <el-card class="user-card">
            <template #header>
              <div class="card-header">
                <h3>用户管理</h3>
                <div class="search-box">
                  <el-input
                    v-model="userSearchQuery"
                    placeholder="搜索用户ID/用户名"
                    class="search-input"
                    clearable
                    @keyup.enter="handleUserSearch"
                  >
                    <template #append>
                      <el-button @click="handleUserSearch">搜索</el-button>
                    </template>
                  </el-input>
                </div>
              </div>
            </template>

            <!-- 用户统计信息 -->
            <div class="user-stats">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-card shadow="hover" class="stat-card">
                    <template #header>
                      <div class="stat-header">
                        <el-icon><User /></el-icon>
                        <span>总用户数</span>
                      </div>
                    </template>
                    <div class="stat-content">
                      <span class="stat-number">{{ totalUsers }}</span>
                      <span class="stat-unit">人</span>
                    </div>
                  </el-card>
                </el-col>
                <el-col :span="8">
                  <el-card shadow="hover" class="stat-card">
                    <template #header>
                      <div class="stat-header">
                        <el-icon><UserFilled /></el-icon>
                        <span>活跃用户</span>
                      </div>
                    </template>
                    <div class="stat-content">
                      <span class="stat-number">{{ activeUsers }}</span>
                      <span class="stat-unit">人</span>
                    </div>
                  </el-card>
                </el-col>
                <el-col :span="8">
                  <el-card shadow="hover" class="stat-card">
                    <template #header>
                      <div class="stat-header">
                        <el-icon><Warning /></el-icon>
                        <span>封禁用户</span>
                      </div>
                    </template>
                    <div class="stat-content">
                      <span class="stat-number">{{ bannedUsers }}</span>
                      <span class="stat-unit">人</span>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>

            <!-- 用户列表 -->
            <div v-if="userList.length > 0" class="user-list">
              <el-table :data="userList" style="width: 100%" border>
                <el-table-column prop="id" label="用户ID" width="120" />
                <el-table-column prop="username" label="用户名" width="150" />
                <el-table-column prop="registerTime" label="注册时间" width="180" />
                <el-table-column prop="violationType" label="违规类型" width="180">
                  <template #default="scope">
                    <el-tag 
                      v-if="scope.row.violationType"
                      :type="getViolationTagType(scope.row.violationType)"
                      effect="plain"
                    >
                      {{ getViolationTypeText(scope.row.violationType) }}
                    </el-tag>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="scope">
                    <el-tag :type="scope.row.status === 'normal' ? 'success' : 'danger'">
                      {{ scope.row.status === 'normal' ? '正常' : '已封禁' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                  <template #default="scope">
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="handleViewUser(scope.row)"
                    >
                      查看
                    </el-button>
                    <el-button 
                      type="danger" 
                      size="small" 
                      @click="showBanDialog(scope.row)"
                      v-if="scope.row.status === 'normal'"
                    >
                      封禁
                    </el-button>
                    <el-button 
                      type="success" 
                      size="small" 
                      @click="handleUnbanUser(scope.row)"
                      v-if="scope.row.status !== 'normal'"
                    >
                      解封
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 分页 -->
              <div class="pagination">
                <el-pagination
                  :model-value="currentPage"
                  @update:model-value="handleCurrentChange"
                  :page-size="pageSize"
                  @update:page-size="handleSizeChange"
                  :page-sizes="[10, 20, 30, 50]"
                  layout="total, sizes, prev, pager, next"
                  :total="totalUsers"
                />
              </div>
            </div>

            <!-- 无数据展示 -->
            <div v-else class="empty-state">
              <el-empty description="暂无用户数据" />
            </div>
          </el-card>
        </div>

        <!-- 封禁弹窗 -->
        <el-dialog
          v-model="banDialogVisible"
          title="封禁用户"
          width="500px"
        >
          <el-form :model="banForm" label-width="120px">
            <el-form-item label="封禁类型">
              <el-select v-model="banForm.type" placeholder="请选择封禁类型" @change="handleBanTypeChange">
                <el-option label="轻度违规" value="light">
                  <span>轻度违规</span>
                  <span class="ban-description">适用于首次轻微违规</span>
                </el-option>
                <el-option label="中度违规" value="medium">
                  <span>中度违规</span>
                  <span class="ban-description">适用于重复违规或较严重行为</span>
                </el-option>
                <el-option label="严重违规" value="severe">
                  <span>严重违规</span>
                  <span class="ban-description">适用于严重违反平台规则</span>
                </el-option>
                <el-option label="永久封禁" value="permanent">
                  <span>永久封禁</span>
                  <span class="ban-description">适用于极其严重的违规行为</span>
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="封禁时长" v-if="banForm.type && banForm.type !== 'permanent'">
              <el-input-number 
                v-model="banForm.duration" 
                :min="1" 
                :max="getMaxDuration(banForm.type)"
                :step="1"
                placeholder="请输入封禁天数"
              />
              <span class="duration-unit">天</span>
            </el-form-item>
            <el-form-item label="封禁原因">
              <el-input
                v-model="banForm.reason"
                type="textarea"
                :rows="3"
                placeholder="请输入封禁原因"
              />
            </el-form-item>
          </el-form>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="banDialogVisible = false">取消</el-button>
              <el-button type="danger" @click="handleBan">确定封禁</el-button>
            </span>
          </template>
        </el-dialog>

        <!-- 违规处理面板 -->
        <div v-if="activeMenu === '2'" class="violation-handling">
          <el-card class="violation-card">
            <template #header>
              <div class="card-header">
                <h3>违规用户处理</h3>
                <div class="search-box">
                  <el-input
                    v-model="searchUserId"
                    placeholder="请输入用户ID"
                    class="search-input"
                    clearable
                  >
                    <template #append>
                      <el-button @click="handleSearch">搜索</el-button>
                    </template>
                  </el-input>
                </div>
              </div>
            </template>

            <!-- 用户信息展示 -->
            <div v-if="currentUser" class="user-info">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="用户ID">{{ currentUser.id }}</el-descriptions-item>
                <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
                <el-descriptions-item label="注册时间">{{ currentUser.registerTime }}</el-descriptions-item>
                <el-descriptions-item label="当前状态">
                  <el-tag :type="currentUser.status === 'normal' ? 'success' : 'danger'">
                    {{ currentUser.status === 'normal' ? '正常' : '已封禁' }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 封禁操作 -->
            <div v-if="currentUser" class="ban-actions">
              <h4>封禁操作</h4>
              <el-form :model="banForm" label-width="120px">
                <el-form-item label="封禁类型">
                  <el-select v-model="banForm.type" placeholder="请选择封禁类型">
                    <el-option label="轻度违规" value="light">
                      <span>轻度违规（1天）</span>
                      <span class="ban-description">适用于首次轻微违规</span>
                    </el-option>
                    <el-option label="中度违规" value="medium">
                      <span>中度违规（7天）</span>
                      <span class="ban-description">适用于重复违规或较严重行为</span>
                    </el-option>
                    <el-option label="严重违规" value="severe">
                      <span>严重违规（30天）</span>
                      <span class="ban-description">适用于严重违反平台规则</span>
                    </el-option>
                    <el-option label="永久封禁" value="permanent">
                      <span>永久封禁</span>
                      <span class="ban-description">适用于极其严重的违规行为</span>
                    </el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="封禁时长" v-if="banForm.type && banForm.type !== 'permanent'">
                  <el-input-number 
                    v-model="banForm.duration" 
                    :min="1" 
                    :max="getMaxDuration(banForm.type)"
                    :step="1"
                    placeholder="请输入封禁天数"
                  />
                  <span class="duration-unit">天</span>
                </el-form-item>
                <el-form-item label="封禁原因">
                  <el-input
                    v-model="banForm.reason"
                    type="textarea"
                    :rows="3"
                    placeholder="请输入封禁原因"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="danger" @click="handleBan">执行封禁</el-button>
                  <el-button @click="handleUnban" v-if="currentUser.status !== 'normal'">
                    解除封禁
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-card>
        </div>

        <!-- 行为管理面板 -->
        <div v-if="activeMenu === '3'" class="behavior-management">
          <el-card class="behavior-card">
            <template #header>
              <div class="card-header">
                <h3>用户行为管理</h3>
                <div class="search-box">
                  <el-input
                    v-model="behaviorSearchQuery"
                    placeholder="搜索用户ID/用户名"
                    class="search-input"
                    clearable
                    @keyup.enter="handleBehaviorSearch"
                  >
                    <template #append>
                      <el-button @click="handleBehaviorSearch">搜索</el-button>
                    </template>
                  </el-input>
                </div>
              </div>
            </template>

            <!-- 行为统计信息 -->
            <div class="behavior-stats">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-card shadow="hover" class="stat-card">
                    <template #header>
                      <div class="stat-header">
                        <el-icon><User /></el-icon>
                        <span>今日登录</span>
                      </div>
                    </template>
                    <div class="stat-content">
                      <span class="stat-number">{{ todayLogins }}</span>
                      <span class="stat-unit">次</span>
                    </div>
                  </el-card>
                </el-col>
                <el-col :span="8">
                  <el-card shadow="hover" class="stat-card">
                    <template #header>
                      <div class="stat-header">
                        <el-icon><Timer /></el-icon>
                        <span>平均登录时长</span>
                      </div>
                    </template>
                    <div class="stat-content">
                      <span class="stat-number">{{ avgLoginDuration }}</span>
                      <span class="stat-unit">分钟</span>
                    </div>
                  </el-card>
                </el-col>
                <el-col :span="8">
                  <el-card shadow="hover" class="stat-card">
                    <template #header>
                      <div class="stat-header">
                        <el-icon><Warning /></el-icon>
                        <span>异常登录</span>
                      </div>
                    </template>
                    <div class="stat-content">
                      <span class="stat-number">{{ abnormalLogins }}</span>
                      <span class="stat-unit">次</span>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>

            <!-- 登录记录列表 -->
            <div class="login-records">
              <el-table :data="loginRecords" style="width: 100%" border>
                <el-table-column prop="userId" label="用户ID" width="120" />
                <el-table-column prop="username" label="用户名" width="150" />
                <el-table-column prop="loginTime" label="登录时间" width="180" />
                <el-table-column prop="ipAddress" label="IP地址" width="150" />
                <el-table-column prop="device" label="设备信息" width="200" />
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="scope">
                    <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
                      {{ scope.row.status === 'success' ? '正常' : '异常' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="120">
                  <template #default="scope">
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="handleViewLoginDetail(scope.row)"
                    >
                      详情
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 分页 -->
              <div class="pagination">
                <el-pagination
                  :model-value="currentPage"
                  @update:model-value="handleCurrentChange"
                  :page-size="pageSize"
                  @update:page-size="handleSizeChange"
                  :page-sizes="[10, 20, 30, 50]"
                  layout="total, sizes, prev, pager, next"
                  :total="totalRecords"
                />
              </div>
            </div>
          </el-card>
        </div>
      </el-main>
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