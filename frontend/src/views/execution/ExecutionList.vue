<template>
  <div class="execution-list">
    <a-card title="项目执行汇总" :bordered="false">
      <!-- 查询区域 -->
      <a-form layout="inline" class="search-form">
        <a-form-item label="项目编码">
          <a-input
            v-model:value="searchForm.project_code"
            placeholder="请输入项目编码"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="项目名称">
          <a-input
            v-model:value="searchForm.project_name"
            placeholder="请输入项目名称"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="项目状态">
          <a-select
            v-model:value="searchForm.status"
            placeholder="请选择状态"
            allow-clear
            style="width: 160px"
          >
            <a-select-option value="DRAFT">草稿</a-select-option>
            <a-select-option value="ONGOING">进行中</a-select-option>
            <a-select-option value="HOLD">暂停</a-select-option>
            <a-select-option value="CLOSURE">已关闭</a-select-option>
            <a-select-option value="CANCEL">已取消</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="handleSearch">
            <template #icon><SearchOutlined /></template>
            查询
          </a-button>
          <a-button style="margin-left: 8px" @click="handleReset">
            <template #icon><ReloadOutlined /></template>
            重置
          </a-button>
        </a-form-item>
      </a-form>

      <!-- 表格区域 -->
      <a-table
        :columns="columns"
        :data-source="tableData"
        :loading="loading"
        :pagination="pagination"
        row-key="project_id"
        @change="handleTableChange"
        @row-click="handleRowClick"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'overallProgress'">
            <a-progress
              :percent="record.overallProgress || 0"
              :status="getProgressStatus(record.overallProgress || 0)"
              size="small"
            />
          </template>
          <template v-if="column.key === 'planAmount'">
            <span>¥{{ formatMoney(record.contract_amount) }}</span>
          </template>
          <template v-if="column.key === 'actualAmount'">
            <span :style="{ color: (record.actualAmount || 0) > (record.contract_amount || 0) ? '#ff4d4f' : 'inherit' }">
              ¥{{ formatMoney(record.actualAmount) }}
            </span>
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { getExecutionList } from '@/api/project'

const router = useRouter()

// 查询表单
const searchForm = reactive({
  project_code: '',
  project_name: '',
  status: undefined
})

// 表格数据
const tableData = ref([])
const loading = ref(false)
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true
})

// 表格列定义
const columns = [
  {
    title: '项目编码',
    dataIndex: 'project_code',
    key: 'project_code',
    width: 150
  },
  {
    title: '项目名称',
    dataIndex: 'project_name',
    key: 'project_name',
    ellipsis: true
  },
  {
    title: '项目经理',
    dataIndex: 'pm',
    key: 'pm',
    width: 120
  },
  {
    title: '整体进度',
    dataIndex: 'overallProgress',
    key: 'overallProgress',
    width: 180
  },
  {
    title: '计划总金额',
    dataIndex: 'contract_amount',
    key: 'planAmount',
    width: 140,
    align: 'right'
  },
  {
    title: '实际总金额',
    dataIndex: 'actualAmount',
    key: 'actualAmount',
    width: 140,
    align: 'right'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100
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
    DRAFT: 'default',
    ONGOING: 'processing',
    HOLD: 'warning',
    CLOSURE: 'success',
    CANCEL: 'error'
  }
  return colorMap[status] || 'default'
}

// 状态文本映射
const getStatusText = (status) => {
  const textMap = {
    DRAFT: '草稿',
    ONGOING: '进行中',
    HOLD: '暂停',
    CLOSURE: '已关闭',
    CANCEL: '已取消'
  }
  return textMap[status] || status
}

// 加载数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      ...searchForm
    }
    const res = await getExecutionList(params)
    tableData.value = res.data?.list || res.results || []
    pagination.total = res.data?.total || res.count || 0
  } catch (error) {
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 查询
const handleSearch = () => {
  pagination.current = 1
  fetchData()
}

// 重置
const handleReset = () => {
  searchForm.project_code = ''
  searchForm.project_name = ''
  searchForm.status = undefined
  handleSearch()
}

// 表格变化
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchData()
}

// 行点击
const handleRowClick = (record) => {
  router.push(`/execution/detail/${record.project_id}`)
}

onMounted(fetchData)
</script>

<style scoped>
.execution-list {
  padding: 24px;
}

.search-form {
  margin-bottom: 24px;
}

:deep(.ant-table-row) {
  cursor: pointer;
}

:deep(.ant-table-row:hover) {
  background-color: #e6f7ff;
}
</style>
