<template>
  <div class="admin-dashboard">
    <!-- 顶部导航栏 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2>灵犀AI平台管理系统</h2>
          <el-menu 
            mode="horizontal" 
            :default-active="activeMenu"
            @select="handleMenuSelect"
            class="admin-menu"
          >
            <el-menu-item index="1">用户管理</el-menu-item>
            <el-menu-item index="2">行为管理</el-menu-item>
            <el-menu-item index="3">智能体审核</el-menu-item>
            <el-menu-item index="4">公告管理</el-menu-item>
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

        <!-- 用户信息对话框 -->
        <el-dialog
          v-model="userInfoDialogVisible"
          title="用户详细信息"
          width="600px"
        >
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用户ID">{{ selectedUser?.id }}</el-descriptions-item>
            <el-descriptions-item label="用户名">{{ selectedUser?.username }}</el-descriptions-item>
            <el-descriptions-item label="注册时间">{{ selectedUser?.registerTime }}</el-descriptions-item>
            <el-descriptions-item label="最后登录时间">{{ selectedUser?.lastLoginTime || '-' }}</el-descriptions-item>
            <el-descriptions-item label="违规类型">
              <el-tag 
                v-if="selectedUser?.violationType"
                :type="getViolationTagType(selectedUser.violationType)"
                effect="plain"
              >
                {{ getViolationTypeText(selectedUser.violationType) }}
              </el-tag>
              <span v-else>-</span>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="selectedUser?.status === 'normal' ? 'success' : 'danger'">
                {{ selectedUser?.status === 'normal' ? '正常' : '已封禁' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="IP地址">{{ selectedUser?.ipAddress || '-' }}</el-descriptions-item>
            <el-descriptions-item label="设备信息">{{ selectedUser?.device || '-' }}</el-descriptions-item>
          </el-descriptions>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="userInfoDialogVisible = false">关闭</el-button>
            </span>
          </template>
        </el-dialog>

        <!-- 行为管理面板 -->
        <div v-if="activeMenu === '2'" class="behavior-management">
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

            <!-- 行为监控标签页 -->
            <el-tabs v-model="activeBehaviorTab" class="behavior-tabs">
              <!-- 登录记录标签页 -->
              <el-tab-pane label="登录记录" name="login">
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
              </el-tab-pane>

              <!-- 操作记录标签页 -->
              <el-tab-pane label="操作记录" name="operation">
                <div class="operation-records">
                  <el-table :data="operationRecords" style="width: 100%" border>
                    <el-table-column prop="userId" label="用户ID" width="120" />
                    <el-table-column prop="username" label="用户名" width="150" />
                    <el-table-column prop="operationTime" label="操作时间" width="180" />
                    <el-table-column prop="operationType" label="操作类型" width="150">
                      <template #default="scope">
                        <el-tag :type="getOperationTypeTag(scope.row.operationType)">
                          {{ getOperationTypeText(scope.row.operationType) }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="operationContent" label="操作内容" />
                    <el-table-column label="操作" width="120">
                      <template #default="scope">
                        <el-button 
                          type="primary" 
                          size="small" 
                          @click="handleViewOperationDetail(scope.row)"
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
                      :total="totalOperationRecords"
                    />
                  </div>
                </div>
              </el-tab-pane>

              <!-- 异常行为标签页 -->
              <el-tab-pane label="异常行为" name="abnormal">
                <div class="abnormal-records">
                  <el-table :data="abnormalRecords" style="width: 100%" border>
                    <el-table-column prop="userId" label="用户ID" width="120" />
                    <el-table-column prop="username" label="用户名" width="150" />
                    <el-table-column prop="abnormalTime" label="发生时间" width="180" />
                    <el-table-column prop="abnormalType" label="异常类型" width="150">
                      <template #default="scope">
                        <el-tag type="danger">
                          {{ getAbnormalTypeText(scope.row.abnormalType) }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="description" label="异常描述" />
                    <el-table-column label="操作" width="120">
                      <template #default="scope">
                        <el-button 
                          type="primary" 
                          size="small" 
                          @click="handleViewAbnormalDetail(scope.row)"
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
                      :total="totalAbnormalRecords"
                    />
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </div>

        <!-- 智能体审核面板 -->
        <div v-if="activeMenu === '3'" class="agent-review">
          <el-card class="review-card">
            <template #header>
              <div class="card-header">
                <h3>智能体审核</h3>
                <div class="search-box">
                  <el-input
                    v-model="agentSearchQuery"
                    placeholder="搜索智能体ID/名称"
                    class="search-input"
                    clearable
                    @keyup.enter="handleAgentSearch"
                  >
                    <template #append>
                      <el-button @click="handleAgentSearch">搜索</el-button>
                    </template>
                  </el-input>
                </div>
              </div>
            </template>

            <!-- 审核统计信息 -->
            <div class="review-stats">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-card shadow="hover" class="stat-card">
                    <template #header>
                      <div class="stat-header">
                        <el-icon><Document /></el-icon>
                        <span>待审核</span>
                      </div>
                    </template>
                    <div class="stat-content">
                      <span class="stat-number">{{ pendingReviews }}</span>
                      <span class="stat-unit">个</span>
                    </div>
                  </el-card>
                </el-col>
                <el-col :span="8">
                  <el-card shadow="hover" class="stat-card">
                    <template #header>
                      <div class="stat-header">
                        <el-icon><Check /></el-icon>
                        <span>已通过</span>
                      </div>
                    </template>
                    <div class="stat-content">
                      <span class="stat-number">{{ approvedAgents }}</span>
                      <span class="stat-unit">个</span>
                    </div>
                  </el-card>
                </el-col>
                <el-col :span="8">
                  <el-card shadow="hover" class="stat-card">
                    <template #header>
                      <div class="stat-header">
                        <el-icon><Close /></el-icon>
                        <span>已拒绝</span>
                      </div>
                    </template>
                    <div class="stat-content">
                      <span class="stat-number">{{ rejectedAgents }}</span>
                      <span class="stat-unit">个</span>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>

            <!-- 审核列表 -->
            <div class="review-list">
              <el-table :data="agentReviews" style="width: 100%" border>
                <el-table-column prop="agentId" label="智能体ID" width="120" />
                <el-table-column prop="agentName" label="智能体名称" width="150" />
                <el-table-column prop="submitTime" label="提交时间" width="180" />
                <el-table-column prop="functionType" label="功能类型" width="150">
                  <template #default="scope">
                    <el-tag :type="getFunctionTypeTag(scope.row.functionType)">
                      {{ getFunctionTypeText(scope.row.functionType) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="content" label="内容预览">
                  <template #default="scope">
                    <div class="content-preview">
                      <el-tag size="small" :type="getContentTypeTag(scope.row.contentType)">
                        {{ getContentTypeText(scope.row.contentType) }}
                      </el-tag>
                      <span class="content-text">{{ scope.row.content }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="状态" width="100">
                  <template #default="scope">
                    <el-tag :type="getReviewStatusTag(scope.row.status)">
                      {{ getReviewStatusText(scope.row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="280">
                  <template #default="scope">
                    <div class="action-buttons">
                      <el-button 
                        type="primary" 
                        size="small" 
                        @click="handleViewDetail(scope.row)"
                      >
                        详情
                      </el-button>
                      <el-button 
                        type="success" 
                        size="small" 
                        @click="handleApprove(scope.row)"
                        v-if="scope.row.status === 'pending'"
                      >
                        通过
                      </el-button>
                      <el-button 
                        type="danger" 
                        size="small" 
                        @click="handleReject(scope.row)"
                        v-if="scope.row.status === 'pending'"
                      >
                        拒绝
                      </el-button>
                    </div>
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
                  :total="totalReviews"
                />
              </div>
            </div>
          </el-card>
        </div>

        <!-- 公告管理面板 -->
        <div v-if="activeMenu === '4'" class="announcement-management">
          <el-card class="announcement-card">
            <template #header>
              <div class="card-header">
                <h3>公告管理</h3>
                <el-button type="primary" @click="showAnnouncementDialog">发布公告</el-button>
              </div>
            </template>

            <!-- 公告列表 -->
            <div class="announcement-list">
              <el-table :data="announcements" style="width: 100%" border>
                <el-table-column prop="title" label="标题" width="200" />
                <el-table-column prop="content" label="内容" show-overflow-tooltip />
                <el-table-column prop="publishTime" label="发布时间" width="180" />
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="scope">
                    <el-tag :type="scope.row.status === 'published' ? 'success' : 'info'">
                      {{ scope.row.status === 'published' ? '已发布' : '草稿' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                  <template #default="scope">
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="handleEditAnnouncement(scope.row)"
                    >
                      编辑
                    </el-button>
                    <el-button 
                      type="danger" 
                      size="small" 
                      @click="handleDeleteAnnouncement(scope.row)"
                    >
                      删除
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
                  :total="totalAnnouncements"
                />
              </div>
            </div>
          </el-card>
        </div>

        <!-- 发布/编辑公告对话框 -->
        <el-dialog
          v-model="announcementDialogVisible"
          :title="isEdit ? '编辑公告' : '发布公告'"
          width="600px"
        >
          <el-form :model="announcementForm" label-width="80px" :rules="announcementRules" ref="announcementFormRef">
            <el-form-item label="标题" prop="title">
              <el-input v-model="announcementForm.title" placeholder="请输入公告标题" />
            </el-form-item>
            <el-form-item label="内容" prop="content">
              <el-input
                v-model="announcementForm.content"
                type="textarea"
                :rows="6"
                placeholder="请输入公告内容"
              />
            </el-form-item>
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="announcementForm.status">
                <el-radio label="draft">草稿</el-radio>
                <el-radio label="published">立即发布</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="announcementDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="handleSaveAnnouncement">确定</el-button>
            </span>
          </template>
        </el-dialog>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, UserFilled, Warning, Timer, Document, Check, Close } from '@element-plus/icons-vue'

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

// 添加行为监控相关变量
const activeBehaviorTab = ref('login')
const operationRecords = ref([])
const abnormalRecords = ref([])
const totalOperationRecords = ref(0)
const totalAbnormalRecords = ref(0)

// 添加智能体审核相关变量
const agentSearchQuery = ref('')
const pendingReviews = ref(0)
const approvedAgents = ref(0)
const rejectedAgents = ref(0)
const agentReviews = ref([])
const totalReviews = ref(0)

// 添加公告管理相关变量
const announcements = ref([])
const totalAnnouncements = ref(0)
const announcementDialogVisible = ref(false)
const isEdit = ref(false)
const announcementFormRef = ref(null)
const currentAnnouncement = ref(null)

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
  router.push('/admin')
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
  selectedUser.value = user
  userInfoDialogVisible.value = true
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

// 获取操作类型标签样式
const getOperationTypeTag = (type) => {
  const tagTypes = {
    create: 'success',
    update: 'warning',
    delete: 'danger',
    query: 'info'
  }
  return tagTypes[type] || 'info'
}

// 获取操作类型文本
const getOperationTypeText = (type) => {
  const texts = {
    create: '创建',
    update: '更新',
    delete: '删除',
    query: '查询'
  }
  return texts[type] || type
}

// 获取异常类型文本
const getAbnormalTypeText = (type) => {
  const texts = {
    frequent_login: '频繁登录',
    suspicious_ip: '可疑IP',
    unusual_operation: '异常操作',
    system_alert: '系统告警'
  }
  return texts[type] || type
}

// 查看操作详情
const handleViewOperationDetail = (record) => {
  ElMessageBox.alert(
    `用户ID: ${record.userId}
用户名: ${record.username}
操作时间: ${record.operationTime}
操作类型: ${getOperationTypeText(record.operationType)}
操作内容: ${record.operationContent}`,
    '操作详情',
    {
      confirmButtonText: '确定',
      type: 'info'
    }
  )
}

// 查看异常详情
const handleViewAbnormalDetail = (record) => {
  ElMessageBox.alert(
    `用户ID: ${record.userId}
用户名: ${record.username}
发生时间: ${record.abnormalTime}
异常类型: ${getAbnormalTypeText(record.abnormalType)}
异常描述: ${record.description}`,
    '异常详情',
    {
      confirmButtonText: '确定',
      type: 'warning'
    }
  )
}

// 模拟操作记录数据
const mockOperationRecords = [
  {
    userId: '12345',
    username: 'test_user1',
    operationTime: '2024-03-27 10:00:00',
    operationType: 'create',
    operationContent: '创建新项目'
  },
  {
    userId: '12346',
    username: 'test_user2',
    operationTime: '2024-03-27 09:30:00',
    operationType: 'update',
    operationContent: '更新用户信息'
  }
]

// 模拟异常记录数据
const mockAbnormalRecords = [
  {
    userId: '12347',
    username: 'test_user3',
    abnormalTime: '2024-03-27 08:45:00',
    abnormalType: 'frequent_login',
    description: '1小时内登录次数超过10次'
  },
  {
    userId: '12348',
    username: 'test_user4',
    abnormalTime: '2024-03-27 08:30:00',
    abnormalType: 'suspicious_ip',
    description: '使用境外IP地址登录'
  }
]

// 修改行为搜索函数
const handleBehaviorSearch = async () => {
  loading.value = true
  try {
    // 使用模拟数据
    if (activeBehaviorTab.value === 'login') {
      loginRecords.value = mockLoginRecords
      totalRecords.value = mockLoginRecords.length
    } else if (activeBehaviorTab.value === 'operation') {
      operationRecords.value = mockOperationRecords
      totalOperationRecords.value = mockOperationRecords.length
    } else if (activeBehaviorTab.value === 'abnormal') {
      abnormalRecords.value = mockAbnormalRecords
      totalAbnormalRecords.value = mockAbnormalRecords.length
    }
    
    // 更新统计数据
    todayLogins.value = 156
    avgLoginDuration.value = 45
    abnormalLogins.value = 12
  } catch (error) {
    console.error('获取行为记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 添加菜单选择处理函数
const handleMenuSelect = (index) => {
  activeMenu.value = index
  // 根据选择的菜单加载相应的数据
  if (index === '1') {
    handleUserSearch()
  } else if (index === '2') {
    handleBehaviorSearch()
  } else if (index === '3') {
    handleAgentSearch()
  } else if (index === '4') {
    handleAnnouncementSearch()
  }
}

// 添加用户信息对话框相关变量
const userInfoDialogVisible = ref(false)

// API 请求函数
const reviewApi = {
  // 获取审核列表
  async getAgentReviews(params) {
    try {
      const queryString = new URLSearchParams(params).toString()
      const response = await fetch(`/agent/review/reviews?${queryString}`)
      if (!response.ok) throw new Error('获取审核列表失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('获取审核列表失败')
      throw error
    }
  },

  // 获取审核统计信息
  async getReviewStats() {
    try {
      const response = await fetch('/agent/review/stats')
      if (!response.ok) throw new Error('获取审核统计信息失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('获取审核统计信息失败')
      throw error
    }
  },

  // 审核智能体
  async reviewAgent(agentId, reviewData) {
    try {
      const response = await fetch(`/agent/review/reviews/${agentId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(reviewData)
      })
      if (!response.ok) throw new Error('审核智能体失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('审核智能体失败')
      throw error
    }
  }
}

// 模拟审核数据
const mockAgentReviews = [
  {
    agentId: 'A001',
    agentName: '智能助手',
    submitTime: '2024-03-27 10:00:00',
    functionType: 'chat',
    contentType: 'response',
    content: '这是一个智能对话助手的示例回答，展示了其对话能力和知识范围...',
    status: 'pending'
  },
  {
    agentId: 'A002',
    agentName: '数据分析',
    submitTime: '2024-03-27 09:30:00',
    functionType: 'analysis',
    contentType: 'template',
    content: '数据分析模板示例，包含数据清洗、分析和可视化等功能...',
    status: 'approved'
  },
  {
    agentId: 'A003',
    agentName: '自动化工具',
    submitTime: '2024-03-27 09:00:00',
    functionType: 'automation',
    contentType: 'prompt',
    content: '自动化工作流程示例，包含任务调度、数据处理和结果输出...',
    status: 'rejected'
  }
]

// 查看详情
const handleViewDetail = (review) => {
  ElMessageBox.alert(
    `智能体ID: ${review.agentId}
智能体名称: ${review.agentName}
提交时间: ${review.submitTime}
功能类型: ${getFunctionTypeText(review.functionType)}
内容类型: ${getContentTypeText(review.contentType)}
内容详情: ${review.content}
状态: ${getReviewStatusText(review.status)}`,
    '审核详情',
    {
      confirmButtonText: '确定',
      type: 'info'
    }
  )
}

// 审核通过
const handleApprove = async (review) => {
  try {
    await ElMessageBox.confirm(
      `确定要通过智能体 ${review.agentName} 的审核吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    )
    loading.value = true
    // 使用模拟数据
    review.status = 'approved'
    ElMessage.success('审核通过')
    // TODO: 实际API调用
    // await reviewApi.reviewAgent(review.agentId, {
    //   status: 'approved',
    //   comment: '审核通过'
    // })
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审核失败:', error)
    }
  } finally {
    loading.value = false
  }
}

// 审核拒绝
const handleReject = async (review) => {
  try {
    await ElMessageBox.confirm(
      `确定要拒绝智能体 ${review.agentName} 的审核吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    loading.value = true
    // 使用模拟数据
    review.status = 'rejected'
    ElMessage.success('已拒绝')
    // TODO: 实际API调用
    // await reviewApi.reviewAgent(review.agentId, {
    //   status: 'rejected',
    //   comment: '审核不通过'
    // })
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审核失败:', error)
    }
  } finally {
    loading.value = false
  }
}

// 处理智能体搜索
const handleAgentSearch = async () => {
  loading.value = true
  try {
    // 使用模拟数据
    agentReviews.value = mockAgentReviews
    totalReviews.value = mockAgentReviews.length
    
    // 更新统计数据
    pendingReviews.value = 5
    approvedAgents.value = 20
    rejectedAgents.value = 3
    // TODO: 实际API调用
    // const params = {
    //   page: currentPage.value,
    //   pageSize: pageSize.value,
    //   query: agentSearchQuery.value
    // }
    // const data = await reviewApi.getAgentReviews(params)
    // agentReviews.value = data.reviews
    // totalReviews.value = data.total
    // const stats = await reviewApi.getReviewStats()
    // pendingReviews.value = stats.pending
    // approvedAgents.value = stats.approved
    // rejectedAgents.value = stats.rejected
  } catch (error) {
    console.error('获取审核列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取功能类型标签样式
const getFunctionTypeTag = (type) => {
  const tagTypes = {
    chat: 'success',
    analysis: 'warning',
    automation: 'info',
    integration: 'primary'
  }
  return tagTypes[type] || 'info'
}

// 获取功能类型文本
const getFunctionTypeText = (type) => {
  const texts = {
    chat: '对话',
    analysis: '分析',
    automation: '自动化',
    integration: '集成'
  }
  return texts[type] || type
}

// 获取内容类型标签样式
const getContentTypeTag = (type) => {
  const tagTypes = {
    response: 'success',
    template: 'warning',
    prompt: 'info',
    knowledge: 'primary'
  }
  return tagTypes[type] || 'info'
}

// 获取内容类型文本
const getContentTypeText = (type) => {
  const texts = {
    response: '回答',
    template: '模板',
    prompt: '提示词',
    knowledge: '知识库'
  }
  return texts[type] || type
}

// 获取审核状态标签样式
const getReviewStatusTag = (status) => {
  const tagTypes = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return tagTypes[status] || 'info'
}

// 获取审核状态文本
const getReviewStatusText = (status) => {
  const texts = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return texts[status] || status
}

// 公告表单数据
const announcementForm = reactive({
  title: '',
  content: '',
  status: 'draft'
})

// 表单验证规则
const announcementRules = {
  title: [
    { required: true, message: '请输入公告标题', trigger: 'blur' },
    { min: 2, max: 50, message: '标题长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入公告内容', trigger: 'blur' },
    { min: 10, message: '内容至少 10 个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择公告状态', trigger: 'change' }
  ]
}

// API 请求函数
const announcementApi = {
  // 获取公告列表
  async getAnnouncements(params) {
    try {
      const queryString = new URLSearchParams(params).toString()
      const response = await fetch(`/announcement/list?${queryString}`)
      if (!response.ok) throw new Error('获取公告列表失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('获取公告列表失败')
      throw error
    }
  },

  // 创建公告
  async createAnnouncement(data) {
    try {
      const response = await fetch('/announcement/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('创建公告失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('创建公告失败')
      throw error
    }
  },

  // 更新公告
  async updateAnnouncement(id, data) {
    try {
      const response = await fetch(`/announcement/update/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('更新公告失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('更新公告失败')
      throw error
    }
  },

  // 删除公告
  async deleteAnnouncement(id) {
    try {
      const response = await fetch(`/announcement/delete/${id}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('删除公告失败')
      return await response.json()
    } catch (error) {
      ElMessage.error('删除公告失败')
      throw error
    }
  }
}

// 模拟公告数据
const mockAnnouncements = [
  {
    id: 'A001',
    title: '系统维护通知',
    content: '为了提供更好的服务，系统将于本周六凌晨2:00-4:00进行维护升级，期间将暂停服务。',
    publishTime: '2024-03-27 10:00:00',
    status: 'published'
  },
  {
    id: 'A002',
    title: '新功能上线',
    content: '智能体审核功能已上线，管理员可以通过该功能审核用户提交的智能体。',
    publishTime: '2024-03-26 15:30:00',
    status: 'published'
  },
  {
    id: 'A003',
    title: '用户行为规范',
    content: '请各位用户遵守平台使用规范，共同维护良好的社区环境。',
    publishTime: '2024-03-25 09:00:00',
    status: 'draft'
  }
]

// 显示发布公告对话框
const showAnnouncementDialog = () => {
  isEdit.value = false
  currentAnnouncement.value = null
  announcementForm.title = ''
  announcementForm.content = ''
  announcementForm.status = 'draft'
  announcementDialogVisible.value = true
}

// 编辑公告
const handleEditAnnouncement = (announcement) => {
  isEdit.value = true
  currentAnnouncement.value = announcement
  announcementForm.title = announcement.title
  announcementForm.content = announcement.content
  announcementForm.status = announcement.status
  announcementDialogVisible.value = true
}

// 删除公告
const handleDeleteAnnouncement = async (announcement) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除公告"${announcement.title}"吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    loading.value = true
    // 使用模拟数据
    announcements.value = announcements.value.filter(item => item.id !== announcement.id)
    totalAnnouncements.value--
    ElMessage.success('删除成功')
    // TODO: 实际API调用
    // await announcementApi.deleteAnnouncement(announcement.id)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除公告失败:', error)
    }
  } finally {
    loading.value = false
  }
}

// 保存公告
const handleSaveAnnouncement = async () => {
  if (!announcementFormRef.value) return
  
  try {
    await announcementFormRef.value.validate()
    loading.value = true
    
    if (isEdit.value) {
      // 使用模拟数据
      const index = announcements.value.findIndex(item => item.id === currentAnnouncement.value.id)
      if (index !== -1) {
        announcements.value[index] = {
          ...currentAnnouncement.value,
          ...announcementForm,
          publishTime: announcementForm.status === 'published' ? new Date().toLocaleString() : currentAnnouncement.value.publishTime
        }
      }
      ElMessage.success('更新成功')
      // TODO: 实际API调用
      // await announcementApi.updateAnnouncement(currentAnnouncement.value.id, announcementForm)
    } else {
      // 使用模拟数据
      const newAnnouncement = {
        id: `A${String(announcements.value.length + 1).padStart(3, '0')}`,
        ...announcementForm,
        publishTime: announcementForm.status === 'published' ? new Date().toLocaleString() : '-'
      }
      announcements.value.unshift(newAnnouncement)
      totalAnnouncements.value++
      ElMessage.success('发布成功')
      // TODO: 实际API调用
      // await announcementApi.createAnnouncement(announcementForm)
    }
    
    announcementDialogVisible.value = false
  } catch (error) {
    console.error('保存公告失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理公告搜索
const handleAnnouncementSearch = async () => {
  loading.value = true
  try {
    // 使用模拟数据
    announcements.value = mockAnnouncements
    totalAnnouncements.value = mockAnnouncements.length
    // TODO: 实际API调用
    // const params = {
    //   page: currentPage.value,
    //   pageSize: pageSize.value
    // }
    // const data = await announcementApi.getAnnouncements(params)
    // announcements.value = data.announcements
    // totalAnnouncements.value = data.total
  } catch (error) {
    console.error('获取公告列表失败:', error)
  } finally {
    loading.value = false
  }
}
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
.behavior-management,
.agent-review {
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

.admin-menu {
  border-bottom: none;
  margin-left: 20px;
}

.admin-menu :deep(.el-menu-item) {
  height: 60px;
  line-height: 60px;
  font-size: 15px;
  font-weight: 500;
}

.admin-menu :deep(.el-menu-item.is-active) {
  color: #409EFF;
  border-bottom: 2px solid #409EFF;
}

:deep(.el-descriptions) {
  margin: 20px 0;
}

:deep(.el-descriptions__label) {
  width: 120px;
  font-weight: 500;
  color: #606266;
}

:deep(.el-descriptions__content) {
  color: #303133;
}

.behavior-tabs {
  margin-top: 20px;
}

.behavior-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.behavior-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
}

.review-stats {
  margin-bottom: 20px;
}

.review-stats .el-col:nth-child(1) :deep(.el-card__header) {
  background: #f0f2f5;
}

.review-stats .el-col:nth-child(2) :deep(.el-card__header) {
  background: #73d13d;
}

.review-stats .el-col:nth-child(3) :deep(.el-card__header) {
  background: #ff7875;
}

.review-stats .el-col:nth-child(1) .stat-header {
  color: #606266;
}

.review-stats .el-col:nth-child(2) .stat-header,
.review-stats .el-col:nth-child(3) .stat-header {
  color: #fff;
}

.review-stats .el-col:nth-child(1) :deep(.el-icon) {
  color: #606266;
}

.review-stats .el-col:nth-child(2) :deep(.el-icon),
.review-stats .el-col:nth-child(3) :deep(.el-icon) {
  color: #fff;
}

.review-tabs {
  margin-top: 20px;
}

.review-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.review-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
}

.content-preview {
  display: flex;
  align-items: center;
  gap: 8px;
}

.content-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #606266;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-start;
  align-items: center;
}

.action-buttons .el-button {
  min-width: 60px;
  padding: 8px 12px;
}

.announcement-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.announcement-card {
  margin-bottom: 20px;
}

.announcement-list {
  margin-top: 20px;
}
</style> 