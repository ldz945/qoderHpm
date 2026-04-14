<template>
  <div class="acceptance-form">
    <a-page-header
      :title="isEdit ? '编辑验收单' : '新增验收单'"
      @back="handleBack"
    >
      <template #extra>
        <a-button @click="handleCheckVpp">
          <template #icon><FileSearchOutlined /></template>
          VPP核对
        </a-button>
      </template>
    </a-page-header>

    <a-card :bordered="false" class="form-card">
      <a-tabs v-model:activeKey="activeTab">
        <!-- Tab1: 基本信息 -->
        <a-tab-pane key="basic" tab="基本信息">
          <a-form
            :model="formData"
            layout="vertical"
            :rules="rules"
            ref="formRef"
          >
            <a-row :gutter="16">
              <a-col :span="8">
                <a-form-item label="验收单号">
                  <a-input v-model:value="formData.acceptanceNo" disabled placeholder="自动生成" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="项目" name="projectId">
                  <a-select
                    v-model:value="formData.projectId"
                    placeholder="请选择项目"
                    show-search
                    :filter-option="filterOption"
                  >
                    <a-select-option
                      v-for="proj in projectOptions"
                      :key="proj.id"
                      :value="proj.id"
                    >
                      {{ proj.code }} - {{ proj.name }}
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="验收类型" name="acceptanceType">
                  <a-select v-model:value="formData.acceptanceType" placeholder="请选择验收类型">
                    <a-select-option value="milestone">里程碑验收</a-select-option>
                    <a-select-option value="phase">阶段验收</a-select-option>
                    <a-select-option value="final">最终验收</a-select-option>
                    <a-select-option value="deliverable">交付物验收</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="16">
              <a-col :span="24">
                <a-form-item label="备注">
                  <a-textarea
                    v-model:value="formData.remark"
                    :rows="4"
                    placeholder="请输入备注信息"
                  />
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </a-tab-pane>

        <!-- Tab2: 任务交付 -->
        <a-tab-pane key="tasks" tab="任务交付">
          <a-alert
            v-if="!formData.projectId"
            message="请先选择项目"
            type="info"
            show-icon
            style="margin-bottom: 16px"
          />
          <a-table
            v-else
            :columns="taskColumns"
            :data-source="taskList"
            :loading="taskLoading"
            row-key="id"
            :pagination="false"
            children-column-name="children"
            :default-expand-all-rows="true"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'hasDeliverable'">
                <a-checkbox v-model:checked="record.hasDeliverable" />
              </template>
              <template v-if="column.key === 'deliverableName'">
                <a-input
                  v-if="record.hasDeliverable"
                  v-model:value="record.deliverableName"
                  placeholder="请输入交付物名称"
                  size="small"
                />
                <span v-else>-</span>
              </template>
            </template>
          </a-table>
        </a-tab-pane>

        <!-- Tab3: 附件 -->
        <a-tab-pane key="attachments" tab="附件">
          <a-upload
            v-model:file-list="fileList"
            :action="uploadAction"
            :headers="uploadHeaders"
            multiple
            @change="handleUploadChange"
          >
            <a-button>
              <template #icon><UploadOutlined /></template>
              上传验收文件
            </a-button>
          </a-upload>
          <a-table
            :columns="fileColumns"
            :data-source="attachmentList"
            :pagination="false"
            size="small"
            style="margin-top: 16px"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'action'">
                <a-button type="link" danger size="small" @click="handleDeleteFile(record)">
                  删除
                </a-button>
              </template>
            </template>
          </a-table>
        </a-tab-pane>
      </a-tabs>

      <!-- 操作按钮 -->
      <a-divider />
      <a-space>
        <a-button type="primary" @click="handleSave">保存</a-button>
        <a-button @click="handleConfirm">确认</a-button>
        <a-button type="primary" danger @click="handleSubmit">提交审批</a-button>
        <a-button @click="handleBack">关闭</a-button>
      </a-space>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UploadOutlined, FileSearchOutlined } from '@ant-design/icons-vue'
import {
  getAcceptanceDetail,
  createAcceptance,
  updateAcceptance,
  submitAcceptance,
  confirmAcceptance
} from '@/api/acceptance'
import { getProjectList } from '@/api/project'
import { getPlanTasks } from '@/api/plan'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)

const isEdit = ref(false)
const acceptanceId = ref(null)
const activeTab = ref('basic')

// 选项数据
const projectOptions = ref([])
const taskList = ref([])
const taskLoading = ref(false)

// 文件上传
const fileList = ref([])
const attachmentList = ref([])
const uploadAction = '/api/upload'
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token') || ''}`
}

// 表单数据
const formData = reactive({
  acceptanceNo: '',
  projectId: undefined,
  acceptanceType: undefined,
  remark: ''
})

// 表单校验规则
const rules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  acceptanceType: [{ required: true, message: '请选择验收类型', trigger: 'change' }]
}

// 任务表格列
const taskColumns = [
  { title: '层级编码', dataIndex: 'wbsCode', key: 'wbsCode', width: 120 },
  { title: '任务名称', dataIndex: 'name', key: 'name', width: 250 },
  { title: '阶段', dataIndex: 'phase', key: 'phase', width: 100, customRender: ({ text }) => getPhaseText(text) },
  { title: '负责人', dataIndex: 'owner', key: 'owner', width: 120 },
  { title: '计划开始', dataIndex: 'planStart', key: 'planStart', width: 120 },
  { title: '计划结束', dataIndex: 'planEnd', key: 'planEnd', width: 120 },
  { title: '进度%', dataIndex: 'progress', key: 'progress', width: 80 },
  { title: '需交付', dataIndex: 'hasDeliverable', key: 'hasDeliverable', width: 80, align: 'center' },
  { title: '交付物名称', dataIndex: 'deliverableName', key: 'deliverableName', width: 200 }
]

// 附件表格列
const fileColumns = [
  { title: '文件名', dataIndex: 'name', key: 'name' },
  { title: '大小', dataIndex: 'size', key: 'size', width: 120 },
  { title: '上传时间', dataIndex: 'uploadTime', key: 'uploadTime', width: 160 },
  { title: '操作', key: 'action', width: 100 }
]

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

// 加载项目选项
const fetchProjects = async () => {
  try {
    const res = await getProjectList({ pageSize: 1000 })
    projectOptions.value = res.data?.list || []
  } catch (error) {
    console.error('加载项目失败', error)
  }
}

// 加载任务列表
const fetchTasks = async (projectId) => {
  if (!projectId) {
    taskList.value = []
    return
  }
  taskLoading.value = true
  try {
    const res = await getPlanTasks(projectId)
    taskList.value = (res.data || []).map(task => ({
      ...task,
      hasDeliverable: task.hasDeliverable || false,
      deliverableName: task.deliverableName || ''
    }))
  } catch (error) {
    message.error('加载任务失败')
  } finally {
    taskLoading.value = false
  }
}

// 加载验收单详情
const fetchDetail = async (id) => {
  try {
    const res = await getAcceptanceDetail(id)
    const data = res.data || {}
    Object.assign(formData, data)
    if (data.projectId) {
      fetchTasks(data.projectId)
    }
    if (data.attachments) {
      attachmentList.value = data.attachments
    }
  } catch (error) {
    message.error('加载验收单详情失败')
  }
}

// 监听项目变化，加载任务
watch(() => formData.projectId, (newVal) => {
  if (newVal) {
    fetchTasks(newVal)
  } else {
    taskList.value = []
  }
})

// 保存
const handleSave = async () => {
  try {
    await formRef.value.validate()
    const data = {
      ...formData,
      tasks: taskList.value.filter(t => t.hasDeliverable).map(t => ({
        taskId: t.id,
        deliverableName: t.deliverableName
      })),
      attachments: attachmentList.value
    }
    if (isEdit.value) {
      await updateAcceptance(acceptanceId.value, data)
    } else {
      await createAcceptance(data)
    }
    message.success('保存成功')
  } catch (error) {
    if (error.errorFields) {
      message.error('请填写必填项')
    } else {
      message.error('保存失败')
    }
  }
}

// 确认
const handleConfirm = async () => {
  try {
    if (!isEdit.value) {
      message.warning('请先保存验收单')
      return
    }
    await confirmAcceptance(acceptanceId.value)
    message.success('确认成功')
  } catch (error) {
    message.error('确认失败')
  }
}

// 提交审批
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    if (!isEdit.value) {
      const res = await createAcceptance({
        ...formData,
        tasks: taskList.value.filter(t => t.hasDeliverable).map(t => ({
          taskId: t.id,
          deliverableName: t.deliverableName
        })),
        attachments: attachmentList.value
      })
      await submitAcceptance(res.data?.id)
    } else {
      await submitAcceptance(acceptanceId.value)
    }
    message.success('提交审批成功')
    router.back()
  } catch (error) {
    if (error.errorFields) {
      message.error('请填写必填项')
    } else {
      message.error('提交失败')
    }
  }
}

// 上传变化
const handleUploadChange = (info) => {
  if (info.file.status === 'done') {
    message.success(`${info.file.name} 上传成功`)
    attachmentList.value.push({
      id: Date.now(),
      name: info.file.name,
      size: formatFileSize(info.file.size),
      uploadTime: new Date().toLocaleString(),
      url: info.file.response?.url
    })
  } else if (info.file.status === 'error') {
    message.error(`${info.file.name} 上传失败`)
  }
}

// 删除文件
const handleDeleteFile = (record) => {
  const index = attachmentList.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    attachmentList.value.splice(index, 1)
    message.success('删除成功')
  }
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (!size) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  let index = 0
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024
    index++
  }
  return `${size.toFixed(2)} ${units[index]}`
}

// VPP核对
const handleCheckVpp = () => {
  if (!formData.projectId) {
    message.warning('请先选择项目')
    return
  }
  router.push(`/vpp/detail/${formData.projectId}`)
}

// 返回
const handleBack = () => {
  router.back()
}

// 筛选选项
const filterOption = (input, option) => {
  return option.children.toLowerCase().includes(input.toLowerCase())
}

onMounted(() => {
  fetchProjects()

  const { id } = route.query
  if (id) {
    isEdit.value = true
    acceptanceId.value = id
    fetchDetail(id)
  }
})
</script>

<style scoped>
.acceptance-form {
  padding: 24px;
}

.form-card {
  margin-top: 16px;
}
</style>
