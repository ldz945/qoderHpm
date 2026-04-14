<template>
  <div class="seven-step-list">
    <a-card title="七步法管理" :bordered="false">
      <!-- 查询区域 -->
      <a-form layout="inline" class="search-form">
        <a-form-item label="项目编码">
          <a-input
            v-model:value="searchForm.projectCode"
            placeholder="请输入项目编码"
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
            <a-select-option value="in_progress">进行中</a-select-option>
            <a-select-option value="completed">已完成</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="FIGR Owner">
          <a-input
            v-model:value="searchForm.figrOwner"
            placeholder="请输入FIGR Owner"
            allow-clear
          />
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
          <template v-if="column.key === 'problemDescription'">
            <a-typography-text :ellipsis="{ rows: 2 }" :content="record.problemDescription" />
          </template>
          <template v-if="column.key === 'currentStep'">
            <a-tag color="blue">Step {{ record.currentStep }}</a-tag>
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
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { getSevenSteps, deleteSevenStep } from '@/api/auxiliary'

const router = useRouter()

// 查询表单
const searchForm = reactive({
  projectCode: '',
  status: undefined,
  figrOwner: ''
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
    title: '问题描述',
    dataIndex: 'problemDescription',
    key: 'problemDescription',
    ellipsis: true
  },
  {
    title: 'FIGR Owner',
    dataIndex: 'figrOwnerName',
    key: 'figrOwnerName',
    width: 120
  },
  {
    title: '当前步骤',
    dataIndex: 'currentStep',
    key: 'currentStep',
    width: 100
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
    width: 150,
    fixed: 'right'
  }
]

// 状态颜色映射
const getStatusColor = (status) => {
  const colorMap = {
    draft: 'default',
    in_progress: 'processing',
    completed: 'success'
  }
  return colorMap[status] || 'default'
}

// 状态文本映射
const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    in_progress: '进行中',
    completed: '已完成'
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
    const res = await getSevenSteps(params)
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
  searchForm.status = undefined
  searchForm.figrOwner = ''
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
  router.push('/seven-step/form')
}

// 编辑
const handleEdit = (record) => {
  router.push(`/seven-step/form/${record.id}`)
}

// 删除
const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除七步法 "${record.code}" 吗？`,
    onOk: async () => {
      try {
        await deleteSevenStep(record.id)
        message.success('删除成功')
        fetchData()
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}

onMounted(fetchData)
</script>

<style scoped>
.seven-step-list {
  padding: 24px;
}

.search-form {
  margin-bottom: 24px;
}

.table-operations {
  margin-bottom: 16px;
}
</style>
