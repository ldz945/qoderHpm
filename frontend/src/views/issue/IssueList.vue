<template>
  <div class="issue-list">
    <a-card title="问题/风险管理" :bordered="false">
      <!-- 查询区域 -->
      <a-form layout="inline" class="search-form">
        <a-form-item label="项目编码">
          <a-input
            v-model:value="searchForm.projectCode"
            placeholder="请输入项目编码"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="类型">
          <a-select
            v-model:value="searchForm.type"
            placeholder="请选择类型"
            allow-clear
            style="width: 120px"
          >
            <a-select-option value="issue">问题</a-select-option>
            <a-select-option value="risk">风险</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-select
            v-model:value="searchForm.status"
            placeholder="请选择状态"
            allow-clear
            style="width: 120px"
          >
            <a-select-option value="draft">草稿</a-select-option>
            <a-select-option value="in_progress">进行中</a-select-option>
            <a-select-option value="cancelled">取消</a-select-option>
            <a-select-option value="completed">完成</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="重要程度">
          <a-select
            v-model:value="searchForm.severity"
            placeholder="请选择重要程度"
            allow-clear
            style="width: 140px"
          >
            <a-select-option value="major">Major</a-select-option>
            <a-select-option value="some">Some</a-select-option>
            <a-select-option value="no_impact">No Impact</a-select-option>
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

      <!-- 操作按钮 -->
      <div class="table-operations">
        <a-button type="primary" @click="handleAdd">
          <template #icon><PlusOutlined /></template>
          新增
        </a-button>
        <a-button style="margin-left: 8px" @click="handleExport">
          <template #icon><ExportOutlined /></template>
          导出
        </a-button>
      </div>

      <!-- 表格区域 -->
      <a-table
        :columns="columns"
        :data-source="tableData"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        @change="handleTableChange"
        :row-class-name="getRowClassName"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'type'">
            <a-tag :color="record.type === 'issue' ? 'blue' : 'orange'">
              {{ record.type === 'issue' ? '问题' : '风险' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'severity'">
            {{ getSeverityText(record.severity) }}
          </template>
          <template v-if="column.key === 'capabilityColor'">
            <span :style="{ backgroundColor: getCapabilityColor(record.capability, record.severity), padding: '4px 8px', borderRadius: '4px' }">
              {{ getCapabilityText(record.capability) }}
            </span>
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" @click="handleView(record)">查看</a-button>
            <a-button type="link" @click="handleEdit(record)">编辑</a-button>
            <a-button type="link" @click="handleExportSingle(record)">导出</a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 新增/编辑弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      width="900px"
      :confirm-loading="modalLoading"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
    >
      <IssueForm
        v-if="modalVisible"
        ref="issueFormRef"
        :is-edit="isEdit"
        :record="currentRecord"
        @success="handleFormSuccess"
        @cancel="handleModalCancel"
      />
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined, PlusOutlined, ExportOutlined } from '@ant-design/icons-vue'
import { getIssueRisks, deleteIssueRisk } from '@/api/auxiliary'
import IssueForm from './IssueForm.vue'

const router = useRouter()

// 查询表单
const searchForm = reactive({
  projectCode: '',
  type: undefined,
  status: undefined,
  severity: undefined
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

// 弹窗相关
const modalVisible = ref(false)
const modalLoading = ref(false)
const modalTitle = ref('')
const isEdit = ref(false)
const currentRecord = ref(null)
const issueFormRef = ref(null)

// 表格列定义
const columns = [
  {
    title: '编号',
    dataIndex: 'code',
    key: 'code',
    width: 120
  },
  {
    title: '项目编码',
    dataIndex: 'projectCode',
    key: 'projectCode',
    width: 120
  },
  {
    title: '类型',
    dataIndex: 'type',
    key: 'type',
    width: 80
  },
  {
    title: '标题',
    dataIndex: 'title',
    key: 'title',
    ellipsis: true
  },
  {
    title: '负责人',
    dataIndex: 'ownerName',
    key: 'ownerName',
    width: 100
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100
  },
  {
    title: '重要程度',
    dataIndex: 'severity',
    key: 'severity',
    width: 100
  },
  {
    title: '能力',
    dataIndex: 'capability',
    key: 'capability',
    width: 100
  },
  {
    title: '颜色',
    key: 'capabilityColor',
    width: 100
  },
  {
    title: '创建时间',
    dataIndex: 'createdAt',
    key: 'createdAt',
    width: 160
  },
  {
    title: '操作',
    key: 'action',
    width: 200,
    fixed: 'right'
  }
]

// 状态颜色映射
const getStatusColor = (status) => {
  const colorMap = {
    draft: 'default',
    in_progress: 'processing',
    cancelled: 'error',
    completed: 'success'
  }
  return colorMap[status] || 'default'
}

// 状态文本映射
const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    in_progress: '进行中',
    cancelled: '取消',
    completed: '完成'
  }
  return textMap[status] || status
}

// 重要程度文本映射
const getSeverityText = (severity) => {
  const textMap = {
    major: 'Major',
    some: 'Some',
    no_impact: 'No Impact'
  }
  return textMap[severity] || severity
}

// 能力文本映射
const getCapabilityText = (capability) => {
  const textMap = {
    incapable: 'Incapable',
    marginal: 'Marginal',
    capable: 'Capable'
  }
  return textMap[capability] || capability
}

// 能力×重要程度矩阵颜色
const getCapabilityColor = (capability, severity) => {
  const colorMatrix = {
    incapable: {
      major: '#ff4d4f',
      some: '#ff7a45',
      no_impact: '#ffa940'
    },
    marginal: {
      major: '#ff7a45',
      some: '#ffa940',
      no_impact: '#ffc53d'
    },
    capable: {
      major: '#ffa940',
      some: '#ffc53d',
      no_impact: '#73d13d'
    }
  }
  return colorMatrix[capability]?.[severity] || '#d9d9d9'
}

// 行样式
const getRowClassName = (record) => {
  return ''
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
    const res = await getIssueRisks(params)
    tableData.value = res.results || []
    pagination.total = res.count || 0
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
  searchForm.projectCode = ''
  searchForm.type = undefined
  searchForm.status = undefined
  searchForm.severity = undefined
  handleSearch()
}

// 表格变化
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchData()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  currentRecord.value = null
  modalTitle.value = '新增问题/风险'
  modalVisible.value = true
}

// 查看
const handleView = (record) => {
  router.push(`/issue/detail/${record.id}`)
}

// 编辑
const handleEdit = (record) => {
  isEdit.value = true
  currentRecord.value = record
  modalTitle.value = '编辑问题/风险'
  modalVisible.value = true
}

// 导出
const handleExport = () => {
  message.info('导出功能开发中')
}

// 导出单个
const handleExportSingle = (record) => {
  message.info(`导出 ${record.code}`)
}

// 弹窗确认
const handleModalOk = () => {
  issueFormRef.value?.handleSubmit()
}

// 弹窗取消
const handleModalCancel = () => {
  modalVisible.value = false
}

// 表单提交成功
const handleFormSuccess = () => {
  modalVisible.value = false
  fetchData()
}

onMounted(fetchData)
</script>

<style scoped>
.issue-list {
  padding: 24px;
}

.search-form {
  margin-bottom: 24px;
}

.table-operations {
  margin-bottom: 16px;
}
</style>
