<template>
  <div class="dashboard-container">
    <!-- 统计卡片区域 -->
    <a-row :gutter="16">
      <a-col :span="6">
        <a-card class="stat-card" hoverable :loading="loading" @click="goToProjects">
          <a-statistic
            title="我的项目数"
            :value="stats.projects"
            :value-style="{ color: '#1890ff' }"
          >
            <template #prefix>
              <ProjectOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card" hoverable :loading="loading" @click="goToWorkflows">
          <a-statistic
            title="工作流待办数"
            :value="stats.workflows"
            :value-style="{ color: '#52c41a' }"
          >
            <template #prefix>
              <AuditOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card" hoverable :loading="loading" @click="goToIssues">
          <a-statistic
            title="问题/风险待办数"
            :value="stats.issues"
            :value-style="{ color: '#faad14' }"
          >
            <template #prefix>
              <WarningOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card" hoverable :loading="loading" @click="goToActions">
          <a-statistic
            title="行动项数"
            :value="stats.actions"
            :value-style="{ color: '#722ed1' }"
          >
            <template #prefix>
              <CarryOutOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <!-- 报表区域 -->
    <a-card title="报表区域" class="report-card">
      <template #extra>
        <a-button size="small" :loading="loading" @click="fetchStats">刷新</a-button>
      </template>
      <a-empty description="报表功能开发中" />
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ProjectOutlined, AuditOutlined, WarningOutlined, CarryOutOutlined } from '@ant-design/icons-vue'
import { getDashboardSummary } from '@/api/dashboard'
import { message } from 'ant-design-vue'

const router = useRouter()
const stats = ref({ projects: 0, workflows: 0, issues: 0, actions: 0 })
const loading = ref(false)

const fetchStats = async () => {
  loading.value = true
  try {
    const res = await getDashboardSummary()
    stats.value = {
      projects: res.projects ?? res.data?.projects ?? 0,
      workflows: res.workflows ?? res.data?.workflows ?? 0,
      issues: res.issues ?? res.data?.issues ?? 0,
      actions: res.actions ?? res.data?.actions ?? 0,
    }
  } catch {
    message.error('加载看板统计失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchStats)

const goToProjects = () => {
  router.push('/project/list')
}

const goToWorkflows = () => {
  router.push('/plan/list')
}

const goToIssues = () => {
  router.push('/issue/list')
}

const goToActions = () => {
  router.push('/action-item/list')
}
</script>

<style scoped>
.dashboard-container {
  padding: 16px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.report-card {
  margin-top: 24px;
  min-height: 400px;
}
</style>
