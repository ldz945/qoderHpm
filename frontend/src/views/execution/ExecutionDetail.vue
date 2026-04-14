<template>
  <div class="execution-detail">
    <!-- 顶部页头 -->
    <a-page-header
      title="执行详情"
      sub-title="进度填写"
      @back="handleBack"
    >
      <template #extra>
        <a-button @click="handleSendEmail">
          <template #icon><MailOutlined /></template>
          发送邮件
        </a-button>
        <a-button type="primary" @click="handleSave">
          <template #icon><SaveOutlined /></template>
          保存进度
        </a-button>
      </template>
    </a-page-header>

    <!-- 项目基本信息 -->
    <a-card title="项目基本信息" size="small" class="info-card">
      <a-descriptions :column="4">
        <a-descriptions-item label="项目编码">{{ projectInfo.code }}</a-descriptions-item>
        <a-descriptions-item label="项目名称">{{ projectInfo.name }}</a-descriptions-item>
        <a-descriptions-item label="项目经理">{{ projectInfo.manager }}</a-descriptions-item>
        <a-descriptions-item label="项目状态">
          <a-tag :color="getStatusColor(projectInfo.status)">
            {{ getStatusText(projectInfo.status) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="计划开始">{{ projectInfo.planStart }}</a-descriptions-item>
        <a-descriptions-item label="计划结束">{{ projectInfo.planEnd }}</a-descriptions-item>
        <a-descriptions-item label="整体进度">
          <a-progress :percent="projectInfo.overallProgress" size="small" />
        </a-descriptions-item>
        <a-descriptions-item label="预算金额">¥{{ formatMoney(projectInfo.budget) }}</a-descriptions-item>
      </a-descriptions>
    </a-card>

    <!-- 任务列表 -->
    <a-card title="任务进度" :bordered="false" class="task-card">
      <a-table
        :columns="columns"
        :data-source="taskList"
        :loading="loading"
        row-key="id"
        :pagination="false"
        children-column-name="children"
        :default-expand-all-rows="true"
      >
        <template #bodyCell="{ column, record }">
          <!-- 预警颜色 -->
          <template v-if="column.key === 'warning'">
            <a-badge :color="getWarningColor(record)" :text="getWarningText(record)" />
          </template>

          <!-- 进度 - 可编辑 -->
          <template v-if="column.key === 'progress'">
            <div class="progress-cell">
              <a-input-number
                v-model:value="record.progress"
                :min="0"
                :max="100"
                :precision="0"
                style="width: 70px"
                @change="(val) => handleProgressChange(record, val)"
              />
              <a-progress
                :percent="record.progress"
                :status="getProgressStatus(record.progress)"
                size="small"
                style="width: 100px; margin-left: 8px"
              />
            </div>
          </template>

          <!-- 交付物 -->
          <template v-if="column.key === 'deliverable'">
            <a-space>
              <a-button size="small" @click="handleUpload(record)">
                <template #icon><UploadOutlined /></template>
                上传
              </a-button>
              <a-input
                v-model:value="record.deliverablePath"
                placeholder="或输入外部路径"
                size="small"
                style="width: 150px"
              />
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 上传弹窗 -->
    <a-modal
      v-model:open="uploadModalVisible"
      title="上传交付物"
      @ok="handleUploadOk"
      @cancel="handleUploadCancel"
    >
      <a-upload
        v-model:file-list="fileList"
        :action="uploadAction"
        :headers="uploadHeaders"
        @change="handleUploadChange"
      >
        <a-button>
          <template #icon><UploadOutlined /></template>
          选择文件
        </a-button>
      </a-upload>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { SaveOutlined, MailOutlined, UploadOutlined } from '@ant-design/icons-vue'
import { getExecutionDetail, updateTaskProgress } from '@/api/project'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id

// 项目信息
const projectInfo = reactive({
  code: '',
  name: '',
  manager: '',
  status: '',
  planStart: '',
  planEnd: '',
  overallProgress: 0,
  budget: 0
})

// 任务列表
const taskList = ref([])
const loading = ref(false)

// 上传相关
const uploadModalVisible = ref(false)
const currentTask = ref(null)
const fileList = ref([])
const uploadAction = '/api/upload'
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token') || ''}`
}

// 表格列定义
const columns = [
  {
    title: '预警',
    key: 'warning',
    width: 80,
    align: 'center'
  },
  {
    title: '层级编码',
    dataIndex: 'wbsCode',
    key: 'wbsCode',
    width: 120
  },
  {
    title: '任务名称',
    dataIndex: 'name',
    key: 'name',
    width: 200
  },
  {
    title: '阶段',
    dataIndex: 'phase',
    key: 'phase',
    width: 100,
    customRender: ({ text }) => getPhaseText(text)
  },
  {
    title: '负责人',
    dataIndex: 'owner',
    key: 'owner',
    width: 120
  },
  {
    title: '计划开始',
    dataIndex: 'planStart',
    key: 'planStart',
    width: 120
  },
  {
    title: '计划结束',
    dataIndex: 'planEnd',
    key: 'planEnd',
    width: 120
  },
  {
    title: '进度%',
    dataIndex: 'progress',
    key: 'progress',
    width: 200
  },
  {
    title: '交付物',
    key: 'deliverable',
    width: 280
  }
]

// 格式化金额
const formatMoney = (value) => {
  if (!value && value !== 0) return '-'
  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 进度状态
const getProgressStatus = (progress) => {
  if (progress >= 100) return 'success'
  if (progress < 30) return 'exception'
  return 'normal'
}

// 状态颜色映射
const getStatusColor = (status) => {
  const colorMap = {
    not_started: 'default',
    in_progress: 'processing',
    paused: 'warning',
    completed: 'success',
    cancelled: 'error'
  }
  return colorMap[status] || 'default'
}

// 状态文本映射
const getStatusText = (status) => {
  const textMap = {
    not_started: '未开始',
    in_progress: '进行中',
    paused: '已暂停',
    completed: '已完成',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

// 阶段文本
const getPhaseText = (phase) => {
  const textMap = {
    init: '立项',
    design: '设计',
    development: '开发',
    test: '测试',
    delivery: '交付'
  }
  return textMap[phase] || phase
}

// 获取预警颜色
const getWarningColor = (record) => {
  const today = new Date()
  const planEnd = new Date(record.planEnd)
  const planStart = new Date(record.planStart)

  // 已完成的任务显示绿色
  if (record.progress >= 100) return 'green'

  // 计划已结束但进度未完成的显示红色
  if (today > planEnd && record.progress < 100) return 'red'

  // 计划即将结束（7天内）但进度低于80%的显示黄色
  const daysToEnd = Math.ceil((planEnd - today) / (1000 * 60 * 60 * 24))
  if (daysToEnd <= 7 && record.progress < 80) return 'yellow'

  // 计划未开始但已过计划开始时间的显示橙色
  if (today > planStart && record.progress === 0) return 'orange'

  return 'green'
}

// 获取预警文本
const getWarningText = (record) => {
  const color = getWarningColor(record)
  const textMap = {
    green: '正常',
    yellow: '预警',
    orange: '延期',
    red: '严重'
  }
  return textMap[color] || '正常'
}

// 加载数据
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getExecutionDetail(projectId)
    const data = res.data || {}

    // 填充项目信息
    Object.assign(projectInfo, data.projectInfo || {})

    // 填充任务列表
    taskList.value = data.tasks || []
  } catch (error) {
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 进度变化
const handleProgressChange = (record, value) => {
  record.progress = value
  // 自动更新父任务进度（简化处理）
  updateParentProgress(taskList.value)
}

// 更新父任务进度
const updateParentProgress = (list) => {
  for (const item of list) {
    if (item.children && item.children.length > 0) {
      updateParentProgress(item.children)
      const totalProgress = item.children.reduce((sum, child) => sum + (child.progress || 0), 0)
      item.progress = Math.round(totalProgress / item.children.length)
    }
  }
}

// 保存进度
const handleSave = async () => {
  try {
    const progressData = taskList.value.map(task => ({
      id: task.id,
      progress: task.progress,
      deliverablePath: task.deliverablePath
    }))
    await updateTaskProgress(projectId, progressData)
    message.success('进度保存成功')
    fetchData()
  } catch (error) {
    message.error('保存失败')
  }
}

// 发送邮件
const handleSendEmail = () => {
  message.info('邮件发送功能开发中')
}

// 上传
const handleUpload = (record) => {
  currentTask.value = record
  fileList.value = []
  uploadModalVisible.value = true
}

const handleUploadChange = (info) => {
  if (info.file.status === 'done') {
    message.success(`${info.file.name} 上传成功`)
    if (currentTask.value) {
      currentTask.value.deliverablePath = info.file.response?.url || info.file.name
    }
  } else if (info.file.status === 'error') {
    message.error(`${info.file.name} 上传失败`)
  }
}

const handleUploadOk = () => {
  uploadModalVisible.value = false
}

const handleUploadCancel = () => {
  uploadModalVisible.value = false
}

// 返回
const handleBack = () => {
  router.back()
}

onMounted(fetchData)
</script>

<style scoped>
.execution-detail {
  padding: 24px;
}

.info-card {
  margin-top: 16px;
  margin-bottom: 16px;
}

.task-card {
  margin-top: 16px;
}

.progress-cell {
  display: flex;
  align-items: center;
}
</style>
