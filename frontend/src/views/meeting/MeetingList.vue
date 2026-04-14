<template>
  <div class="meeting-list">
    <a-card title="会议管理" :bordered="false">
      <!-- 查询区域 -->
      <a-form layout="inline" class="search-form">
        <a-form-item label="项目编码">
          <a-input
            v-model:value="searchForm.projectCode"
            placeholder="请输入项目编码"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="会议主题">
          <a-input
            v-model:value="searchForm.subject"
            placeholder="请输入会议主题"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="状态">
          <a-select
            v-model:value="searchForm.status"
            placeholder="请选择状态"
            allow-clear
            style="width: 120px"
          >
            <a-select-option value="draft">草稿</a-select-option>
            <a-select-option value="completed">已完成</a-select-option>
            <a-select-option value="cancelled">已取消</a-select-option>
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
          新增会议
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
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'participants'">
            <a-typography-text :ellipsis="{ rows: 1 }" :content="record.participants" />
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" @click="handleView(record)">查看</a-button>
            <a-button type="link" @click="handleEdit(record)">编辑</a-button>
            <a-button type="link" @click="handleExport(record)">导出</a-button>
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
import { SearchOutlined, ReloadOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { getMeetings, deleteMeeting } from '@/api/auxiliary'

const router = useRouter()

// 查询表单
const searchForm = reactive({
  projectCode: '',
  subject: '',
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
    dataIndex: 'projectCode',
    key: 'projectCode',
    width: 120
  },
  {
    title: '会议主题',
    dataIndex: 'subject',
    key: 'subject',
    ellipsis: true
  },
  {
    title: '会议日期',
    dataIndex: 'meetingDate',
    key: 'meetingDate',
    width: 120
  },
  {
    title: '组织人',
    dataIndex: 'organizerName',
    key: 'organizerName',
    width: 100
  },
  {
    title: '参加人员',
    dataIndex: 'participants',
    key: 'participants',
    ellipsis: true
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100
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
    completed: 'success',
    cancelled: 'error'
  }
  return colorMap[status] || 'default'
}

// 状态文本映射
const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    completed: '已完成',
    cancelled: '已取消'
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
    const res = await getMeetings(params)
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
  searchForm.subject = ''
  searchForm.status = undefined
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
  router.push('/meeting/form')
}

// 查看
const handleView = (record) => {
  router.push(`/meeting/detail/${record.id}`)
}

// 编辑
const handleEdit = (record) => {
  router.push(`/meeting/form/${record.id}`)
}

// 导出
const handleExport = (record) => {
  message.info(`导出会议纪要: ${record.subject}`)
}

onMounted(fetchData)
</script>

<style scoped>
.meeting-list {
  padding: 24px;
}

.search-form {
  margin-bottom: 24px;
}

.table-operations {
  margin-bottom: 16px;
}
</style>
