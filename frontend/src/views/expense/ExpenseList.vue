<template>
  <div class="expense-list">
    <a-card title="杂项费用管理" :bordered="false">
      <a-tabs v-model:activeKey="activeTabKey">
        <!-- Tab1: 预计费用 -->
        <a-tab-pane key="expected" tab="预计费用">
          <!-- 查询区域 -->
          <a-form layout="inline" class="search-form">
            <a-form-item label="项目编码">
              <a-input
                v-model:value="expectedSearchForm.projectCode"
                placeholder="请输入项目编码"
                allow-clear
              />
            </a-form-item>
            <a-form-item label="结算周期">
              <a-month-picker
                v-model:value="expectedSearchForm.period"
                placeholder="请选择结算周期"
                style="width: 160px"
              />
            </a-form-item>
            <a-form-item label="杂费类型">
              <a-select
                v-model:value="expectedSearchForm.expenseType"
                placeholder="请选择杂费类型"
                allow-clear
                style="width: 140px"
              >
                <a-select-option value="reserve">备用金</a-select-option>
                <a-select-option value="fuel">油耗</a-select-option>
                <a-select-option value="travel">项目差旅</a-select-option>
                <a-select-option value="purchase">采购</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="handleExpectedSearch">
                <template #icon><SearchOutlined /></template>
                查询
              </a-button>
              <a-button style="margin-left: 8px" @click="handleExpectedReset">
                <template #icon><ReloadOutlined /></template>
                重置
              </a-button>
            </a-form-item>
          </a-form>

          <!-- 操作按钮 -->
          <div class="table-operations">
            <a-button type="primary" @click="handleAdd">
              <template #icon><PlusOutlined /></template>
              新增费用
            </a-button>
          </div>

          <!-- 表格区域 -->
          <a-table
            :columns="expectedColumns"
            :data-source="expectedTableData"
            :loading="expectedLoading"
            :pagination="expectedPagination"
            row-key="id"
            @change="handleExpectedTableChange"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'expenseType'">
                {{ getExpenseTypeText(record.expenseType) }}
              </template>
              <template v-if="column.key === 'expectedAmount'">
                <span style="color: #1890ff; font-weight: bold;">{{ formatMoney(record.expectedAmount) }}</span>
              </template>
              <template v-if="column.key === 'status'">
                <a-tag :color="getStatusColor(record.status)">
                  {{ getStatusText(record.status) }}
                </a-tag>
              </template>
              <template v-if="column.key === 'action'">
                <a-button type="link" @click="handleEdit(record)">编辑</a-button>
                <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
              </template>
            </template>
          </a-table>
        </a-tab-pane>

        <!-- Tab2: 费用对比 -->
        <a-tab-pane key="comparison" tab="费用对比">
          <!-- 查询区域 -->
          <a-form layout="inline" class="search-form">
            <a-form-item label="项目编码">
              <a-input
                v-model:value="comparisonSearchForm.projectCode"
                placeholder="请输入项目编码"
                allow-clear
              />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="handleComparisonSearch">
                <template #icon><SearchOutlined /></template>
                查询
              </a-button>
              <a-button style="margin-left: 8px" @click="handleComparisonReset">
                <template #icon><ReloadOutlined /></template>
                重置
              </a-button>
            </a-form-item>
          </a-form>

          <!-- 对比表格 -->
          <a-table
            :columns="comparisonColumns"
            :data-source="comparisonTableData"
            :loading="comparisonLoading"
            :pagination="comparisonPagination"
            row-key="id"
            @change="handleComparisonTableChange"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'expenseType'">
                {{ getExpenseTypeText(record.expenseType) }}
              </template>
              <template v-if="column.key === 'expectedAmount'">
                <span style="color: #1890ff;">{{ formatMoney(record.expectedAmount) }}</span>
              </template>
              <template v-if="column.key === 'actualAmount'">
                <span style="color: #52c41a;">{{ formatMoney(record.actualAmount) }}</span>
              </template>
              <template v-if="column.key === 'difference'">
                <span :style="{ color: record.difference >= 0 ? '#52c41a' : '#ff4d4f' }">
                  {{ record.difference >= 0 ? '+' : '' }}{{ formatMoney(record.difference) }}
                </span>
              </template>
              <template v-if="column.key === 'differencePercent'">
                <a-progress
                  :percent="Math.abs(record.differencePercent)"
                  :status="record.difference >= 0 ? 'success' : 'exception'"
                  size="small"
                />
              </template>
            </template>
          </a-table>
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { getMiscExpenses, deleteMiscExpense } from '@/api/auxiliary'
import dayjs from 'dayjs'

const router = useRouter()

const activeTabKey = ref('expected')

// ========== 预计费用 ==========
const expectedSearchForm = reactive({
  projectCode: '',
  period: null,
  expenseType: undefined
})

const expectedTableData = ref([])
const expectedLoading = ref(false)
const expectedPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true
})

const expectedColumns = [
  { title: '项目编码', dataIndex: 'projectCode', key: 'projectCode', width: 120 },
  { title: '结算周期', dataIndex: 'period', key: 'period', width: 120 },
  { title: '部门', dataIndex: 'departmentName', key: 'departmentName', width: 120 },
  { title: '资源类型', dataIndex: 'resourceType', key: 'resourceType', width: 120 },
  { title: '资源名', dataIndex: 'resourceName', key: 'resourceName', width: 150 },
  { title: '预计价格', dataIndex: 'expectedPrice', key: 'expectedPrice', width: 120 },
  { title: '预计数量', dataIndex: 'expectedQuantity', key: 'expectedQuantity', width: 100 },
  { title: '预计金额', dataIndex: 'expectedAmount', key: 'expectedAmount', width: 120 },
  { title: '杂费类型', dataIndex: 'expenseType', key: 'expenseType', width: 100 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '操作', key: 'action', width: 150, fixed: 'right' }
]

// ========== 费用对比 ==========
const comparisonSearchForm = reactive({
  projectCode: ''
})

const comparisonTableData = ref([])
const comparisonLoading = ref(false)
const comparisonPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true
})

const comparisonColumns = [
  { title: '项目编码', dataIndex: 'projectCode', key: 'projectCode', width: 120 },
  { title: '杂费类型', dataIndex: 'expenseType', key: 'expenseType', width: 120 },
  { title: '结算周期', dataIndex: 'period', key: 'period', width: 120 },
  { title: '预计金额', dataIndex: 'expectedAmount', key: 'expectedAmount', width: 120 },
  { title: '实际金额', dataIndex: 'actualAmount', key: 'actualAmount', width: 120 },
  { title: '差额', dataIndex: 'difference', key: 'difference', width: 120 },
  { title: '差额百分比', dataIndex: 'differencePercent', key: 'differencePercent', width: 150 }
]

// 杂费类型文本映射
const getExpenseTypeText = (type) => {
  const textMap = {
    reserve: '备用金',
    fuel: '油耗',
    travel: '项目差旅',
    purchase: '采购'
  }
  return textMap[type] || type
}

// 状态颜色映射
const getStatusColor = (status) => {
  const colorMap = {
    draft: 'default',
    approved: 'success',
    rejected: 'error'
  }
  return colorMap[status] || 'default'
}

// 状态文本映射
const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    approved: '已批准',
    rejected: '已驳回'
  }
  return textMap[status] || status
}

// 格式化金额
const formatMoney = (amount) => {
  if (amount === null || amount === undefined) return '-'
  return '¥' + Number(amount).toFixed(2)
}

// 加载预计费用数据
const fetchExpectedData = async () => {
  expectedLoading.value = true
  try {
    const params = {
      page: expectedPagination.current,
      page_size: expectedPagination.pageSize,
      project_code: expectedSearchForm.projectCode,
      period: expectedSearchForm.period ? dayjs(expectedSearchForm.period).format('YYYY-MM') : undefined,
      expense_type: expectedSearchForm.expenseType
    }
    const res = await getMiscExpenses(params)
    expectedTableData.value = res.results || []
    expectedPagination.total = res.count || 0
  } catch (error) {
    message.error('加载数据失败')
  } finally {
    expectedLoading.value = false
  }
}

// 加载对比数据
const fetchComparisonData = async () => {
  comparisonLoading.value = true
  try {
    // 这里应该调用专门的对比API
    const params = {
      page: comparisonPagination.current,
      page_size: comparisonPagination.pageSize,
      project_code: comparisonSearchForm.projectCode,
      comparison: true
    }
    const res = await getMiscExpenses(params)
    // 模拟对比数据
    comparisonTableData.value = (res.results || []).map(item => ({
      ...item,
      actualAmount: item.actualAmount || item.expectedAmount * (0.8 + Math.random() * 0.4),
      difference: (item.actualAmount || item.expectedAmount * (0.8 + Math.random() * 0.4)) - item.expectedAmount,
      differencePercent: Math.round(Math.random() * 20)
    }))
    comparisonPagination.total = res.count || 0
  } catch (error) {
    message.error('加载对比数据失败')
  } finally {
    comparisonLoading.value = false
  }
}

// 预计费用查询
const handleExpectedSearch = () => {
  expectedPagination.current = 1
  fetchExpectedData()
}

// 预计费用重置
const handleExpectedReset = () => {
  expectedSearchForm.projectCode = ''
  expectedSearchForm.period = null
  expectedSearchForm.expenseType = undefined
  handleExpectedSearch()
}

// 预计费用表格变化
const handleExpectedTableChange = (pag) => {
  expectedPagination.current = pag.current
  expectedPagination.pageSize = pag.pageSize
  fetchExpectedData()
}

// 对比查询
const handleComparisonSearch = () => {
  comparisonPagination.current = 1
  fetchComparisonData()
}

// 对比重置
const handleComparisonReset = () => {
  comparisonSearchForm.projectCode = ''
  handleComparisonSearch()
}

// 对比表格变化
const handleComparisonTableChange = (pag) => {
  comparisonPagination.current = pag.current
  comparisonPagination.pageSize = pag.pageSize
  fetchComparisonData()
}

// 新增
const handleAdd = () => {
  router.push('/expense/form')
}

// 编辑
const handleEdit = (record) => {
  router.push(`/expense/form/${record.id}`)
}

// 删除
const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除该费用记录吗？`,
    onOk: async () => {
      try {
        await deleteMiscExpense(record.id)
        message.success('删除成功')
        fetchExpectedData()
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}

onMounted(() => {
  fetchExpectedData()
  fetchComparisonData()
})
</script>

<style scoped>
.expense-list {
  padding: 24px;
}

.search-form {
  margin-bottom: 24px;
}

.table-operations {
  margin-bottom: 16px;
}
</style>
