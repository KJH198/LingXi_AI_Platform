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
            <el-menu-item index="kb_review">知识库审核</el-menu-item>
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
                    placeholder="搜索用户ID"
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
          <el-card class="profile-card">
            <div class="profile-header">
              <div class="avatar-wrapper">
                <el-avatar
                  :size="100"
                  :src="userInfo?.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'"
                />
              </div>
              <div class="basic-info">
                <h2>{{ userInfo?.username }}</h2>
                <p>{{ userInfo?.bio || '这个人很懒，什么都没有留下' }}</p>
              </div>
            </div>
            <el-descriptions :column="1" border>
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
          </el-card>
          
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="userInfoDialogVisible = false">关闭</el-button>
            </span>
          </template>
        </el-dialog>

        <!-- 搜索结果用户信息对话框 -->
        <el-dialog
          v-model="searchResultDialogVisible"
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
              <el-button @click="searchResultDialogVisible = false">关闭</el-button>
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
                    @clear="resetBehaviorSearch"
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
                      <span class="stat-unit">秒</span>
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
              <el-tab-pane label="登录记录" name="login" @click="fetchLoginRecords">
                <div class="login-records">
                  <el-table :data="loginRecords" style="width: 100%" border>
                    <el-table-column prop="user_id" label="用户ID" width="120" />
                    <el-table-column prop="user_name" label="用户名" width="150" />
                    <el-table-column prop="time" label="登录时间" width="180" />
                    <el-table-column prop="ip_address" label="IP地址" width="150" />
                    <el-table-column prop="user_isactive" label="活跃状态">
                      <template #default="scope">
                        <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
                          {{ scope.row.is_active ? '活跃' : '未活跃' }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="user_email" label="邮箱" width="200" />
                    <el-table-column prop="user_phone_number" label="手机号" width="150" />
                    <!-- <el-table-column prop="created_at" label="注册时间" width="180" /> -->
                  </el-table>
                </div>

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
              </el-tab-pane>

              <!-- 操作记录标签页 -->
              <el-tab-pane label="操作记录" name="operation">
                <div class="operation-records">
                  <el-table :data="operationRecords" style="width: 100%" border>
                    <el-table-column prop="user_id" label="用户ID" width="120" />
                    <el-table-column prop="user_name" label="用户名" width="150" />
                    <el-table-column prop="time" label="操作时间" width="180" />
                    <el-table-column prop="action" label="操作类型" width="150">
                      <template #default="scope">
                        <el-tag :type="getOperationTypeTag(scope.row.action)">
                          {{ getOperationTypeText(scope.row.action) }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="target_id" label="操作对象ID" width="120" />
                    <el-table-column prop="target_type" label="操作对象类型" />
                    <el-table-column prop="ip_address" label="IP地址" width="150" />
                    <el-table-column label="操作" width="120">
                      <template #default="scope">
                        <el-button 
                          type="primary" 
                          size="small" 
                          @click="handleViewOperationDetail(scope.row)"
                        >
                          查看
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
                    <el-table-column prop="abnormalType" label="异常类型">
                      <template #default="scope">
                        <el-tag type="danger">
                          {{ getAbnormalTypeText(scope.row.abnormalType) }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="ipAddress" label="IP地址" width="150" />
                    <el-table-column prop="isHandled" label="处理状态" width="100">
                      <template #default="scope">
                        <el-tag :type="scope.row.isHandled ? 'success' : 'warning'">
                          {{ scope.row.isHandled ? '已处理' : '未处理' }}
                        </el-tag>
                      </template>
                    </el-table-column>
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

        <!-- 行为管理搜索结果对话框 -->
        <el-dialog
          v-model="behaviorSearchResultDialogVisible"
          title="行为记录详细信息"
          width="600px"
        >
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用户ID">{{ selectedBehavior?.userId }}</el-descriptions-item>
            <el-descriptions-item label="用户名">{{ selectedBehavior?.username }}</el-descriptions-item>
            <el-descriptions-item label="行为时间">{{ selectedBehavior?.behaviorTime }}</el-descriptions-item>
            <el-descriptions-item label="行为类型">
              <el-tag :type="getBehaviorTypeTag(selectedBehavior?.behaviorType)">
                {{ getBehaviorTypeText(selectedBehavior?.behaviorType) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="selectedBehavior?.status === 'normal' ? 'success' : 'danger'">
                {{ selectedBehavior?.status === 'normal' ? '正常' : '异常' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="IP地址">{{ selectedBehavior?.ipAddress }}</el-descriptions-item>
            <el-descriptions-item label="设备信息">{{ selectedBehavior?.device }}</el-descriptions-item>
            <el-descriptions-item label="行为描述" :span="2">{{ selectedBehavior?.description }}</el-descriptions-item>
          </el-descriptions>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="behaviorSearchResultDialogVisible = false">关闭</el-button>
            </span>
          </template>
        </el-dialog>

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
              <el-table :data="filteredAgentListForTable" style="width: 100%" border>
                <el-table-column prop="agentId" label="智能体ID" width="120" />
                <el-table-column prop="agentName" label="智能体名称" width="150" />
                <el-table-column prop="submitTime" label="提交时间" width="180" />
                <el-table-column label="发布者ID" width="150">
                  <template #default="scope">
                    <el-tag :type="'info'">
                      {{ scope.row.creatorId }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="内容预览">
                  <template #default="scope">
                    <div class="content-preview">
                      <el-tag size="small" :type="getContentTypeTag(scope.row.contentType || 'template')">
                        {{ getContentTypeText(scope.row.contentType || 'template') }}
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
                        @click="viewAgentDetail(scope.row)"
                      >
                        查看详情
                      </el-button>
                      <el-button 
                        type="success" 
                        size="small" 
                        @click="handleReviewAgent(scope.row, 'approve')"
                        v-if="scope.row.status === 'pending'"
                      >
                        通过
                      </el-button>
                      <el-button 
                        type="danger" 
                        size="small" 
                        @click="handleReviewAgent(scope.row, 'reject')"
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

        <!-- 智能体审核搜索结果对话框 -->
        <el-dialog
          v-model="agentSearchResultDialogVisible"
          title="智能体详细信息"
          width="700px"
        >
          <el-descriptions :column="2" border>
            <el-descriptions-item label="智能体ID">{{ selectedAgent?.agentId }}</el-descriptions-item>
            <el-descriptions-item label="智能体名称">{{ selectedAgent?.agentName }}</el-descriptions-item>
            <el-descriptions-item label="提交时间">{{ selectedAgent?.submitTime }}</el-descriptions-item>
            <el-descriptions-item label="功能类型">
              <el-tag :type="getFunctionTypeTag(selectedAgent?.functionType)">
                {{ getFunctionTypeText(selectedAgent?.functionType) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getReviewStatusTag(selectedAgent?.status)">
                {{ getReviewStatusText(selectedAgent?.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="内容类型">
              <el-tag :type="getContentTypeTag(selectedAgent?.contentType)">
                {{ getContentTypeText(selectedAgent?.contentType) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="审核时间">{{ selectedAgent?.reviewTime }}</el-descriptions-item>
            <el-descriptions-item label="审核人">{{ selectedAgent?.reviewer }}</el-descriptions-item>
            <el-descriptions-item label="审核意见" :span="2">{{ selectedAgent?.reviewComment }}</el-descriptions-item>
            <el-descriptions-item label="内容预览" :span="2">
              <div class="content-preview">
                <el-tag size="small" :type="getContentTypeTag(selectedAgent?.contentType)">
                  {{ getContentTypeText(selectedAgent?.contentType) }}
                </el-tag>
                <span class="content-text">{{ selectedAgent?.content }}</span>
              </div>
            </el-descriptions-item>
          </el-descriptions>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="agentSearchResultDialogVisible = false">关闭</el-button>
            </span>
          </template>
        </el-dialog>

        <div v-if="activeMenu === 'kb_review'" class="kb-review"> <!-- 修改 v-if 条件 -->
          <el-card class="review-card"> <!-- 可以复用样式类名 -->
            <template #header>
              <div class="card-header">
                <h3>知识库审核</h3> <!-- 修改标题 -->
                <div class="search-box">
                  <el-input
                    v-model="kbSearchQuery"
                    placeholder="搜索知识库ID/名称"
                    class="search-input"
                    clearable
                    @keyup.enter="handleKbSearch"
                  >
                    <template #append>
                      <el-button @click="handleKbSearch">搜索</el-button>
                    </template>
                  </el-input>
                </div>
              </div>
            </template>

            <!-- 审核统计信息 -->
            <div class="review-stats"> <!-- 可以复用样式类名 -->
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
                      <span class="stat-number">{{ pendingKbs }}</span> <!-- 新的统计变量 -->
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
                      <span class="stat-number">{{ approvedKbs }}</span> <!-- 新的统计变量 -->
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
                      <span class="stat-number">{{ rejectedKbs }}</span> <!-- 新的统计变量 -->
                      <span class="stat-unit">个</span>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>

            <!-- 审核列表 -->
            <div class="review-list"> <!-- 可以复用样式类名 -->
              <el-table :data="filteredKbListForTable" style="width: 100%" border> <!-- 新的表格数据源 -->
                <el-table-column prop="kbId" label="知识库ID" width="120" /> <!-- 修改 prop -->
                <el-table-column prop="kbName" label="知识库名称" width="180" /> <!-- 修改 prop -->
                <el-table-column prop="submitTime" label="提交时间" width="180" />
                <el-table-column label="发布者ID" width="150">
                  <template #default="scope">
                    <el-tag :type="'info'">
                      {{ scope.row.creatorId }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="描述预览"> <!-- 修改标签 -->
                  <template #default="scope">
                    <span class="content-text">{{ scope.row.description }}</span> <!-- 显示 description -->
                  </template>
                </el-table-column>
                <el-table-column label="文件数" width="100">
                    <template #default="scope">
                        {{ scope.row.fileCount }}
                    </template>
                </el-table-column>
                <el-table-column label="状态" width="100">
                  <template #default="scope">
                    <el-tag :type="getReviewStatusTag(scope.row.status)"> <!-- 复用辅助函数 -->
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
                        @click="viewKbDetail(scope.row)"
                      >
                        查看详情
                      </el-button>
                      <el-button 
                        type="success" 
                        size="small" 
                        @click="handleReviewKb(scope.row, 'approved')"
                        v-if="scope.row.status === 'pending'"
                      >
                        通过
                      </el-button>
                      <el-button 
                        type="danger" 
                        size="small" 
                        @click="handleReviewKb(scope.row, 'rejected')"
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
                  :model-value="kbCurrentPage" 
                  @update:model-value="handleKbCurrentChange"
                  :page-size="kbPageSize"
                  @update:page-size="handleKbSizeChange"
                  :page-sizes="[10, 20, 30, 50]"
                  layout="total, sizes, prev, pager, next"
                  :total="totalKbs"
                />
              </div>
            </div>
          </el-card>
        </div>

        <!-- 知识库审核搜索结果对话框 (新增) -->
        <el-dialog
          v-model="kbSearchResultDialogVisible"
          title="知识库详细信息"
          width="700px"
        >
          <!-- selectedKb 是新定义的用于显示知识库详情的变量 -->
          <el-descriptions v-if="selectedKb" :column="2" border>
            <el-descriptions-item label="知识库ID">{{ selectedKb.kbId }}</el-descriptions-item>
            <el-descriptions-item label="知识库名称">{{ selectedKb.kbName }}</el-descriptions-item>
            <el-descriptions-item label="提交时间">{{ selectedKb.submitTime }}</el-descriptions-item>
            <el-descriptions-item label="创建者ID">{{ selectedKb.creatorId }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getReviewStatusTag(selectedKb.status)">
                {{ getReviewStatusText(selectedKb.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="文件数量">{{ selectedKb.fileCount }}</el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">{{ selectedKb.description }}</el-descriptions-item>
            <!-- 根据后端 AdminGetKB 返回的字段添加更多详情 -->
            <el-descriptions-item label="审核意见" :span="2">{{ selectedKb.reviewNotes || '-' }}</el-descriptions-item>
          </el-descriptions>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="kbSearchResultDialogVisible = false">关闭</el-button>
            </span>
          </template>
        </el-dialog>


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
                <el-table-column prop="publish_time" label="发布时间" width="180" />
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
import { ref, reactive, onMounted, watch, computed } from 'vue'
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
const behaviorLogs = ref([])
const totalLogs = ref(0)
const selectedAction = ref('')
const startDate = ref('')
const endDate = ref('')

// 修改智能体审核相关变量
const agentSearchQuery = ref('') 
const allRawAgentReviews = ref([]);
const totalReviews = ref(0);
const pendingReviews = ref(0);
const approvedAgents = ref(0);
const rejectedAgents = ref(0);

// 新增：知识库审核相关变量
const kbSearchQuery = ref('');
const allRawKbReviews = ref([]); // 用于存储从后端获取的原始知识库列表
const totalKbs = ref(0);        // 知识库列表总数
const pendingKbs = ref(0);      // 待审核知识库数量
const approvedKbs = ref(0);     // 已通过知识库数量
const rejectedKbs = ref(0);     // 已拒绝知识库数量
const selectedKb = ref(null);   // 用于知识库详情弹窗
const kbSearchResultDialogVisible = ref(false); // 控制知识库详情弹窗
const kbCurrentPage = ref(1);   // 知识库分页当前页
const kbPageSize = ref(10);     // 知识库分页大小

// 添加公告管理相关变量
const announcements = ref([])
const totalAnnouncements = ref(0)
const announcementDialogVisible = ref(false)
const isEdit = ref(false)
const announcementFormRef = ref(null)
const currentAnnouncement = ref(null)

// 添加用户信息对话框相关变量
const userInfoDialogVisible = ref(false)
const searchResultDialogVisible = ref(false)

// 添加行为管理和智能体审核的搜索结果对话框变量
const behaviorSearchResultDialogVisible = ref(false)
const agentSearchResultDialogVisible = ref(false)
const selectedBehavior = ref(null)
const selectedAgent = ref(null)

// 原始数据
const allLoginRecords = ref([]);
const allOperationRecords = ref([]);
const allAbnormalRecords = ref([]);

// API 请求函数
const api = {
  // 获取用户列表
  async getUserList(params) {
    try {
      const response = await fetch(`/user/adminGetUsers`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      })
      if (!response.ok) throw new Error('获取用户列表失败')
      const data = await response.json()
      return {
        users: data.users,
        total: data.total,
        active_users: data.active_users,
        banned_users: data.banned_users
      }
    } catch (error) {
      ElMessage.error('获取用户列表失败')
      throw error
    }
  },

  // 搜索用户
  async searchUser(userId) {
    try {
      const response = await fetch(`/user/adminGetUsersDetail/${userId}/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      })
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.error || '搜索用户失败')
      }
      return await response.json()
    } catch (error) {
      throw error
    }
  },

  // 封禁用户
  async banUser(userId) {
    try {
      const response = await fetch(`/user/admin/banUser/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({
          user_id: userId,
          reason: banForm.reason,
          type: banForm.type,
          duration: banForm.type === 'permanent' ? null : banForm.duration
        })
      });
      if (!response.ok) throw new Error('封禁用户失败')
      const data = await response.json()
      if (data.success) {
        ElMessage.success('封禁用户成功')
        // 更新用户列表
        await handleUserSearch()
        // 关闭弹窗
        banDialogVisible.value = false
      } else {
        throw new Error(data.message || '封禁用户失败')
      }
    } catch (error) {
      console.error('封禁用户失败:', error)
      ElMessage.error(error.message || '封禁用户失败')
    }
  },

  // 解封用户
  async unbanUser(userId) {
    try {
      const response = await fetch(`/user/admin/unbanUser/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({
          user_id: userId
        })
      })
      if (!response.ok) throw new Error('解封用户失败')
      const data = await response.json()
      if (data.success) {
        ElMessage.success('解封用户成功')
        // 更新用户列表
        await handleUserSearch()
      } else {
        throw new Error(data.message || '解封用户失败')
      }
    } catch (error) {
      console.error('解封用户失败:', error)
      ElMessage.error(error.message || '解封用户失败')
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


// API 请求函数
const behaviorApi = {
  async getBehaviorLogs(params) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const response = await fetch(`/user/admin/behavior_logs/?${queryString}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      if (!response.ok) throw new Error('获取用户行为日志失败');
      return await response.json();
    } catch (error) {
      ElMessage.error('获取用户行为日志失败');
      throw error;
    }
  }
};

// 修改用户列表搜索函数
const handleUserSearch = async () => {
  loading.value = true
  try {
    if (userSearchQuery.value) {
      // 搜索单个用户
      const data = await api.searchUser(userSearchQuery.value)
      if (data.user) {
        // 将用户数据转换为弹窗显示格式
        selectedUser.value = {
          id: data.user.id,
          username: data.user.username,
          registerTime: data.user.registerTime || '-',
          lastLoginTime: data.user.lastLoginTime || '-',
          status: data.user.status || 'normal',
          violationType: data.user.violationType || null,
          ipAddress: data.user.ipAddress || '-',
          device: data.user.device || '-'
        }
        // 显示搜索结果弹窗
        searchResultDialogVisible.value = true
        // 清空搜索框
        userSearchQuery.value = ''
      } else {
        // 用户不存在，显示错误信息
        ElMessage.error('搜索失败，用户不存在')
        userSearchQuery.value = ''
      }
    } else {
      // 获取所有用户列表
      const data = await api.getUserList({})
      userList.value = data.users
      totalUsers.value = data.total
      activeUsers.value = data.active_users
      bannedUsers.value = data.banned_users
    }
  } catch (error) {
    // 处理其他错误
    ElMessage.error('搜索用户失败')
    userSearchQuery.value = ''
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
    await api.banUser(selectedUser.value.id)
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
    await api.unbanUser(user.id)
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
  console.log("==== handleCurrentChange", val)
  handleUserSearch()
}

// 修改行为管理页面的逻辑，点击登录记录时发送请求
const fetchLoginRecords = async () => {
  loading.value = true;
  try {
    const response = await fetch('/user/admin/login_records', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
      },
      body: JSON.stringify({
        page: currentPage.value || 1,
        page_size: pageSize.value || 10
      })
    });
    
    if (!response.ok) throw new Error('获取登录记录失败');
    const data = await response.json();
    
    // 保存所有数据
    allLoginRecords.value = data.records;
    // 初始显示所有数据
    loginRecords.value = [...allLoginRecords.value];
    
    totalRecords.value = data.total;
    todayLogins.value = data.total_login_times;
    avgLoginDuration.value = data.total_online_duration;
    abnormalLogins.value = data.total_unexpected_operation_times;
  } catch (error) {
    console.error('获取登录记录失败:', error);
    ElMessage.error('获取登录记录失败');
  } finally {
    loading.value = false;
  }
};

const fetchAnnouncements = async () => {
  loading.value = true;
  try {
    const response = await fetch('/user/admin/GetAnnouncements', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
      },
    });
    if (!response.ok) throw new Error('获取登录记录失败');
    const data = await response.json();
    return data
  } catch (error) {
    console.error('获取登录记录失败:', error);
    ElMessage.error('获取登录记录失败');
  } finally {
    loading.value = false;
  }
}


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
    system_alert: '系统告警',
    login_ip_change: 'IP变动登录', // 添加新的异常类型映射
    multiple_failures: '多次登录失败',
    unusual_device: '异常设备登录',
    unauthorized_access: '未授权访问',
    content_violation: '内容违规',
  }
  return texts[type] || type
}

// 查看操作详情
// 查看操作详情
const handleViewOperationDetail = (record) => {
  ElMessageBox.alert(
    `用户ID: ${record.user_id}
用户名: ${record.user_name}
操作时间: ${record.time}
操作类型: ${getOperationTypeText(record.action)}
操作对象ID: ${record.target_id || '-'}
操作对象类型: ${record.target_type || '-'}
IP地址: ${record.ip_address || '-'}`,
    '操作详情',
    {
      confirmButtonText: '确定',
      type: 'info'
    }
  )
}

// 查看异常详情
// 查看异常详情
const handleViewAbnormalDetail = (record) => {
  ElMessageBox.alert(
    `用户ID: ${record.userId}
用户名: ${record.username}
发生时间: ${record.abnormalTime}
异常类型: ${getAbnormalTypeText(record.abnormalType)}
IP地址: ${record.ipAddress || '-'}
是否处理: ${record.isHandled ? '已处理' : '未处理'}
处理时间: ${record.handledAt || '-'}
处理说明: ${record.handledNotes || '-'}`,
    '异常详情',
    {
      confirmButtonText: '确定',
      type: 'warning'
    }
  )
}

// 修改行为搜索函数
// Update behavior search to filter lists instead of showing user details
const handleBehaviorSearch = () => {
  const query = behaviorSearchQuery.value.toLowerCase().trim();
  
  if (!query) {
    // 如果搜索框为空，显示所有数据
    resetBehaviorSearch();
    return;
  }
  
  // 根据当前标签页过滤对应的数据
  if (activeBehaviorTab.value === 'login') {
    loginRecords.value = allLoginRecords.value.filter(record => 
      String(record.user_id).includes(query) || 
      record.user_name.toLowerCase().includes(query)
    );
  } else if (activeBehaviorTab.value === 'operation') {
    operationRecords.value = allOperationRecords.value.filter(record => 
      String(record.user_id).includes(query) || 
      record.user_name.toLowerCase().includes(query)
    );
  } else if (activeBehaviorTab.value === 'abnormal') {
    abnormalRecords.value = allAbnormalRecords.value.filter(record => 
      String(record.userId).includes(query) || 
      record.username.toLowerCase().includes(query)
    );
  }
};

// Update tab change behavior to reload data
// 添加标签页切换时重置搜索结果
watch(activeBehaviorTab, (newTab) => {
  // 如果有搜索内容，则应用搜索过滤
  if (behaviorSearchQuery.value) {
    handleBehaviorSearch();
  } else {
    // 否则显示该标签页的所有数据
    if (newTab === 'login') {
      loginRecords.value = [...allLoginRecords.value];
    } else if (newTab === 'operation') {
      operationRecords.value = [...allOperationRecords.value];
    } else if (newTab === 'abnormal') {
      abnormalRecords.value = [...allAbnormalRecords.value];
    }
  }

  if (newTab === 'login' && allLoginRecords.value.length === 0) {
    fetchLoginRecords();
  } else if (newTab === 'operation' && allOperationRecords.value.length === 0) {
    fetchOperationRecords();
  } else if (newTab === 'abnormal' && allAbnormalRecords.value.length === 0) {
    fetchAbnormalBehaviors();
  }
});

// 监听搜索框内容变化
watch(behaviorSearchQuery, (newQuery) => {
  if (!newQuery || newQuery.trim() === '') {
    // 如果搜索框为空，恢复所有数据
    resetBehaviorSearch();
  }
});

// 重置搜索结果的函数
const resetBehaviorSearch = () => {
  // 根据当前活动的标签页恢复对应的数据
  if (activeBehaviorTab.value === 'login') {
    loginRecords.value = [...allLoginRecords.value];
  } else if (activeBehaviorTab.value === 'operation') {
    operationRecords.value = [...allOperationRecords.value];
  } else if (activeBehaviorTab.value === 'abnormal') {
    abnormalRecords.value = [...allAbnormalRecords.value];
  }
};

// 添加菜单选择处理函数
const handleMenuSelect = (index) => {
  activeMenu.value = index;
  // 根据选择的菜单加载相应的数据
  if (index === '1') {
    handleUserSearch();
  } else if (index === '2') {
    fetchLoginRecords(); // 点击行为管理时加载登录记录
  } else if (index === '3') {
    fetchAgentReviews();
  } else if (index === 'kb_review') { // 新增
    fetchKbReviews();
  } else if (index === '4') {
    handleAnnouncementSearch();
  }
};

// 获取操作类型标签样式
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
      const response = await fetch('/user/admin/CreateAnnouncement/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({
          title: data.title,
          content: data.content,
          status: data.status,
        })
      })
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '创建公告失败')
      }
      return await response.json()
    } catch (error) {
      ElMessage.error(error.message || '创建公告失败')
      throw error
    }
  },

  // 更新公告
  async updateAnnouncement(id, data) {
    try {
      const response = await fetch(`/user/admin/EditAnnouncement/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({...data})
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
      const response = await fetch(`/user/admin/DeleteAnnouncement/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
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
    // announcements.value = announcements.value.filter(item => item.id !== announcement.id)
    // totalAnnouncements.value--
    // TODO: 实际API调用
    await announcementApi.deleteAnnouncement(announcement.id)
    handleAnnouncementSearch()
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
      const temp = await announcementApi.updateAnnouncement(currentAnnouncement.value.id, {
        title: announcementForm.title,
        content: announcementForm.content,
        status: announcementForm.status,
        publishTime: new Date().toISOString()
      })
      ElMessage.success('更新成功')
    } else {
      const newAnnouncement = await announcementApi.createAnnouncement({
        title: announcementForm.title,
        content: announcementForm.content,
        status: announcementForm.status,
        publishTime: new Date().toISOString()
      })
      ElMessage.success('发布成功')
    }
    handleAnnouncementSearch()
    announcementDialogVisible.value = false
  } catch (error) {
    console.error('保存公告失败:', error)
    ElMessage.error(error.message || '保存公告失败')
  } finally {
    loading.value = false
  }
}

// 处理公告搜索
const handleAnnouncementSearch = async () => {
  loading.value = true
  let mockAnnouncements = await fetchAnnouncements();
  console.log("==== mockAnnouncements",mockAnnouncements)
  try {
    // 使用模拟数据
    announcements.value = mockAnnouncements.announcements || []
    totalAnnouncements.value = mockAnnouncements.announcements?.length
  } catch (error) {
    console.error('获取公告列表失败:', error)
  } finally {
    loading.value = false
  }
}

const filteredAgentListForTable = computed(() => {
  if (!agentSearchQuery.value) { // agentSearchQuery 是你已有的搜索框 v-model 变量
    return allRawAgentReviews.value; 
  }
  const query = agentSearchQuery.value.toLowerCase().trim();
  if (!query) {
    return allRawAgentReviews.value;
  }
  // allRawAgentReviews.value 里的对象结构应与 fetchAgentReviewsData 中映射的一致
  return allRawAgentReviews.value.filter(agent => {
    const nameMatch = agent.agentName && agent.agentName.toLowerCase().includes(query);
    // creatorId 是你表格中显示的，假设 allRawAgentReviews 中的对象也有 creatorId
    const creatorIdMatch = agent.creatorId && agent.creatorId.toString().toLowerCase().includes(query);
    const agentIdMatch = agent.agentId && agent.agentId.toString().toLowerCase().includes(query);
    return nameMatch || creatorIdMatch || agentIdMatch;
  });
});

watch(filteredAgentListForTable, (newValue) => {
  agentReviews.value = newValue; // agentReviews 是你已有的用于表格的 ref
});

// 修改获取智能体列表的函数
const fetchAgentReviews = async () => {
  loading.value = true;
  try {
    // 1. 获取智能体列表 (来自 /user/admin/agents/list)
    const listResponse = await fetch('/user/admin/agents/list', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
      }
    });
    if (!listResponse.ok) throw new Error('获取智能体列表失败');
    const listData = await listResponse.json();

    // 将获取的原始列表数据存储到 allRawAgentReviews
    allRawAgentReviews.value = listData.agents.map(agent => ({
      agentId: agent.agentID,
      agentName: agent.name,
      submitTime: agent.time,
      content: agent.description, // description 作为内容预览的基础
      contentType: agent.contentTypeFromPublishedAgent || 'template', // 假设 PublishedAgent 有此字段，或用默认值
      creatorId: agent.creatorID,
      status: agent.status, // 这个接口默认返回 pending
      is_OpenSource: agent.is_OpenSource,
      // 以下字段主要用于详情弹窗，如果列表接口不提供，查看详情时会通过 fetchAgentDetail 获取
      functionType: agent.functionTypeFromPublishedAgent || '未知功能', // 假设 PublishedAgent 有此字段
      reviewTime: null, // 初始化
      reviewer: null,   // 初始化
      reviewComment: '',// 初始化
    }));
    totalReviews.value = listData.total || allRawAgentReviews.value.length; // totalReviews 是你已有的

    // 2. 获取统计数据 (来自 /user/admin/agent_rating/)
    const statsResponse = await fetch('/user/admin/agent_rating/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
      }
    });
    if (!statsResponse.ok) throw new Error('获取智能体统计数据失败');
    const statsData = await statsResponse.json();

    // 更新你已有的统计变量
    pendingReviews.value = statsData.pending_count || 0;
    approvedAgents.value = statsData.approved_count || 0;
    rejectedAgents.value = statsData.rejected_count || 0;

  } catch (error) {
    console.error('获取智能体审核数据失败:', error);
    ElMessage.error(error.message || '获取智能体审核数据失败');
    allRawAgentReviews.value = [];
    totalReviews.value = 0;
    pendingReviews.value = 0;
    approvedAgents.value = 0;
    rejectedAgents.value = 0;
  } finally {
    loading.value = false;
  }
};

// 添加获取单个智能体的函数
// 修改获取单个智能体的函数以匹配后端返回的数据结构
const fetchAgentDetail = async (agentId) => {
  loading.value = true;
  try {
    const response = await fetch(`/user/admin/agents/list/${agentId}`, { // API路径正确
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
      }
    });
    if (!response.ok) throw new Error('获取智能体详情失败');
    const data = await response.json(); // 后端返回 { agents: [obj], total: 1, ...}
    
    if (data.agents && data.agents.length > 0) {
      const agentData = data.agents[0]; // 获取数组中的第一个元素
      return { // 映射到 selectedAgent 期望的结构
        agentId: agentData.agentID,
        agentName: agentData.name,
        submitTime: agentData.time,
        // 根据 PublishedAgent 模型和你的需求来映射
        contentType: agentData.contentTypeFromPublishedAgent || 'template', // 占位符
        functionType: agentData.functionTypeFromPublishedAgent || agentData.creatorID, // 你之前用 creatorID 作为 functionType
        status: agentData.status,
        content: agentData.description, // description 作为内容
        is_OpenSource: agentData.is_OpenSource,
        // 后端 PublishedAgent 模型有 review_notes 字段
        reviewTime: agentData.updated_at, // 可以用 updated_at 作为审核时间参考
        reviewer: agentData.review_notes ? '系统/管理员' : '-', // 如果有审核笔记，认为是已审核
        reviewComment: agentData.review_notes || ''
      };
    } else {
      throw new Error('未找到智能体详情');
    }
  } catch (error) {
    console.error('获取智能体详情失败:', error);
    ElMessage.error('获取智能体详情失败');
    throw error;
  } finally {
    loading.value = false;
  }
};

const handleAgentSearch = async () => {
  if (agentSearchQuery.value) {
    // 搜索特定智能体
    loading.value = true;
    try {
      const response = await fetch(`/user/admin/agents/list/${agentSearchQuery.value}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      });
      
      if (!response.ok) throw new Error('搜索智能体失败');
      const data = await response.json();
      
      if (data.agents && data.agents.length > 0) {
        const agentData = data.agents[0];
        selectedAgent.value = {
          agentId: agentData.agentID,
          agentName: agentData.name,
          submitTime: agentData.time,
          content: agentData.description,
          contentType: 'template',
          functionType: agentData.creatorID, // 使用创建者ID作为功能类型显示
          status: agentData.status,
          is_OpenSource: agentData.is_OpenSource
        };
        agentSearchResultDialogVisible.value = true;
      } else {
        ElMessage.warning('未找到相关智能体');
      }
    } catch (error) {
      console.error('搜索智能体失败:', error);
      ElMessage.error('搜索智能体失败');
    } finally {
      loading.value = false;
    }
  } else {
    // 获取所有智能体列表
    fetchAgentReviews();
  }
};

// 修改查看详情函数
const viewAgentDetail = async (agent) => {
  try {
    selectedAgent.value = await fetchAgentDetail(agent.agentId);
    agentSearchResultDialogVisible.value = true;
  } catch (error) {
    ElMessage.error('获取智能体详情失败');
  }
};

const handleReviewAgent = async (agent, decision) => {
  try {
    await ElMessageBox.confirm(
      `确定要${decision === 'approve' ? '通过' : '拒绝'}智能体 "${agent.agentName}" 吗？`,
      '审核操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: decision === 'approve' ? 'success' : 'warning'
      }
    );

    loading.value = true;
    
    const response = await fetch(`/user/admin/changeAgentSataus/${agent.agentId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
      },
      body: JSON.stringify({
        enable: decision === 'approve' // true表示通过，false表示拒绝
      })
    });

    if (!response.ok) throw new Error('审核智能体失败');
    const result = await response.json();
    
    if (result.success) {
      ElMessage.success(`已${decision === 'approve' ? '通过' : '拒绝'}智能体`);
      // 刷新列表
      fetchAgentReviews();
    } else {
      throw new Error(result.message || '审核失败');
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审核智能体失败:', error);
      ElMessage.error(typeof error === 'string' ? error : '审核操作失败');
    }
  } finally {
    loading.value = false;
  }
};



const filteredKbListForTable = computed(() => {
  if (!kbSearchQuery.value) {
    return allRawKbReviews.value; 
  }
  const query = kbSearchQuery.value.toLowerCase().trim();
  if (!query) {
    return allRawKbReviews.value;
  }
  return allRawKbReviews.value.filter(kb => {
    const nameMatch = kb.kbName && kb.kbName.toLowerCase().includes(query);
    const idMatch = kb.kbId && kb.kbId.toString().toLowerCase().includes(query);
    // 还可以根据 creatorId 搜索，如果需要的话
    // const creatorIdMatch = kb.creatorId && kb.creatorId.toString().toLowerCase().includes(query);
    return nameMatch || idMatch;
  });
});

const fetchKbReviews = async () => {
  loading.value = true;
  try {
    // 1. 获取知识库列表 (来自 /user/admin/knowledgebases, 默认获取待审核)
    // 后端 AdminGetKB 视图，不带 kb_id 时返回 status='pending' 的列表
    const listResponse = await fetch('/user/admin/knowledgebases/', { // API 路径
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
      }
    });
    if (!listResponse.ok) throw new Error('获取知识库列表失败');
    const listData = await listResponse.json(); // AdminGetKB 返回 {code, message, data: kb_list}

    if (listData.code === 200 && listData.data) {
      allRawKbReviews.value = listData.data.map(kb => ({
        kbId: kb.id, // 从后端 id 映射
        kbName: kb.name,
        // AdminGetKB 没有直接返回提交时间，可以用创建时间代替或从详情获取
        // 假设 PublishedAgent 的 created_at 对应知识库的提交时间，这里 AdminGetKB 没有直接返回
        // submitTime: kb.created_at || new Date().toLocaleDateString(), // 占位，需要后端确认
        // AdminGetKB 返回 creatorID, fileCount
        creatorId: kb.creatorID,
        fileCount: kb.fileCount,
        description: kb.description || '', // AdminGetKB 返回 description
        status: kb.status || 'pending', // AdminGetKB 应该返回 status
        // 以下为详情弹窗可能需要的
        reviewNotes: kb.review_notes || '', // 假设有审核备注字段
      }));
      // AdminGetKB 似乎不直接返回 total 和各状态count, 需要分别统计或修改后端
      totalKbs.value = allRawKbReviews.value.length; // 临时用列表长度
    } else {
      throw new Error(listData.message || '获取知识库列表数据格式错误');
    }

    // 2. 获取知识库统计数据 (需要后端提供类似 agent_rating 的接口，或者前端自行统计)
    // 假设后端没有专门的知识库统计接口，我们基于获取到的列表（可能不全）进行统计
    // 如果 allRawKbReviews 只包含待审核的，这里的统计就不准
    // 你可能需要一个能获取所有状态知识库并返回统计的接口，或者分别请求不同状态的列表来统计
    // 为简化，暂时基于当前列表（通常是待审核）统计
    let pendingCount = 0;
    let approvedCount = 0;
    let rejectedCount = 0;
    
    // 如果需要准确统计所有状态，需要后端接口支持或者多次请求不同status的列表
    // 示例：假设我们要调用一个能返回所有知识库的接口来做统计
    // const allKbResponse = await fetch('/user/admin/knowledgebases?status=all'); // 假设的接口
    // if (allKbResponse.ok) {
    //   const allKbData = await allKbResponse.json();
    //   if (allKbData.code === 200 && allKbData.data) {
    //     allKbData.data.forEach(kb => {
    //       if (kb.status === 'pending') pendingCount++;
    //       else if (kb.status === 'approved') approvedCount++;
    //       else if (kb.status === 'rejected') rejectedCount++;
    //     });
    //   }
    // }
    //  由于 AdminGetKB 默认只拉取 pending, 所以这里的统计只会是 pending 的。
    //  你需要一个接口能拉取所有状态的KB才能做准确统计，或者 AgentRatingView 那样的接口。
    //  暂时，我们将只显示待审核的数量（如果列表只含待审核）
    //  或者，如果你的 /user/admin/knowledgebases 能够通过参数获取不同状态的列表，可以多次调用来统计。
    //  此处假设 AgentRatingView 的逻辑可以复用，但针对知识库 (这是理想情况，但后端没有这样的接口)
    //  const kbStatsResponse = await fetch('/user/admin/kb_stats_endpoint/'); // 假设的统计接口
    //  if (kbStatsResponse.ok) {
    //      const kbStatsData = await kbStatsResponse.json();
    //      pendingKbs.value = kbStatsData.pending_count || 0;
    //      approvedKbs.value = kbStatsData.approved_count || 0;
    //      rejectedKbs.value = kbStatsData.rejected_count || 0;
    //  } else {
    //      ElMessage.warn('获取知识库统计数据失败，统计可能不准确');
    //      pendingKbs.value = allRawKbReviews.value.filter(kb => kb.status === 'pending').length;
    //      approvedKbs.value = 0; // 无法准确获取
    //      rejectedKbs.value = 0; // 无法准确获取
    //  }
    //  由于 AdminGetKB 默认只返回 status='pending' 的，所以这样统计：
       pendingKbs.value = allRawKbReviews.value.filter(kb => kb.status === 'pending').length;
    //  对于 approved 和 rejected，你需要不同的API调用或后端修改 AdminGetKB
       approvedKbs.value = 0; // 占位 - 需要后端支持
       rejectedKbs.value = 0; // 占位 - 需要后端支持
       ElMessage.info('当前仅显示待审核知识库列表，已通过/已拒绝数量需后端支持完整统计接口。');


  } catch (error) {
    console.error('获取知识库审核数据失败:', error);
    ElMessage.error(error.message || '获取知识库审核数据失败');
    allRawKbReviews.value = [];
    totalKbs.value = 0;
    pendingKbs.value = 0;
    approvedKbs.value = 0;
    rejectedKbs.value = 0;
  } finally {
    loading.value = false;
  }
};

const fetchKbDetail = async (kbId) => {
  loading.value = true;
  try {
    // 后端 AdminGetKB 带 kb_id 的接口
    const response = await fetch(`/user/admin/knowledgebases/${kbId}`, { 
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
      }
    });
    if (!response.ok) throw new Error('获取知识库详情失败');
    const data = await response.json(); // AdminGetKB 带kb_id时，data直接是kb对象或包含它的列表

    // AdminGetKB 带id时，返回的是单个知识库对象（或者只含一个的列表）
    // 假设 data.data 是单个对象，或者 data.data[0]
    let kbDataToProcess = null;
    if (data.code === 200 && data.data) {
        kbDataToProcess = Array.isArray(data.data) ? data.data[0] : data.data;
    }

    if (kbDataToProcess) {
      return {
        kbId: kbDataToProcess.id,
        kbName: kbDataToProcess.name,
        // submitTime: kbDataToProcess.created_at || new Date().toLocaleDateString(), // 占位
        creatorId: kbDataToProcess.creatorID,
        fileCount: kbDataToProcess.fileCount,
        description: kbDataToProcess.description || '',
        status: kbDataToProcess.status || 'pending',
        reviewNotes: kbDataToProcess.review_notes || '', // 假设后端会返回这个
      };
    } else {
      throw new Error('未找到知识库详情或数据格式错误');
    }
  } catch (error) {
    console.error('获取知识库详情失败:', error);
    ElMessage.error('获取知识库详情失败');
    throw error;
  } finally {
    loading.value = false;
  }
};

const handleKbSearch = async () => {
  if (kbSearchQuery.value) {
    loading.value = true;
    try {
      // 调用 fetchKbDetail 获取单个知识库详情并弹窗
      const kbDetail = await fetchKbDetail(kbSearchQuery.value);
      selectedKb.value = kbDetail;
      kbSearchResultDialogVisible.value = true;
    } catch (error) {
      // fetchKbDetail 内部已经有 ElMessage.error
      // ElMessage.warning('未找到相关知识库'); // 可以不重复提示
    } finally {
      loading.value = false;
    }
  } else {
    // 如果搜索框为空，则刷新整个列表
    fetchKbReviews();
  }
};

const viewKbDetail = async (kb) => { // kb 参数是列表中的行对象
  try {
    selectedKb.value = await fetchKbDetail(kb.kbId); // 使用 kb.kbId
    kbSearchResultDialogVisible.value = true;
  } catch (error) {
    // ElMessage.error('获取知识库详情失败'); // fetchKbDetail 内部已处理
  }
};

const handleReviewKb = async (kb, decision) => { // kb 参数是列表行对象, decision 是 'approved' 或 'rejected'
  try {
    await ElMessageBox.confirm(
      `确定要将知识库 "${kb.kbName}" 状态修改为 "${decision === 'approved' ? '已通过' : '已拒绝'}" 吗？`,
      '审核操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: decision === 'approved' ? 'success' : 'warning',
      }
    );

    loading.value = true;
    // 后端接口 /user/admin/changeKBSataus/<int:kb_id>
    // 请求体需要 status: 'approved' 或 'rejected'
    const response = await fetch(`/user/admin/changeKBSataus/${kb.kbId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
      },
      body: JSON.stringify({
        status: decision // 直接传递 'approved' 或 'rejected'
      })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({message: '审核知识库请求失败'}));
        throw new Error(errorData.message || `审核知识库失败: ${response.statusText}`);
    }
    const result = await response.json(); // AdminChangeKBSataus 返回 {code, message, data: None}
    
    if (result.code === 200) { // 假设后端成功时 code 是 200
      ElMessage.success(`知识库状态已更新为 "${decision === 'approved' ? '已通过' : '已拒绝'}"`);
      fetchKbReviews(); // 刷新列表和统计
      if (kbSearchResultDialogVisible.value && selectedKb.value && selectedKb.value.kbId === kb.kbId) {
        kbSearchResultDialogVisible.value = false;
      }
    } else {
      throw new Error(result.message || '审核知识库操作未成功');
    }
  } catch (error) {
    if (error !== 'cancel' && error.message !== 'cancel') {
      console.error('审核知识库操作出错:', error);
      ElMessage.error(error.message || '审核知识库操作失败');
    }
  } finally {
    loading.value = false;
  }
};

const handleKbCurrentChange = (val) => {
  kbCurrentPage.value = val;
  fetchKbReviews(); // 或如果后端支持分页参数，则传递分页参数
};

const handleKbSizeChange = (val) => {
  kbPageSize.value = val;
  kbCurrentPage.value = 1; // 改变每页大小时通常回到第一页
  fetchKbReviews(); // 或如果后端支持分页参数，则传递分页参数
};

// 添加行为类型相关辅助函数
const getBehaviorTypeTag = (type) => {
  const tagTypes = {
    login: 'success',
    operation: 'warning',
    abnormal: 'danger'
  }
  return tagTypes[type] || 'info'
}

const getBehaviorTypeText = (type) => {
  const texts = {
    login: '登录',
    operation: '操作',
    abnormal: '异常'
  }
  return texts[type] || type
}

// 添加获取操作记录的函数
// Fix the operation records function to use proper parameters
const fetchOperationRecords = async () => {
  try {
    const response = await fetch('/user/admin/operation_records', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
      },
      body: JSON.stringify({
        page: currentPage.value || 1,
        page_size: pageSize.value || 10
      })
    });
    
    if (!response.ok) throw new Error('Failed to fetch operation records');
    const data = await response.json();
    
    // 保存所有数据
    allOperationRecords.value = data.records;
    // 初始显示所有数据 
    operationRecords.value = [...allOperationRecords.value];
    
    totalOperationRecords.value = data.total;
  } catch (error) {
    console.error('Error fetching operation records:', error);
    ElMessage.error('获取操作记录失败');
  }
};

// 添加获取异常行为的函数
const fetchAbnormalBehaviors = async () => {
  try {
    const response = await fetch('/user/admin/abnormal_behaviors', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
      }
    });
    
    if (!response.ok) throw new Error('Failed to fetch abnormal behaviors');
    const data = await response.json();
    
    // 映射字段名，使后端返回的字段名与前端组件期望的字段名匹配
    const mappedBehaviors = data.behaviors.map(item => ({
      userId: item.user_id,
      username: item.user_name,
      abnormalTime: item.abnormal_time,
      abnormalType: item.abnormal_type,
      ipAddress: item.ip_address,
      isHandled: item.is_handled,
      handledAt: item.handled_at,
      handledNotes: item.handled_notes
    }));
    
    // 保存所有数据
    allAbnormalRecords.value = mappedBehaviors;
    // 初始显示所有数据
    abnormalRecords.value = [...allAbnormalRecords.value];
    totalAbnormalRecords.value = data.total;
  } catch (error) {
    console.error('Error fetching abnormal behaviors:', error);
    ElMessage.error('获取异常行为失败');
  }
};

// 在mounted钩子中调用这些函数以获取数据
onMounted(() => {
  handleUserSearch();
  if (activeMenu.value === '2') {
    fetchLoginRecords();
    fetchOperationRecords();
    fetchAbnormalBehaviors();
  }
  else if (activeMenu.value === '3') {
    fetchAgentReviews(); // 使用独立的fetch函数加载数据
  }
  else if (activeMenu.value === 'kb_review') { // 如果可能默认是这个tab
    fetchKbReviews();
  }
  else if (activeMenu.value === '4') {
    handleAnnouncementSearch();
  }
});
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
  flex: 1;
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
  flex: 1;      /* 新增，让菜单占满剩余空间 */
  min-width: 0; /* 防止溢出时换行 */
  overflow: hidden; /* 防止溢出 */
  display: flex;    /* 让菜单项一行显示 */
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