<template>
  <div class="seven-step-form">
    <a-card title="七步法录入" :bordered="false">
      <!-- 当前步骤展示 -->
      <div class="steps-container">
        <a-steps :current="currentStep - 1" size="small">
          <a-step title="Step 1" description="定义问题" />
          <a-step title="Step 2" description="遏制措施" />
          <a-step title="Step 3" description="根本原因" />
          <a-step title="Step 4" description="纠正措施" />
          <a-step title="Step 5" description="验证结果" />
          <a-step title="Step 6" description="预防措施" />
          <a-step title="Step 7" description="团队祝贺" />
        </a-steps>
      </div>

      <a-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        layout="horizontal"
        :label-col="{ span: 4 }"
        :wrapper-col="{ span: 20 }"
      >
        <!-- 基本信息区 -->
        <a-divider>基本信息</a-divider>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="编号" name="code">
              <a-input v-model:value="formData.code" disabled placeholder="系统自动生成" />
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

        <a-form-item label="问题描述" name="problemDescription">
          <a-textarea
            v-model:value="formData.problemDescription"
            :rows="3"
            :maxlength="1000"
            show-count
            placeholder="请输入问题描述（最多1000字）"
          />
        </a-form-item>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="FIGR Owner" name="figrOwner">
              <a-select
                v-model:value="formData.figrOwner"
                placeholder="请选择FIGR Owner"
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
            <a-form-item label="FIGR Team" name="figrTeam">
              <a-input v-model:value="formData.figrTeam" placeholder="请输入FIGR Team" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="Platform Impact" name="platformImpact">
              <a-switch v-model:checked="formData.platformImpact" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="Local Specialist" name="localSpecialist">
              <a-input v-model:value="formData.localSpecialist" placeholder="请输入Local Specialist" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="Next Action" name="nextAction">
          <a-textarea
            v-model:value="formData.nextAction"
            :rows="2"
            placeholder="请输入下一步行动"
          />
        </a-form-item>

        <a-form-item label="Risk Assessment" name="riskAssessment">
          <a-textarea
            v-model:value="formData.riskAssessment"
            :rows="2"
            placeholder="请输入风险评估"
          />
        </a-form-item>

        <!-- 七步详情 -->
        <a-divider>七步详情</a-divider>
        <a-collapse v-model:activeKey="activeCollapseKey" accordion>
          <a-collapse-panel key="1" header="Step 1: 定义问题">
            <a-form-item label="问题定义" :label-col="{ span: 2 }" :wrapper-col="{ span: 22 }">
              <a-textarea
                v-model:value="formData.step1ProblemDefinition"
                :rows="4"
                placeholder="请详细描述问题定义"
              />
            </a-form-item>
          </a-collapse-panel>

          <a-collapse-panel key="2" header="Step 2: 遏制措施">
            <a-form-item label="遏制措施" :label-col="{ span: 2 }" :wrapper-col="{ span: 22 }">
              <a-textarea
                v-model:value="formData.step2Containment"
                :rows="4"
                placeholder="请描述遏制措施"
              />
            </a-form-item>
          </a-collapse-panel>

          <a-collapse-panel key="3" header="Step 3: 根本原因">
            <a-form-item label="根本原因" :label-col="{ span: 2 }" :wrapper-col="{ span: 22 }">
              <a-textarea
                v-model:value="formData.step3RootCause"
                :rows="4"
                placeholder="请分析根本原因"
              />
            </a-form-item>
          </a-collapse-panel>

          <a-collapse-panel key="4" header="Step 4: 纠正措施">
            <a-form-item label="纠正措施" :label-col="{ span: 2 }" :wrapper-col="{ span: 22 }">
              <a-textarea
                v-model:value="formData.step4CorrectiveAction"
                :rows="4"
                placeholder="请描述纠正措施"
              />
            </a-form-item>
          </a-collapse-panel>

          <a-collapse-panel key="5" header="Step 5: 验证结果">
            <a-form-item label="验证结果" :label-col="{ span: 2 }" :wrapper-col="{ span: 22 }">
              <a-textarea
                v-model:value="formData.step5Verification"
                :rows="4"
                placeholder="请描述验证结果"
              />
            </a-form-item>
          </a-collapse-panel>

          <a-collapse-panel key="6" header="Step 6: 预防措施">
            <a-form-item label="预防措施" :label-col="{ span: 2 }" :wrapper-col="{ span: 22 }">
              <a-textarea
                v-model:value="formData.step6PreventiveAction"
                :rows="4"
                placeholder="请描述预防措施"
              />
            </a-form-item>
          </a-collapse-panel>

          <a-collapse-panel key="7" header="Step 7: 团队祝贺">
            <a-form-item label="团队祝贺" :label-col="{ span: 2 }" :wrapper-col="{ span: 22 }">
              <a-textarea
                v-model:value="formData.step7TeamRecognition"
                :rows="4"
                placeholder="请记录团队祝贺"
              />
            </a-form-item>
          </a-collapse-panel>
        </a-collapse>

        <!-- 附件上传 -->
        <a-divider>附件</a-divider>
        <a-form-item label="附件上传" :label-col="{ span: 2 }" :wrapper-col="{ span: 22 }">
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

      <!-- 操作按钮 -->
      <div class="form-actions">
        <a-button type="primary" @click="handleSave" :loading="saveLoading">保存</a-button>
        <a-button type="primary" style="margin-left: 8px" @click="handleNextStep" :loading="saveLoading">
          {{ currentStep < 7 ? '下一步' : '完成' }}
        </a-button>
        <a-button style="margin-left: 8px" @click="handleCancel">取消</a-button>
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UploadOutlined } from '@ant-design/icons-vue'
import { createSevenStep, updateSevenStep, getSevenStep } from '@/api/auxiliary'
import { getProjects } from '@/api/project'
import { getEmployees } from '@/api/masterData'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const saveLoading = ref(false)
const currentStep = ref(1)
const activeCollapseKey = ref('1')

// 判断是否为编辑模式
const isEdit = computed(() => !!route.params.id)

// 表单数据
const formData = reactive({
  code: '',
  project: undefined,
  problemDescription: '',
  figrOwner: undefined,
  figrTeam: '',
  platformImpact: false,
  localSpecialist: '',
  nextAction: '',
  riskAssessment: '',
  step1ProblemDefinition: '',
  step2Containment: '',
  step3RootCause: '',
  step4CorrectiveAction: '',
  step5Verification: '',
  step6PreventiveAction: '',
  step7TeamRecognition: ''
})

// 规则
const rules = {
  project: [{ required: true, message: '请选择项目', trigger: 'change' }],
  problemDescription: [{ required: true, message: '请输入问题描述', trigger: 'blur' }],
  figrOwner: [{ required: true, message: '请选择FIGR Owner', trigger: 'change' }]
}

// 项目列表
const projectList = ref([])
// 员工列表
const employeeList = ref([])
// 文件列表
const fileList = ref([])
// 上传地址
const uploadAction = '/api/auxiliary/seven-steps/upload/'
// 上传头
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

// 加载详情
const loadDetail = async () => {
  if (!isEdit.value) return
  try {
    const res = await getSevenStep(route.params.id)
    Object.assign(formData, res)
    currentStep.value = res.currentStep || 1
    activeCollapseKey.value = String(currentStep.value)
  } catch (error) {
    message.error('加载详情失败')
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

// 保存
const handleSave = async () => {
  try {
    await formRef.value.validate()
    saveLoading.value = true

    const submitData = {
      ...formData,
      currentStep: currentStep.value
    }

    if (isEdit.value) {
      await updateSevenStep(route.params.id, submitData)
      message.success('更新成功')
    } else {
      await createSevenStep(submitData)
      message.success('创建成功')
    }

    router.push('/seven-step')
  } catch (error) {
    console.error('保存失败', error)
    message.error('保存失败，请检查表单')
  } finally {
    saveLoading.value = false
  }
}

// 下一步
const handleNextStep = async () => {
  try {
    await formRef.value.validate()
    saveLoading.value = true

    const submitData = {
      ...formData,
      currentStep: currentStep.value < 7 ? currentStep.value + 1 : 7
    }

    if (isEdit.value) {
      await updateSevenStep(route.params.id, submitData)
    } else {
      const res = await createSevenStep(submitData)
      router.replace(`/seven-step/form/${res.id}`)
    }

    if (currentStep.value < 7) {
      currentStep.value++
      activeCollapseKey.value = String(currentStep.value)
      message.success('已进入下一步')
    } else {
      message.success('七步法已完成')
      router.push('/seven-step')
    }
  } catch (error) {
    console.error('保存失败', error)
    message.error('保存失败，请检查表单')
  } finally {
    saveLoading.value = false
  }
}

// 取消
const handleCancel = () => {
  router.back()
}

onMounted(() => {
  loadProjects()
  loadEmployees()
  loadDetail()
})
</script>

<style scoped>
.seven-step-form {
  padding: 24px;
}

.steps-container {
  margin-bottom: 24px;
  padding: 16px;
  background-color: #fafafa;
  border-radius: 4px;
}

.form-actions {
  margin-top: 24px;
  text-align: center;
}
</style>
