<template>
  <div class="project-create-container">
    <a-page-header title="新增项目" sub-title="创建项目基础信息" @back="goBack" />

    <a-card>
      <a-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 14 }"
      >
        <a-form-item label="项目ID" name="project_id">
          <a-input v-model:value="formData.project_id" placeholder="请输入唯一项目ID" />
        </a-form-item>

        <a-form-item label="项目编码" name="project_code">
          <a-input v-model:value="formData.project_code" placeholder="请输入项目编码" />
        </a-form-item>

        <a-form-item label="项目名称" name="project_name">
          <a-input v-model:value="formData.project_name" placeholder="请输入项目名称" />
        </a-form-item>

        <a-form-item label="项目类型" name="project_type">
          <a-select v-model:value="formData.project_type" placeholder="请选择项目类型">
            <a-select-option value="VPI">VPI</a-select-option>
            <a-select-option value="VPC">VPC</a-select-option>
            <a-select-option value="CPS">CPS</a-select-option>
            <a-select-option value="Other">Other</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="版本" name="version">
          <a-input v-model:value="formData.version" placeholder="例如 1.0" />
        </a-form-item>

        <a-form-item label="项目经理" name="pm">
          <a-input v-model:value="formData.pm" placeholder="请输入项目经理" />
        </a-form-item>

        <a-form-item label="客户名称" name="customer_name">
          <a-input v-model:value="formData.customer_name" placeholder="请输入客户名称" />
        </a-form-item>

        <a-form-item label="合同金额" name="contract_amount">
          <a-input-number v-model:value="formData.contract_amount" :min="0" :precision="2" style="width: 100%" />
        </a-form-item>

        <a-form-item label="币种" name="currency">
          <a-select v-model:value="formData.currency" placeholder="请选择币种">
            <a-select-option value="CNY">CNY</a-select-option>
            <a-select-option value="USD">USD</a-select-option>
            <a-select-option value="EUR">EUR</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="状态" name="status">
          <a-select v-model:value="formData.status" placeholder="请选择状态">
            <a-select-option value="DRAFT">草稿</a-select-option>
            <a-select-option value="ONGOING">进行中</a-select-option>
            <a-select-option value="HOLD">暂停</a-select-option>
            <a-select-option value="CLOSURE">已关闭</a-select-option>
            <a-select-option value="CANCEL">已取消</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="健康状态" name="health_status">
          <a-select v-model:value="formData.health_status" placeholder="请选择健康状态">
            <a-select-option value="GREEN">GREEN</a-select-option>
            <a-select-option value="BLUE">BLUE</a-select-option>
            <a-select-option value="YELLOW">YELLOW</a-select-option>
            <a-select-option value="RED">RED</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item :wrapper-col="{ span: 14, offset: 6 }">
          <a-space>
            <a-button @click="goBack">取消</a-button>
            <a-button type="primary" :loading="submitting" @click="handleSubmit">保存项目</a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { createProject } from '@/api/project'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)

const generateDefaultProjectId = () => `PRJ-${Date.now()}`

const formData = reactive({
  project_id: generateDefaultProjectId(),
  project_code: '',
  project_name: '',
  project_type: undefined,
  version: '1.0',
  contract_amount: 0,
  currency: 'CNY',
  status: 'DRAFT',
  pm: '',
  customer_name: '',
  health_status: 'GREEN'
})

const formRules = {
  project_id: [{ required: true, message: '请输入项目ID', trigger: 'blur' }],
  project_code: [{ required: true, message: '请输入项目编码', trigger: 'blur' }],
  project_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  project_type: [{ required: true, message: '请选择项目类型', trigger: 'change' }],
  version: [{ required: true, message: '请输入版本', trigger: 'blur' }]
}

const goBack = () => {
  router.push('/project/list')
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true

    const payload = {
      ...formData,
      project_id: String(formData.project_id).trim(),
      project_code: String(formData.project_code).trim(),
      project_name: String(formData.project_name).trim(),
      version: String(formData.version).trim(),
      pm: String(formData.pm || '').trim(),
      customer_name: String(formData.customer_name || '').trim()
    }

    const res = await createProject(payload)
    const createdProjectId = res?.project_id || res?.data?.project_id || payload.project_id
    message.success('项目创建成功')
    router.push(`/project/detail/${createdProjectId}`)
  } catch (error) {
    if (error?.errorFields) return
    message.error('项目创建失败，请检查必填项或编码是否重复')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.project-create-container {
  padding: 16px;
}
</style>

