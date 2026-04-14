<template>
  <div class="meeting-form">
    <a-card title="会议录入" :bordered="false">
      <a-tabs v-model:activeKey="activeTabKey">
        <!-- Tab1: 会议信息 -->
        <a-tab-pane key="info" tab="会议信息">
          <a-form
            ref="formRef"
            :model="formData"
            :rules="rules"
            layout="horizontal"
            :label-col="{ span: 4 }"
            :wrapper-col="{ span: 20 }"
          >
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="会议主题" name="subject">
                  <a-input v-model:value="formData.subject" placeholder="请输入会议主题" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="项目" name="project">
                  <a-select
                    v-model:value="formData.project"
                    placeholder="请选择项目"
                    show-search
                    :filter-option="filterOption"
                  >
                    <a-select-option v-for="item in projectList" :key="item.id" :value="item.id">
                      {{ item.code }} - {{ item.name }}
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="24">
              <a-col :span="8">
                <a-form-item label="会议日期" name="meetingDate">
                  <a-date-picker v-model:value="formData.meetingDate" style="width: 100%" placeholder="请选择日期" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="会议时间" name="meetingTime">
                  <a-time-picker v-model:value="formData.meetingTime" style="width: 100%" format="HH:mm" placeholder="请选择时间" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="时长(分钟)" name="duration">
                  <a-input-number v-model:value="formData.duration" :min="15" :step="15" style="width: 100%" placeholder="请输入时长" />
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="组织人" name="organizer">
                  <a-select
                    v-model:value="formData.organizer"
                    placeholder="请选择组织人"
                    show-search
                    :filter-option="filterOption"
                  >
                    <a-select-option v-for="item in employeeList" :key="item.id" :value="item.id">
                      {{ item.name }}
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="会议类型" name="meetingType">
                  <a-select v-model:value="formData.meetingType" placeholder="请选择会议类型">
                    <a-select-option value="regular">例会</a-select-option>
                    <a-select-option value="review">评审会</a-select-option>
                    <a-select-option value="kickoff">启动会</a-select-option>
                    <a-select-option value="summary">总结会</a-select-option>
                    <a-select-option value="other">其他</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>

            <a-form-item label="参加人员" name="participants">
              <a-select
                v-model:value="formData.participants"
                mode="multiple"
                placeholder="请选择参加人员"
                show-search
                :filter-option="filterOption"
              >
                <a-select-option v-for="item in employeeList" :key="item.id" :value="item.id">
                  {{ item.name }}
                </a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="地点" name="location">
              <a-input v-model:value="formData.location" placeholder="请输入会议地点" />
            </a-form-item>

            <a-form-item label="会议纪要" name="minutes">
              <a-textarea
                v-model:value="formData.minutes"
                :rows="6"
                placeholder="请输入会议纪要"
              />
            </a-form-item>

            <a-form-item label="附件上传" name="attachments">
              <a-upload
                v-model:file-list="fileList"
                :action="uploadAction"
                :headers="uploadHeaders"
                multiple
                @change="handleUploadChange"
              >
                <a-button>
                  <template #icon><UploadOutlined /></template>
                  上传附件
                </a-button>
              </a-upload>
            </a-form-item>
          </a-form>
        </a-tab-pane>

        <!-- Tab2: 决定项 -->
        <a-tab-pane key="decisions" tab="决定项">
          <div class="tab-actions">
            <a-button type="primary" @click="handleAddDecision">
              <template #icon><PlusOutlined /></template>
              新增决定项
            </a-button>
          </div>
          <a-table
            :columns="decisionColumns"
            :data-source="formData.decisions"
            :pagination="false"
            row-key="id"
            bordered
          >
            <template #bodyCell="{ column, record, index }">
              <template v-if="column.key === 'seq'">
                {{ index + 1 }}
              </template>
              <template v-if="column.key === 'content'">
                <a-textarea v-model:value="record.content" :rows="2" placeholder="请输入决定事项" />
              </template>
              <template v-if="column.key === 'remark'">
                <a-input v-model:value="record.remark" placeholder="请输入备注" />
              </template>
              <template v-if="column.key === 'action'">
                <a-button type="link" danger @click="handleDeleteDecision(index)">
                  <DeleteOutlined />
                </a-button>
              </template>
            </template>
          </a-table>
        </a-tab-pane>

        <!-- Tab3: 行动项 -->
        <a-tab-pane key="actionItems" tab="行动项">
          <div class="tab-actions">
            <a-button type="primary" @click="handleAddActionItem">
              <template #icon><PlusOutlined /></template>
              新增行动项
            </a-button>
          </div>
          <a-table
            :columns="actionItemColumns"
            :data-source="formData.actionItems"
            :pagination="false"
            row-key="id"
            bordered
          >
            <template #bodyCell="{ column, record, index }">
              <template v-if="column.key === 'seq'">
                {{ index + 1 }}
              </template>
              <template v-if="column.key === 'description'">
                <a-textarea v-model:value="record.description" :rows="2" placeholder="请输入描述" />
              </template>
              <template v-if="column.key === 'responsible'">
                <a-select
                  v-model:value="record.responsible"
                  placeholder="请选择负责人"
                  style="width: 100%"
                  show-search
                  :filter-option="filterOption"
                >
                  <a-select-option v-for="item in employeeList" :key="item.id" :value="item.id">
                    {{ item.name }}
                  </a-select-option>
                </a-select>
              </template>
              <template v-if="column.key === 'dueDate'">
                <a-date-picker v-model:value="record.dueDate" style="width: 100%" placeholder="请选择到期日" />
              </template>
              <template v-if="column.key === 'status'">
                <a-select v-model:value="record.status" placeholder="请选择状态" style="width: 100%">
                  <a-select-option value="pending">待处理</a-select-option>
                  <a-select-option value="in_progress">进行中</a-select-option>
                  <a-select-option value="completed">已完成</a-select-option>
                </a-select>
              </template>
              <template v-if="column.key === 'action'">
                <a-button type="link" danger @click="handleDeleteActionItem(index)">
                  <DeleteOutlined />
                </a-button>
              </template>
            </template>
          </a-table>
        </a-tab-pane>
      </a-tabs>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <a-button type="primary" @click="handleSave" :loading="saveLoading">保存</a-button>
        <a-button type="primary" style="margin-left: 8px" @click="handleSubmitAndSend" :loading="saveLoading">提交(发邮件)</a-button>
        <a-button style="margin-left: 8px" @click="handleExport">导出会议纪要</a-button>
        <a-button style="margin-left: 8px" @click="handleCancel">取消</a-button>
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { PlusOutlined, DeleteOutlined, UploadOutlined } from '@ant-design/icons-vue'
import { createMeeting, updateMeeting, getMeeting } from '@/api/auxiliary'
import { getProjects } from '@/api/project'
import { getEmployees } from '@/api/masterData'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const activeTabKey = ref('info')

const formRef = ref(null)
const saveLoading = ref(false)

// 表单数据
const formData = reactive({
  subject: '',
  project: undefined,
  meetingDate: null,
  meetingTime: null,
  duration: 60,
  organizer: undefined,
  meetingType: 'regular',
  participants: [],
  location: '',
  minutes: '',
  decisions: [],
  actionItems: [],
  status: 'draft'
})

// 规则
const rules = {
  subject: [{ required: true, message: '请输入会议主题', trigger: 'blur' }],
  project: [{ required: true, message: '请选择项目', trigger: 'change' }],
  meetingDate: [{ required: true, message: '请选择会议日期', trigger: 'change' }],
  organizer: [{ required: true, message: '请选择组织人', trigger: 'change' }]
}

// 决定项列定义
const decisionColumns = [
  { title: '序号', key: 'seq', width: 60, align: 'center' },
  { title: '决定事项', key: 'content', width: 400 },
  { title: '备注', key: 'remark', width: 200 },
  { title: '操作', key: 'action', width: 60, fixed: 'right' }
]

// 行动项列定义
const actionItemColumns = [
  { title: '序号', key: 'seq', width: 60, align: 'center' },
  { title: '描述', key: 'description', width: 300 },
  { title: '负责人', key: 'responsible', width: 120 },
  { title: '到期日', key: 'dueDate', width: 140 },
  { title: '状态', key: 'status', width: 100 },
  { title: '操作', key: 'action', width: 60, fixed: 'right' }
]

// 项目列表
const projectList = ref([])
// 员工列表
const employeeList = ref([])
// 文件列表
const fileList = ref([])
// 上传配置
const uploadAction = '/api/auxiliary/meetings/upload/'
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token') || ''}`
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await getProjects({ page_size: 9999 })
    projectList.value = res.results || []
  } catch (error) {
    console.error('加载项目失败', error)
  }
}

// 加载员工列表
const loadEmployees = async () => {
  try {
    const res = await getEmployees({ page_size: 9999 })
    employeeList.value = res.results || []
  } catch (error) {
    console.error('加载员工失败', error)
  }
}

// 加载会议详情
const loadMeetingDetail = async () => {
  if (!isEdit.value) return
  try {
    const res = await getMeeting(route.params.id)
    Object.assign(formData, {
      ...res,
      meetingDate: res.meetingDate ? dayjs(res.meetingDate) : null,
      meetingTime: res.meetingTime ? dayjs(res.meetingTime, 'HH:mm') : null,
      decisions: res.decisions || [],
      actionItems: res.actionItems?.map(item => ({
        ...item,
        dueDate: item.dueDate ? dayjs(item.dueDate) : null
      })) || []
    })
  } catch (error) {
    message.error('加载会议详情失败')
  }
}

// 筛选选项
const filterOption = (input, option) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

// 上传变化
const handleUploadChange = (info) => {
  if (info.file.status === 'done') {
    message.success(`${info.file.name} 上传成功`)
  } else if (info.file.status === 'error') {
    message.error(`${info.file.name} 上传失败`)
  }
}

// 新增决定项
const handleAddDecision = () => {
  formData.decisions.push({
    id: Date.now(),
    content: '',
    remark: ''
  })
}

// 删除决定项
const handleDeleteDecision = (index) => {
  formData.decisions.splice(index, 1)
}

// 新增行动项
const handleAddActionItem = () => {
  formData.actionItems.push({
    id: Date.now(),
    description: '',
    responsible: undefined,
    dueDate: null,
    status: 'pending'
  })
}

// 删除行动项
const handleDeleteActionItem = (index) => {
  formData.actionItems.splice(index, 1)
}

// 保存
const handleSave = async () => {
  try {
    await formRef.value.validate()
    saveLoading.value = true

    const submitData = {
      ...formData,
      meetingDate: formData.meetingDate ? dayjs(formData.meetingDate).format('YYYY-MM-DD') : null,
      meetingTime: formData.meetingTime ? dayjs(formData.meetingTime).format('HH:mm') : null,
      actionItems: formData.actionItems.map(item => ({
        ...item,
        dueDate: item.dueDate ? dayjs(item.dueDate).format('YYYY-MM-DD') : null
      }))
    }

    if (isEdit.value) {
      await updateMeeting(route.params.id, submitData)
      message.success('更新成功')
    } else {
      await createMeeting(submitData)
      message.success('创建成功')
    }

    router.push('/meeting')
  } catch (error) {
    console.error('保存失败', error)
    message.error('保存失败，请检查表单')
  } finally {
    saveLoading.value = false
  }
}

// 提交并发送邮件
const handleSubmitAndSend = async () => {
  formData.status = 'completed'
  await handleSave()
  message.success('会议纪要已发送')
}

// 导出会议纪要
const handleExport = () => {
  message.info('导出会议纪要功能开发中')
}

// 取消
const handleCancel = () => {
  router.back()
}

onMounted(() => {
  loadProjects()
  loadEmployees()
  loadMeetingDetail()
})
</script>

<style scoped>
.meeting-form {
  padding: 24px;
}

.tab-actions {
  margin-bottom: 16px;
}

.form-actions {
  margin-top: 24px;
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}
</style>
