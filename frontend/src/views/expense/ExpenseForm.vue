<template>
  <div class="expense-form">
    <a-card title="杂项费用录入" :bordered="false">
      <a-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        layout="horizontal"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 18 }"
      >
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="项目" name="project">
              <a-select
                v-model:value="formData.project"
                placeholder="请选择项目"
                :disabled="!!route.query.projectId"
                show-search
                :filter-option="filterOption"
              >
                <a-select-option v-for="item in projectList" :key="item.id" :value="item.id">
                  {{ item.code }} - {{ item.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="结算周期" name="period">
              <a-month-picker
                v-model:value="formData.period"
                style="width: 100%"
                placeholder="请选择结算周期"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="部门" name="department">
              <a-select
                v-model:value="formData.department"
                placeholder="请选择部门"
                show-search
                :filter-option="filterOption"
              >
                <a-select-option v-for="item in departmentList" :key="item.id" :value="item.id">
                  {{ item.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="杂费类型" name="expenseType">
              <a-select v-model:value="formData.expenseType" placeholder="请选择杂费类型">
                <a-select-option value="reserve">备用金</a-select-option>
                <a-select-option value="fuel">油耗</a-select-option>
                <a-select-option value="travel">项目差旅</a-select-option>
                <a-select-option value="purchase">采购</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="资源类型" name="resourceType">
              <a-select v-model:value="formData.resourceType" placeholder="请选择资源类型">
                <a-select-option value="human">人力</a-select-option>
                <a-select-option value="material">物料</a-select-option>
                <a-select-option value="equipment">设备</a-select-option>
                <a-select-option value="service">服务</a-select-option>
                <a-select-option value="other">其他</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="资源名" name="resourceName">
              <a-input v-model:value="formData.resourceName" placeholder="请输入资源名" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="预计价格" name="expectedPrice">
              <a-input-number
                v-model:value="formData.expectedPrice"
                :min="0"
                :precision="2"
                style="width: 100%"
                placeholder="请输入预计价格"
                @change="calculateAmount"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="预计数量" name="expectedQuantity">
              <a-input-number
                v-model:value="formData.expectedQuantity"
                :min="0"
                :precision="2"
                style="width: 100%"
                placeholder="请输入预计数量"
                @change="calculateAmount"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item label="预计金额">
              <a-input-number
                v-model:value="calculatedAmount"
                :disabled="true"
                :precision="2"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="备注" name="remark">
              <a-textarea
                v-model:value="formData.remark"
                :rows="2"
                placeholder="请输入备注"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <a-button type="primary" @click="handleSubmit" :loading="submitLoading">保存</a-button>
        <a-button style="margin-left: 8px" @click="handleCancel">取消</a-button>
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { createMiscExpense, updateMiscExpense, getMiscExpense } from '@/api/auxiliary'
import { getProjects } from '@/api/project'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)

const formRef = ref(null)
const submitLoading = ref(false)

// 表单数据
const formData = reactive({
  project: undefined,
  period: null,
  department: undefined,
  expenseType: undefined,
  resourceType: undefined,
  resourceName: '',
  expectedPrice: 0,
  expectedQuantity: 0,
  remark: ''
})

// 规则
const rules = {
  project: [{ required: true, message: '请选择项目', trigger: 'change' }],
  period: [{ required: true, message: '请选择结算周期', trigger: 'change' }],
  department: [{ required: true, message: '请选择部门', trigger: 'change' }],
  expenseType: [{ required: true, message: '请选择杂费类型', trigger: 'change' }],
  resourceType: [{ required: true, message: '请选择资源类型', trigger: 'change' }],
  resourceName: [{ required: true, message: '请输入资源名', trigger: 'blur' }],
  expectedPrice: [{ required: true, message: '请输入预计价格', trigger: 'blur' }],
  expectedQuantity: [{ required: true, message: '请输入预计数量', trigger: 'blur' }]
}

// 项目列表
const projectList = ref([])
// 部门列表（模拟）
const departmentList = ref([
  { id: 'dept1', name: '研发部' },
  { id: 'dept2', name: '市场部' },
  { id: 'dept3', name: '财务部' },
  { id: 'dept4', name: '人事部' },
  { id: 'dept5', name: '运营部' }
])

// 计算预计金额
const calculatedAmount = computed(() => {
  const price = formData.expectedPrice || 0
  const quantity = formData.expectedQuantity || 0
  return price * quantity
})

// 计算金额
const calculateAmount = () => {
  // 计算逻辑在computed中处理
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

// 加载费用详情
const loadExpenseDetail = async () => {
  if (!isEdit.value) {
    // 如果有projectId参数，自动填充
    if (route.query.projectId) {
      formData.project = Number(route.query.projectId)
    }
    return
  }
  
  try {
    const res = await getMiscExpense(route.params.id)
    Object.assign(formData, {
      ...res,
      period: res.period ? dayjs(res.period) : null
    })
  } catch (error) {
    message.error('加载费用详情失败')
  }
}

// 筛选选项
const filterOption = (input, option) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true

    const submitData = {
      ...formData,
      period: formData.period ? dayjs(formData.period).format('YYYY-MM') : null,
      expectedAmount: calculatedAmount.value
    }

    if (isEdit.value) {
      await updateMiscExpense(route.params.id, submitData)
      message.success('更新成功')
    } else {
      await createMiscExpense(submitData)
      message.success('创建成功')
    }

    router.push('/expense')
  } catch (error) {
    console.error('提交失败', error)
    message.error('提交失败，请检查表单')
  } finally {
    submitLoading.value = false
  }
}

// 取消
const handleCancel = () => {
  router.back()
}

onMounted(() => {
  loadProjects()
  loadExpenseDetail()
})
</script>

<style scoped>
.expense-form {
  padding: 24px;
}

.form-actions {
  margin-top: 24px;
  text-align: center;
}
</style>
