<template>
  <div class="change-list">
    <a-card title="变更单管理" :bordered="false">
      <!-- 查询区域 -->
      <a-form layout="inline" class="search-form">
        <a-form-item label="项目编码">
          <a-input
            v-model:value="searchForm.projectCode"
            placeholder="请输入项目编码"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="变更类型">
          <a-select
            v-model:value="searchForm.changeType"
            placeholder="请选择变更类型"
            allow-clear
            style="width: 160px"
          >
            <a-select-option value="scope">项目范围</a-select-option>
            <a-select-option value="schedule">计划关键路径</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-select
            v-model:value="searchForm.status"
            placeholder="请选择状态"
            allow-clear
            style="width: 160px"
          >
            <a-select-option value="draft">草稿</a-select-option>
            <a-select-option value="pending">待审批</a-select-option>
            <a-select-option value="approved">已批准</a-select-option>
            <a-select-option value="rejected">已驳回</a-select-option>
            <a-select-option value="implemented">已执行</a-select-option>
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
          <a-button type="primary" style="margin-left: 8px" @click="handleAdd">
            <template #icon><PlusOutlined /></template>
            新增变更单
          </a-button>
        </a-form-item>
      </a-form>

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
          <template v-if="column.key === 'changeType'">
            <a-tag :color="record.changeType === 'scope' ? 'blue' : 'green'">
              {{ getChangeTypeText(record.changeType) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleView(record)">
                查看
              </a-button>
              <a-button
                v-if="record.status === 'draft' || record.status === 'rejected'"
                type="link"
                size="small"
                @click="handleEdit(record)"
              >
                编辑
              </a-button>
            </a-space>
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
import { getChangeList } from '@/api/change'

const router = useRouter()

// 查询表单
const searchForm = reactive({
  projectCode: '',
  changeType: undefined,
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
    title: '变更单编号',
    dataIndex: 'changeNo',
    key: 'changeNo',
    width: 150
  },
  {
    title: '项目编码',
    dataIndex: 'projectCode',
    key: 'projectCode',
    width: 120
  },
  {
    title: '项目名称',
    dataIndex: 'projectName',
    key: 'projectName',
    ellipsis: true
  },
  {
    title: '变更类型',
    dataIndex: 'changeType',
    key: 'changeType',
    width: 120
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100
  },
  {
    title: '创建人',
    dataIndex: 'creator',
    key: 'creator',
    width: 100
  },
  {
    title: '创建时间',
    dataIndex: 'createTime',
    key: 'createTime',
    width: 160
  },
  {
    title: '操作',
    key: 'action',
    width: 150,
    fixed: 'right'
  }
]

// 变更类型文本
const getChangeTypeText = (type) => {
  const textMap = {
    scope: '项目范围',
    schedule: '计划关键路径'
  }
  return textMap[type] || type
}

// 状态颜色映射
const getStatusColor = (status) => {
  const colorMap = {
    draft: 'default',
    pending: 'processing',
    approved: 'success',
    rejected: 'error',
    implemented: 'blue'
  }
  return colorMap[status] || 'default'
}

// 状态文本映射
const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    pending: '待审批',
    approved: '已批准',
    rejected: '已驳回',
    implemented: '已执行'
  }
  return textMap[status] || status
}

// 加载数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      pageSize: pagination.pageSize,
      ...searchForm
    }
    const res = await getChangeList(params)
    tableData.value = res.data?.list || []
    pagination.total = res.data?.total || 0
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
  searchForm.changeType = undefined
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
  router.push('/change/form')
}

// 查看
const handleView = (record) => {
  router.push(`/change/form?id=${record.id}&view=1`)
}

// 编辑
const handleEdit = (record) => {
  router.push(`/change/form?id=${record.id}`)
}

onMounted(fetchData)
</script>

<style scoped>
.change-list {
  padding: 24px;
}

.search-form {
  margin-bottom: 24px;
}
</style>
