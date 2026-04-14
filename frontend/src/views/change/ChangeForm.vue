<template>
  <div class="change-form">
    <a-page-header
      :title="isEdit ? '编辑变更单' : '新增变更单'"
      @back="handleBack"
    />

    <a-card :bordered="false" class="form-card">
      <a-form
        :model="formData"
        layout="vertical"
        :rules="rules"
        ref="formRef"
      >
        <!-- 基本信息 -->
        <a-divider orientation="left">基本信息</a-divider>
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="变更单编号">
              <a-input v-model:value="formData.changeNo" disabled placeholder="自动生成" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="项目" name="projectId">
              <a-select
                v-model:value="formData.projectId"
                placeholder="请选择项目"
                show-search
                :filter-option="filterOption"
                :disabled="isView"
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
            <a-form-item label="变更类型" name="changeType">
              <a-radio-group v-model:value="formData.changeType" :disabled="isView">
                <a-radio value="scope">项目范围</a-radio>
                <a-radio value="schedule">计划关键路径</a-radio>
              </a-radio-group>
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 项目范围变更 -->
        <template v-if="formData.changeType === 'scope'">
          <a-divider orientation="left">范围变更信息</a-divider>
          <a-row :gutter="16">
            <a-col :span="8">
              <a-form-item label="变更字段" name="changeField">
                <a-select
                  v-model:value="formData.changeField"
                  placeholder="请选择变更字段"
                  :disabled="isView"
                >
                  <a-select-option value="name">项目名称</a-select-option>
                  <a-select-option value="description">项目描述</a-select-option>
                  <a-select-option value="budget">预算金额</a-select-option>
                  <a-select-option value="manager">项目经理</a-select-option>
                  <a-select-option value="planEnd">计划结束日期</a-select-option>
                  <a-select-option value="scope">项目范围</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="16">
            <a-col :span="24">
              <a-form-item label="变更影响" name="changeImpact">
                <a-textarea
                  v-model:value="formData.changeImpact"
                  :rows="3"
                  placeholder="请描述变更对项目的影响"
                  :disabled="isView"
                />
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="变更前">
                <a-textarea
                  v-model:value="formData.beforeValue"
                  :rows="4"
                  disabled
                  placeholder="变更前内容（自动显示）"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="变更后" name="afterValue">
                <a-textarea
                  v-model:value="formData.afterValue"
                  :rows="4"
                  placeholder="请输入变更后内容"
                  :disabled="isView"
                />
              </a-form-item>
            </a-col>
          </a-row>
        </template>

        <!-- 计划关键路径变更 -->
        <template v-if="formData.changeType === 'schedule'">
          <a-divider orientation="left">计划变更信息</a-divider>
          <a-row :gutter="16">
            <a-col :span="8">
              <a-form-item label="任务编号" name="taskId">
                <a-select
                  v-model:value="formData.taskId"
                  placeholder="请选择任务"
                  :disabled="isView || !formData.projectId"
                >
                  <a-select-option
                    v-for="task in taskOptions"
                    :key="task.id"
                    :value="task.id"
                  >
                    {{ task.wbsCode }} - {{ task.name }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="16">
            <a-col :span="24">
              <a-form-item label="变更原因" name="changeReason">
                <a-textarea
                  v-model:value="formData.changeReason"
                  :rows="3"
                  placeholder="请描述变更原因"
                  :disabled="isView"
                />
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="16">
            <a-col :span="24">
              <a-form-item label="变更内容" name="changeContent">
                <a-textarea
                  v-model:value="formData.changeContent"
                  :rows="4"
                  placeholder="请详细描述变更内容，包括计划开始/结束日期、工作量等调整"
                  :disabled="isView"
                />
              </a-form-item>
            </a-col>
          </a-row>
        </template>

        <!-- 操作按钮 -->
        <a-divider />
        <a-form-item v-if="!isView">
          <a-space>
            <a-button @click="handleSaveDraft">保存草稿</a-button>
            <a-button type="primary" @click="handleSubmit">提交审批</a-button>
            <a-button @click="handleBack">关闭</a-button>
          </a-space>
        </a-form-item>
        <a-form-item v-else>
          <a-button @click="handleBack">返回</a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getChangeDetail, createChange, updateChange, submitChange } from '@/api/change'
import { getProjectList } from '@/api/project'
import { getPlanTasks } from '@/api/plan'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)

const isEdit = ref(false)
const isView = ref(false)
const changeId = ref(null)

// 选项数据
const projectOptions = ref([])
const taskOptions = ref([])

// 表单数据
const formData = reactive({
  changeNo: '',
  projectId: undefined,
  changeType: 'scope',
  // 范围变更字段
  changeField: undefined,
  changeImpact: '',
  beforeValue: '',
  afterValue: '',
  // 计划变更字段
  taskId: undefined,
  changeReason: '',
  changeContent: ''
})

// 表单校验规则
const rules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  changeType: [{ required: true, message: '请选择变更类型', trigger: 'change' }],
  changeField: [{ required: true, message: '请选择变更字段', trigger: 'change', type: 'object' }],
  changeImpact: [{ required: true, message: '请描述变更影响', trigger: 'blur', type: 'object' }],
  afterValue: [{ required: true, message: '请输入变更后内容', trigger: 'blur', type: 'object' }],
  taskId: [{ required: true, message: '请选择任务', trigger: 'change', type: 'object' }],
  changeReason: [{ required: true, message: '请描述变更原因', trigger: 'blur', type: 'object' }],
  changeContent: [{ required: true, message: '请描述变更内容', trigger: 'blur', type: 'object' }]
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

// 加载任务选项
const fetchTasks = async (projectId) => {
  if (!projectId) {
    taskOptions.value = []
    return
  }
  try {
    const res = await getPlanTasks(projectId)
    taskOptions.value = res.data || []
  } catch (error) {
    console.error('加载任务失败', error)
  }
}

// 加载变更单详情
const fetchDetail = async (id) => {
  try {
    const res = await getChangeDetail(id)
    const data = res.data || {}
    Object.assign(formData, data)
    if (data.projectId) {
      fetchTasks(data.projectId)
    }
  } catch (error) {
    message.error('加载变更单详情失败')
  }
}

// 监听项目变化，加载任务
watch(() => formData.projectId, (newVal) => {
  if (newVal) {
    fetchTasks(newVal)
  } else {
    taskOptions.value = []
  }
})

// 保存草稿
const handleSaveDraft = async () => {
  try {
    await formRef.value.validate()
    const data = { ...formData, status: 'draft' }
    if (isEdit.value) {
      await updateChange(changeId.value, data)
    } else {
      await createChange(data)
    }
    message.success('保存草稿成功')
    router.back()
  } catch (error) {
    if (error.errorFields) {
      message.error('请填写必填项')
    } else {
      message.error('保存失败')
    }
  }
}

// 提交审批
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    const data = { ...formData, status: 'pending' }
    if (isEdit.value) {
      await updateChange(changeId.value, data)
      await submitChange(changeId.value)
    } else {
      const res = await createChange(data)
      await submitChange(res.data?.id)
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

  const { id, view } = route.query
  if (id) {
    isEdit.value = true
    changeId.value = id
    fetchDetail(id)
  }
  if (view === '1') {
    isView.value = true
  }
})
</script>

<style scoped>
.change-form {
  padding: 24px;
}

.form-card {
  margin-top: 16px;
}
</style>
