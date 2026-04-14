<template>
  <div class="issue-form">
    <a-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      layout="horizontal"
      :label-col="{ span: 6 }"
      :wrapper-col="{ span: 18 }"
    >
      <a-row :gutter="24">
        <!-- 左列 -->
        <a-col :span="12">
          <a-form-item label="编号" name="code">
            <a-input v-model:value="formData.code" disabled placeholder="系统自动生成" />
          </a-form-item>
          
          <a-form-item label="项目" name="project">
            <a-select
              v-model:value="formData.project"
              placeholder="请选择项目"
              show-search
              :filter-option="filterProjectOption"
            >
              <a-select-option v-for="item in projectList" :key="item.id" :value="item.id">
                {{ item.code }} - {{ item.name }}
              </a-select-option>
            </a-select>
          </a-form-item>
          
          <a-form-item label="类型" name="type">
            <a-radio-group v-model:value="formData.type">
              <a-radio value="issue">问题</a-radio>
              <a-radio value="risk">风险</a-radio>
            </a-radio-group>
          </a-form-item>
          
          <a-form-item label="标题" name="title">
            <a-input v-model:value="formData.title" placeholder="请输入标题" />
          </a-form-item>
          
          <a-form-item label="描述" name="description">
            <a-textarea
              v-model:value="formData.description"
              :rows="4"
              placeholder="请输入描述"
            />
          </a-form-item>
          
          <a-form-item label="负责人" name="owner">
            <a-select
              v-model:value="formData.owner"
              placeholder="请选择负责人"
              show-search
              :filter-option="filterEmployeeOption"
            >
              <a-select-option v-for="item in employeeList" :key="item.id" :value="item.id">
                {{ item.name }}
              </a-select-option>
            </a-select>
          </a-form-item>
          
          <a-form-item label="问题类型" name="issueType">
            <a-input v-model:value="formData.issueType" placeholder="请输入问题类型" />
          </a-form-item>
          
          <a-form-item label="状态" name="status">
            <a-select v-model:value="formData.status" placeholder="请选择状态">
              <a-select-option value="draft">草稿</a-select-option>
              <a-select-option value="in_progress">进行中</a-select-option>
              <a-select-option value="cancelled">取消</a-select-option>
              <a-select-option value="completed">完成</a-select-option>
            </a-select>
          </a-form-item>
        </a-col>
        
        <!-- 右列 -->
        <a-col :span="12">
          <a-form-item label="重要程度" name="severity">
            <a-select v-model:value="formData.severity" placeholder="请选择重要程度">
              <a-select-option value="major">Major</a-select-option>
              <a-select-option value="some">Some</a-select-option>
              <a-select-option value="no_impact">No Impact</a-select-option>
            </a-select>
          </a-form-item>
          
          <a-form-item label="能力" name="capability">
            <a-select v-model:value="formData.capability" placeholder="请选择能力">
              <a-select-option value="incapable">Incapable</a-select-option>
              <a-select-option value="marginal">Marginal</a-select-option>
              <a-select-option value="capable">Capable</a-select-option>
            </a-select>
          </a-form-item>
          
          <a-form-item label="PROGRAM" name="program">
            <a-input v-model:value="formData.program" placeholder="请输入PROGRAM" />
          </a-form-item>
          
          <a-form-item label="NEXT M REVIEW" name="nextMReview">
            <a-input v-model:value="formData.nextMReview" placeholder="请输入NEXT M REVIEW" />
          </a-form-item>
          
          <a-form-item label="NEXT M REVIEW DATE" name="nextMReviewDate">
            <a-date-picker
              v-model:value="formData.nextMReviewDate"
              style="width: 100%"
              placeholder="请选择日期"
            />
          </a-form-item>
          
          <a-form-item label="REVISION DATE" name="revisionDate">
            <a-date-picker
              v-model:value="formData.revisionDate"
              style="width: 100%"
              placeholder="请选择日期"
            />
          </a-form-item>
        </a-col>
      </a-row>
      
      <!-- 明细列表 -->
      <a-divider>对策明细</a-divider>
      <div class="detail-actions">
        <a-button type="primary" @click="handleAddDetail">
          <template #icon><PlusOutlined /></template>
          新增对策
        </a-button>
      </div>
      <a-table
        :columns="detailColumns"
        :data-source="formData.details"
        :pagination="false"
        row-key="id"
        size="small"
        bordered
      >
        <template #bodyCell="{ column, record, index }">
          <template v-if="column.key === 'countermeasure'">
            <a-input v-model:value="record.countermeasure" placeholder="请输入对策" />
          </template>
          <template v-if="column.key === 'responsible'">
            <a-select
              v-model:value="record.responsible"
              placeholder="请选择责任人"
              style="width: 100%"
              show-search
              :filter-option="filterEmployeeOption"
            >
              <a-select-option v-for="item in employeeList" :key="item.id" :value="item.id">
                {{ item.name }}
              </a-select-option>
            </a-select>
          </template>
          <template v-if="column.key === 'dueDate'">
            <a-date-picker
              v-model:value="record.dueDate"
              style="width: 100%"
              placeholder="请选择到期日"
            />
          </template>
          <template v-if="column.key === 'status'">
            <a-select v-model:value="record.status" placeholder="请选择状态" style="width: 100%">
              <a-select-option value="pending">待处理</a-select-option>
              <a-select-option value="in_progress">进行中</a-select-option>
              <a-select-option value="completed">已完成</a-select-option>
            </a-select>
          </template>
          <template v-if="column.key === 'memberType'">
            <a-select v-model:value="record.memberType" placeholder="请选择类型" style="width: 100%">
              <a-select-option value="employee">员工</a-select-option>
              <a-select-option value="external">外部</a-select-option>
            </a-select>
          </template>
          <template v-if="column.key === 'email'">
            <a-input v-model:value="record.email" placeholder="请输入邮箱" />
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" danger @click="handleDeleteDetail(index)">
              <DeleteOutlined />
            </a-button>
          </template>
        </template>
      </a-table>
    </a-form>
    
    <!-- 操作按钮 -->
    <div class="form-actions">
      <a-button type="primary" @click="handleSubmit" :loading="submitLoading">保存</a-button>
      <a-button type="primary" style="margin-left: 8px" @click="handleSubmitAndSubmit" :loading="submitLoading">提交</a-button>
      <a-button style="margin-left: 8px" @click="handleCancel">取消</a-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { createIssueRisk, updateIssueRisk } from '@/api/auxiliary'
import { getProjects } from '@/api/project'
import { getEmployees } from '@/api/masterData'
import dayjs from 'dayjs'

const props = defineProps({
  isEdit: {
    type: Boolean,
    default: false
  },
  record: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['success', 'cancel'])

const formRef = ref(null)
const submitLoading = ref(false)

// 表单数据
const formData = reactive({
  code: '',
  project: undefined,
  type: 'issue',
  title: '',
  description: '',
  owner: undefined,
  issueType: '',
  status: 'draft',
  severity: undefined,
  capability: undefined,
  program: '',
  nextMReview: '',
  nextMReviewDate: null,
  revisionDate: null,
  details: []
})

// 规则
const rules = {
  project: [{ required: true, message: '请选择项目', trigger: 'change' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  owner: [{ required: true, message: '请选择负责人', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  severity: [{ required: true, message: '请选择重要程度', trigger: 'change' }],
  capability: [{ required: true, message: '请选择能力', trigger: 'change' }]
}

// 明细列定义
const detailColumns = [
  { title: '对策', key: 'countermeasure', width: 200 },
  { title: '责任人', key: 'responsible', width: 120 },
  { title: '到期日', key: 'dueDate', width: 140 },
  { title: '状态', key: 'status', width: 100 },
  { title: '成员类型', key: 'memberType', width: 100 },
  { title: '邮箱', key: 'email', width: 150 },
  { title: '操作', key: 'action', width: 60, fixed: 'right' }
]

// 项目列表
const projectList = ref([])
// 员工列表
const employeeList = ref([])

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

// 项目筛选
const filterProjectOption = (input, option) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

// 员工筛选
const filterEmployeeOption = (input, option) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

// 新增明细
const handleAddDetail = () => {
  formData.details.push({
    id: Date.now(),
    countermeasure: '',
    responsible: undefined,
    dueDate: null,
    status: 'pending',
    memberType: 'employee',
    email: ''
  })
}

// 删除明细
const handleDeleteDetail = (index) => {
  formData.details.splice(index, 1)
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    const submitData = {
      ...formData,
      nextMReviewDate: formData.nextMReviewDate ? dayjs(formData.nextMReviewDate).format('YYYY-MM-DD') : null,
      revisionDate: formData.revisionDate ? dayjs(formData.revisionDate).format('YYYY-MM-DD') : null,
      details: formData.details.map(item => ({
        ...item,
        dueDate: item.dueDate ? dayjs(item.dueDate).format('YYYY-MM-DD') : null
      }))
    }
    
    if (props.isEdit && props.record?.id) {
      await updateIssueRisk(props.record.id, submitData)
      message.success('更新成功')
    } else {
      await createIssueRisk(submitData)
      message.success('创建成功')
    }
    
    emit('success')
  } catch (error) {
    console.error('提交失败', error)
    message.error('提交失败，请检查表单')
  } finally {
    submitLoading.value = false
  }
}

// 提交并提交
const handleSubmitAndSubmit = async () => {
  formData.status = 'in_progress'
  await handleSubmit()
}

// 取消
const handleCancel = () => {
  emit('cancel')
}

// 监听record变化
watch(() => props.record, (newVal) => {
  if (newVal) {
    Object.assign(formData, {
      ...newVal,
      nextMReviewDate: newVal.nextMReviewDate ? dayjs(newVal.nextMReviewDate) : null,
      revisionDate: newVal.revisionDate ? dayjs(newVal.revisionDate) : null,
      details: newVal.details?.map(item => ({
        ...item,
        dueDate: item.dueDate ? dayjs(item.dueDate) : null
      })) || []
    })
  }
}, { immediate: true })

onMounted(() => {
  loadProjects()
  loadEmployees()
})

defineExpose({
  handleSubmit
})
</script>

<style scoped>
.issue-form {
  padding: 0;
}

.detail-actions {
  margin-bottom: 16px;
}

.form-actions {
  margin-top: 24px;
  text-align: center;
}
</style>
