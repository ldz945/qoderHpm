<template>
  <div class="project-detail-container">
    <!-- 页面标题 -->
    <a-page-header
      :title="projectData.project_name"
      :sub-title="projectData.project_code"
      @back="goBack"
    >
      <template #extra>
        <a-tag :color="getStatusColor(projectData.status)">
          {{ getStatusText(projectData.status) }}
        </a-tag>
      </template>
    </a-page-header>

    <a-tabs v-model:activeKey="activeTab">
      <!-- Tab1: 基础信息 -->
      <a-tab-pane key="basic" tab="基础信息">
        <a-card>
          <a-descriptions :column="2" bordered>
            <a-descriptions-item label="项目编码">{{ projectData.project_code || '-' }}</a-descriptions-item>
            <a-descriptions-item label="项目名称">{{ projectData.project_name || '-' }}</a-descriptions-item>
            <a-descriptions-item label="项目类型">{{ projectData.project_type || '-' }}</a-descriptions-item>
            <a-descriptions-item label="版本">{{ projectData.version || '-' }}</a-descriptions-item>
            <a-descriptions-item label="合同金额">{{ projectData.contract_amount ? `${projectData.currency} ${projectData.contract_amount}` : '-' }}</a-descriptions-item>
            <a-descriptions-item label="币种">{{ projectData.currency || '-' }}</a-descriptions-item>
            <a-descriptions-item label="状态">
              <a-tag :color="getStatusColor(projectData.status)">
                {{ getStatusText(projectData.status) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="健康状态">
              <a-badge :color="getHealthColor(projectData.health_status)" :text="getHealthText(projectData.health_status)" />
            </a-descriptions-item>
            <a-descriptions-item label="项目经理">{{ projectData.project_manager || '-' }}</a-descriptions-item>
            <a-descriptions-item label="客户名称">{{ projectData.customer_name || '-' }}</a-descriptions-item>
            <a-descriptions-item label="项目等级">{{ projectData.project_level || '-' }}</a-descriptions-item>
            <a-descriptions-item label="项目阶段">{{ projectData.project_phase || '-' }}</a-descriptions-item>
            <a-descriptions-item label="开始日期">{{ projectData.start_date || '-' }}</a-descriptions-item>
            <a-descriptions-item label="计划完成日期">{{ projectData.planned_end_date || '-' }}</a-descriptions-item>
            <a-descriptions-item label="实际完成日期">{{ projectData.actual_end_date || '-' }}</a-descriptions-item>
            <a-descriptions-item label="项目描述" :span="2">{{ projectData.description || '-' }}</a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-tab-pane>

      <!-- Tab2: 项目任务 -->
      <a-tab-pane key="tasks" tab="项目任务">
        <a-card>
          <a-table
            :columns="taskColumns"
            :data-source="taskDataSource"
            :loading="taskLoading"
            :pagination="taskPagination"
            row-key="task_id"
            @change="handleTaskTableChange"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag :color="getTaskStatusColor(record.status)">
                  {{ getTaskStatusText(record.status) }}
                </a-tag>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>

      <!-- Tab3: 项目成员 -->
      <a-tab-pane key="members" tab="项目成员">
        <a-card>
          <div class="table-operations">
            <a-button type="primary" @click="handleAddMember">
              <PlusOutlined />添加成员
            </a-button>
          </div>
          <a-table
            :columns="memberColumns"
            :data-source="memberDataSource"
            :loading="memberLoading"
            :pagination="memberPagination"
            row-key="member_id"
            @change="handleMemberTableChange"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'is_core'">
                <a-tag :color="record.is_core ? 'red' : 'default'">
                  {{ record.is_core ? '是' : '否' }}
                </a-tag>
              </template>
              <template v-if="column.key === 'action'">
                <a-space>
                  <a-button type="link" size="small" @click="handleEditMember(record)">
                    <EditOutlined />编辑
                  </a-button>
                  <a-popconfirm
                    title="确定要移除该成员吗？"
                    @confirm="handleDeleteMember(record.member_id)"
                  >
                    <a-button type="link" danger size="small">
                      <DeleteOutlined />移除
                    </a-button>
                  </a-popconfirm>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
    </a-tabs>

    <!-- 编辑成员弹窗 -->
    <a-modal
      v-model:open="memberModalVisible"
      :title="isEditMember ? '编辑成员' : '添加成员'"
      :confirm-loading="memberSubmitLoading"
      @ok="handleSubmitMember"
      @cancel="handleCancelMember"
      width="600px"
    >
      <a-form
        ref="memberFormRef"
        :model="memberForm"
        :rules="memberFormRules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item v-if="!isEditMember" label="选择员工" name="employee_id">
          <a-select v-model:value="memberForm.employee_id" placeholder="请选择员工">
            <a-select-option v-for="emp in employeeOptions" :key="emp.employee_id" :value="emp.employee_id">
              {{ emp.employee_name }} ({{ emp.employee_code }})
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="角色" name="role">
          <a-select v-model:value="memberForm.role" placeholder="请选择角色">
            <a-select-option value="PM">项目经理</a-select-option>
            <a-select-option value="PL">项目组长</a-select-option>
            <a-select-option value="MEMBER">成员</a-select-option>
            <a-select-option value="OBSERVER">观察员</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="核心成员" name="is_core">
          <a-switch v-model:checked="memberForm.is_core" />
        </a-form-item>
        <a-form-item label="人员来源" name="source">
          <a-select v-model:value="memberForm.source" placeholder="请选择人员来源">
            <a-select-option value="INTERNAL">内部</a-select-option>
            <a-select-option value="EXTERNAL">外部</a-select-option>
            <a-select-option value="PARTNER">合作伙伴</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { getProject, getProjectTasks, getProjectMembers, createProjectMember, updateProjectMember, deleteProjectMember } from '@/api/project'
import { getEmployees } from '@/api/masterData'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id

const activeTab = ref('basic')

// ===== 项目基础信息 =====
const projectData = reactive({
  project_id: null,
  project_code: '',
  project_name: '',
  project_type: '',
  version: '',
  contract_amount: null,
  currency: '',
  status: '',
  health_status: '',
  project_manager: '',
  customer_name: '',
  project_level: '',
  project_phase: '',
  start_date: '',
  planned_end_date: '',
  actual_end_date: '',
  description: ''
})

const statusMap = {
  'DRAFT': { text: '草稿', color: 'default' },
  'ONGOING': { text: '进行中', color: 'blue' },
  'HOLD': { text: '暂停', color: 'orange' },
  'CLOSURE': { text: '已关闭', color: 'green' },
  'CANCEL': { text: '已取消', color: 'red' }
}

const healthStatusMap = {
  'GREEN': { text: '健康', color: 'green' },
  'BLUE': { text: '良好', color: 'blue' },
  'YELLOW': { text: '警告', color: 'yellow' },
  'RED': { text: '危险', color: 'red' }
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusColor = (status) => statusMap[status]?.color || 'default'
const getHealthText = (health) => healthStatusMap[health]?.text || health
const getHealthColor = (health) => healthStatusMap[health]?.color || 'default'

const fetchProjectDetail = async () => {
  try {
    const res = await getProject(projectId)
    Object.assign(projectData, {
      ...res,
      project_manager: res.project_manager || res.pm || ''
    })
  } catch (error) {
    message.error('获取项目详情失败')
  }
}

// ===== 项目任务 =====
const taskLoading = ref(false)
const taskDataSource = ref([])

const taskPagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`
})

const taskStatusMap = {
  'PENDING': { text: '待开始', color: 'default' },
  'IN_PROGRESS': { text: '进行中', color: 'blue' },
  'COMPLETED': { text: '已完成', color: 'green' },
  'DELAYED': { text: '延期', color: 'red' }
}

const getTaskStatusText = (status) => taskStatusMap[status]?.text || status
const getTaskStatusColor = (status) => taskStatusMap[status]?.color || 'default'

const taskColumns = [
  { title: '任务编码', dataIndex: 'task_code', key: 'task_code', width: 150 },
  { title: '任务名称', dataIndex: 'task_name', key: 'task_name', width: 250 },
  { title: '计划开始日期', dataIndex: 'planned_start_date', key: 'planned_start_date', width: 120 },
  { title: '计划完成日期', dataIndex: 'planned_end_date', key: 'planned_end_date', width: 120 },
  { title: '实际开始日期', dataIndex: 'actual_start_date', key: 'actual_start_date', width: 120 },
  { title: '实际完成日期', dataIndex: 'actual_end_date', key: 'actual_end_date', width: 120 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 }
]

const fetchTaskData = async () => {
  taskLoading.value = true
  try {
    const res = await getProjectTasks({
      project_id: projectId,
      page: taskPagination.current,
      page_size: taskPagination.pageSize
    })
    taskDataSource.value = res.results || []
    taskPagination.total = res.count || 0
  } catch (error) {
    message.error('获取项目任务列表失败')
  } finally {
    taskLoading.value = false
  }
}

const handleTaskTableChange = (pag) => {
  taskPagination.current = pag.current
  taskPagination.pageSize = pag.pageSize
  fetchTaskData()
}

// ===== 项目成员 =====
const memberLoading = ref(false)
const memberSubmitLoading = ref(false)
const memberDataSource = ref([])
const employeeOptions = ref([])
const memberModalVisible = ref(false)
const isEditMember = ref(false)
const memberFormRef = ref(null)

const memberPagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`
})

const memberForm = reactive({
  member_id: null,
  project_id: projectId,
  employee_id: null,
  role: 'MEMBER',
  is_core: false,
  source: 'INTERNAL'
})

const memberFormRules = {
  employee_id: [{ required: true, message: '请选择员工', trigger: 'change' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const memberColumns = [
  { title: '员工姓名', dataIndex: 'employee_name', key: 'employee_name', width: 120 },
  { title: '工号', dataIndex: 'employee_code', key: 'employee_code', width: 120 },
  { title: '部门', dataIndex: 'department', key: 'department', width: 150 },
  { title: '角色', dataIndex: 'role', key: 'role', width: 100 },
  { title: '核心成员', dataIndex: 'is_core', key: 'is_core', width: 100 },
  { title: '人员来源', dataIndex: 'source', key: 'source', width: 100 },
  { title: '操作', key: 'action', fixed: 'right', width: 150 }
]

const resetMemberForm = () => {
  Object.assign(memberForm, {
    member_id: null,
    project_id: projectId,
    employee_id: null,
    role: 'MEMBER',
    is_core: false,
    source: 'INTERNAL'
  })
}

const fetchMemberData = async () => {
  memberLoading.value = true
  try {
    const res = await getProjectMembers({
      project_id: projectId,
      page: memberPagination.current,
      page_size: memberPagination.pageSize
    })
    memberDataSource.value = res.results || []
    memberPagination.total = res.count || 0
  } catch (error) {
    message.error('获取项目成员列表失败')
  } finally {
    memberLoading.value = false
  }
}

const fetchEmployeeOptions = async () => {
  try {
    const res = await getEmployees({ page_size: 1000 })
    // 过滤掉已添加的成员
    const existingEmployeeIds = memberDataSource.value.map(m => m.employee_id)
    employeeOptions.value = (res.results || []).filter(emp => !existingEmployeeIds.includes(emp.employee_id))
  } catch (error) {
    message.error('获取员工列表失败')
  }
}

const handleMemberTableChange = (pag) => {
  memberPagination.current = pag.current
  memberPagination.pageSize = pag.pageSize
  fetchMemberData()
}

const handleAddMember = async () => {
  isEditMember.value = false
  resetMemberForm()
  await fetchEmployeeOptions()
  memberModalVisible.value = true
}

const handleEditMember = (record) => {
  isEditMember.value = true
  Object.assign(memberForm, record)
  memberModalVisible.value = true
}

const handleDeleteMember = async (id) => {
  try {
    await deleteProjectMember(id)
    message.success('移除成功')
    fetchMemberData()
  } catch (error) {
    message.error('移除失败')
  }
}

const handleSubmitMember = async () => {
  try {
    await memberFormRef.value.validate()
    memberSubmitLoading.value = true
    
    if (isEditMember.value) {
      await updateProjectMember(memberForm.member_id, memberForm)
      message.success('编辑成功')
    } else {
      await createProjectMember(memberForm)
      message.success('添加成功')
    }
    
    memberModalVisible.value = false
    fetchMemberData()
  } catch (error) {
    if (error.errorFields) return
    message.error(isEditMember.value ? '编辑失败' : '添加失败')
  } finally {
    memberSubmitLoading.value = false
  }
}

const handleCancelMember = () => {
  memberModalVisible.value = false
  memberFormRef.value?.resetFields()
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchProjectDetail()
  fetchTaskData()
  fetchMemberData()
})
</script>

<style scoped>
.project-detail-container {
  padding: 16px;
}

.table-operations {
  margin-bottom: 16px;
}
</style>
