<template>
  <a-layout style="min-height: 100vh">
    <!-- 侧边栏 -->
    <a-layout-sider
      v-model:collapsed="collapsed"
      collapsible
      :width="240"
      theme="dark"
    >
      <!-- Logo区域 -->
      <div class="logo">
        <span v-if="!collapsed">HPM项目管理</span>
        <span v-else>HPM</span>
      </div>
      
      <!-- 导航菜单 -->
      <a-menu
        :selectedKeys="selectedKeys"
        :openKeys="openKeys"
        mode="inline"
        theme="dark"
        @click="handleMenuClick"
        @openChange="handleOpenChange"
      >
        <!-- 看板 -->
        <a-menu-item key="dashboard">
          <template #icon>
            <DashboardOutlined />
          </template>
          看板
        </a-menu-item>

        <!-- 主数据管理 -->
        <a-sub-menu key="master-data">
          <template #icon>
            <DatabaseOutlined />
          </template>
          <template #title>主数据管理</template>
          <a-menu-item key="master-data-employees">人员维护</a-menu-item>
          <a-menu-item key="master-data-departments">部门维护</a-menu-item>
          <a-menu-item key="master-data-resources">资源管理</a-menu-item>
          <a-menu-item key="master-data-prices">价格管理</a-menu-item>
        </a-sub-menu>

        <!-- 项目管理 -->
        <a-sub-menu key="project">
          <template #icon>
            <ProjectOutlined />
          </template>
          <template #title>项目管理</template>
          <a-menu-item key="project-list">项目立项</a-menu-item>
        </a-sub-menu>

        <!-- 计划管理 -->
        <a-sub-menu key="plan">
          <template #icon>
            <ScheduleOutlined />
          </template>
          <template #title>计划管理</template>
          <a-menu-item key="plan-list">项目计划</a-menu-item>
          <a-menu-item key="plan-reserve">资源预占</a-menu-item>
          <a-menu-item key="plan-change-logs">变更记录</a-menu-item>
        </a-sub-menu>

        <!-- 项目执行 -->
        <a-menu-item key="execution">
          <template #icon>
            <PlayCircleOutlined />
          </template>
          项目执行
        </a-menu-item>

        <!-- 变更管理 -->
        <a-menu-item key="change">
          <template #icon>
            <SwapOutlined />
          </template>
          变更管理
        </a-menu-item>

        <!-- 验收管理 -->
        <a-menu-item key="acceptance">
          <template #icon>
            <CheckCircleOutlined />
          </template>
          验收管理
        </a-menu-item>

        <!-- 辅助功能 -->
        <a-sub-menu key="auxiliary">
          <template #icon>
            <ToolOutlined />
          </template>
          <template #title>辅助功能</template>
          <a-menu-item key="issue-list">问题/风险</a-menu-item>
          <a-menu-item key="seven-step-list">七步法</a-menu-item>
          <a-menu-item key="document-list">文档管理</a-menu-item>
          <a-menu-item key="vpp-list">VPP管理</a-menu-item>
          <a-menu-item key="scorecard-list">积分卡</a-menu-item>
          <a-menu-item key="meeting-list">会议管理</a-menu-item>
          <a-menu-item key="action-item-list">行动项</a-menu-item>
          <a-menu-item key="expense-list">杂项费用</a-menu-item>
          <a-menu-item key="scope-list">项目范围</a-menu-item>
        </a-sub-menu>

        <!-- 系统管理 -->
        <a-sub-menu key="system" v-if="isSuperAdmin">
          <template #icon>
            <SettingOutlined />
          </template>
          <template #title>系统管理</template>
          <a-menu-item key="system-users">用户管理</a-menu-item>
          <a-menu-item key="system-permissions">权限说明</a-menu-item>
        </a-sub-menu>
      </a-menu>
    </a-layout-sider>

    <!-- 右侧主内容区 -->
    <a-layout>
      <!-- 头部 -->
      <a-layout-header class="header">
        <div class="header-content">
          <a-breadcrumb>
            <a-breadcrumb-item>首页</a-breadcrumb-item>
            <a-breadcrumb-item v-if="route.meta?.title">{{ route.meta.title }}</a-breadcrumb-item>
          </a-breadcrumb>
          <div class="user-info">
            <a-avatar icon="<UserOutlined />" />
            <span class="username">{{ currentUser.name || '用户' }}</span>
            <a-tag color="blue">{{ roleLabel }}</a-tag>
            <a-button type="link" danger size="small" @click="handleLogout">退出</a-button>
          </div>
        </div>
      </a-layout-header>

      <!-- 内容区 -->
      <a-layout-content class="content">
        <div class="content-wrapper">
          <router-view />
        </div>
      </a-layout-content>

      <!-- 底部 -->
      <a-layout-footer class="footer">
        HPM项目管理系统 ©2024
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DashboardOutlined,
  DatabaseOutlined,
  ProjectOutlined,
  ScheduleOutlined,
  PlayCircleOutlined,
  SwapOutlined,
  CheckCircleOutlined,
  ToolOutlined,
  UserOutlined,
  SettingOutlined,
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()

const ROLE_LABELS = {
  SUPER_ADMIN: '超级管理员', MD_ADMIN: '主数据管理员', PMO: 'PMO',
  PROJECT_MANAGER: '项目经理', PLAN_ENGINEER: '计划工程师', EXECUTOR: '执行人', AUDITOR: '审计/只读',
}

const currentUser = computed(() => {
  try { return JSON.parse(localStorage.getItem('hpm_user') || '{}') } catch { return {} }
})
const currentRoles = computed(() => {
  const u = currentUser.value
  if (u.roles && Array.isArray(u.roles)) return u.roles
  return ['SUPER_ADMIN']
})
const roleLabel = computed(() => currentRoles.value.map(r => ROLE_LABELS[r] || r).join(' / '))
const isSuperAdmin = computed(() => currentRoles.value.includes('SUPER_ADMIN'))

const handleLogout = () => {
  localStorage.removeItem('hpm_token')
  localStorage.removeItem('hpm_refresh_token')
  localStorage.removeItem('hpm_user')
  localStorage.removeItem('hpm_role')
  router.push('/login')
}

// 侧边栏折叠状态
const collapsed = ref(false)

// 打开的子菜单
const openKeys = ref([])

// 选中的菜单项
const selectedKeys = computed(() => {
  const path = route.path
  const keyMap = {
    '/dashboard': 'dashboard',
    '/master-data/employees': 'master-data-employees',
    '/master-data/departments': 'master-data-departments',
    '/master-data/resources': 'master-data-resources',
    '/master-data/prices': 'master-data-prices',
    '/project/list': 'project-list',
    '/project/detail': 'project-list',
    '/plan/list': 'plan-list',
    '/plan/edit': 'plan-list',
    '/plan/reserve': 'plan-reserve',
    '/plan/change-logs': 'plan-change-logs',
    '/execution/list': 'execution',
    '/execution/detail': 'execution',
    '/change/list': 'change',
    '/change/form': 'change',
    '/acceptance/list': 'acceptance',
    '/acceptance/form': 'acceptance',
    '/issue/list': 'issue-list',
    '/issue/form': 'issue-list',
    '/seven-step/list': 'seven-step-list',
    '/seven-step/form': 'seven-step-list',
    '/document/list': 'document-list',
    '/vpp/list': 'vpp-list',
    '/vpp/detail': 'vpp-list',
    '/scorecard/list': 'scorecard-list',
    '/scorecard/edit': 'scorecard-list',
    '/meeting/list': 'meeting-list',
    '/meeting/form': 'meeting-list',
    '/action-item/list': 'action-item-list',
    '/expense/list': 'expense-list',
    '/expense/form': 'expense-list',
    '/scope/list': 'scope-list',
    '/scope/form': 'scope-list',
    '/system/users': 'system-users',
    '/system/permissions': 'system-permissions',
  }
  
  // 精确匹配
  if (keyMap[path]) {
    return [keyMap[path]]
  }
  
  // 前缀匹配
  for (const [key, value] of Object.entries(keyMap)) {
    if (path.startsWith(key)) {
      return [value]
    }
  }
  
  return []
})

// 路由变化时更新展开的子菜单
watch(() => route.path, (path) => {
  if (path.startsWith('/master-data')) {
    openKeys.value = ['master-data']
  } else if (path.startsWith('/project')) {
    openKeys.value = ['project']
  } else if (path.startsWith('/plan')) {
    openKeys.value = ['plan']
  } else if (
    path.startsWith('/issue') ||
    path.startsWith('/seven-step') ||
    path.startsWith('/document') ||
    path.startsWith('/vpp') ||
    path.startsWith('/scorecard') ||
    path.startsWith('/meeting') ||
    path.startsWith('/action-item') ||
    path.startsWith('/expense') ||
    path.startsWith('/scope')
  ) {
    openKeys.value = ['auxiliary']
  } else if (path.startsWith('/system')) {
    openKeys.value = ['system']
  }
}, { immediate: true })

// 菜单点击事件
const handleMenuClick = ({ key }) => {
  const routeMap = {
    'dashboard': '/dashboard',
    'master-data-employees': '/master-data/employees',
    'master-data-departments': '/master-data/departments',
    'master-data-resources': '/master-data/resources',
    'master-data-prices': '/master-data/prices',
    'project-list': '/project/list',
    'plan-list': '/plan/list',
    'plan-reserve': '/plan/reserve',
    'plan-change-logs': '/plan/change-logs',
    'execution': '/execution/list',
    'change': '/change/list',
    'acceptance': '/acceptance/list',
    'issue-list': '/issue/list',
    'seven-step-list': '/seven-step/list',
    'document-list': '/document/list',
    'vpp-list': '/vpp/list',
    'scorecard-list': '/scorecard/list',
    'meeting-list': '/meeting/list',
    'action-item-list': '/action-item/list',
    'expense-list': '/expense/list',
    'scope-list': '/scope/list',
    'system-users': '/system/users',
    'system-permissions': '/system/permissions',
  }
  
  const targetPath = routeMap[key]
  if (targetPath) {
    router.push(targetPath)
  }
}

// 子菜单展开变化
const handleOpenChange = (keys) => {
  openKeys.value = keys
}
</script>

<style scoped>
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header {
  background: #fff;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  color: rgba(0, 0, 0, 0.65);
}

.content {
  margin: 24px;
}

.content-wrapper {
  background: #fff;
  padding: 24px;
  min-height: calc(100vh - 64px - 48px - 70px);
  border-radius: 4px;
}

.footer {
  text-align: center;
  color: rgba(0, 0, 0, 0.45);
}
</style>
