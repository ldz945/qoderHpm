<template>
  <div class="plan-list">
    <a-card title="项目计划管理" :bordered="false">
      <!-- 查询区域 -->
      <a-form layout="inline" class="search-form">
        <a-form-item label="项目编码">
          <a-input
            v-model:value="searchForm.project_code"
            placeholder="请输入项目编码"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="项目经理">
          <a-input
            v-model:value="searchForm.project_manager"
            placeholder="请输入项目经理"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="计划状态">
          <a-select
            v-model:value="searchForm.status"
            placeholder="请选择状态"
            allow-clear
            style="width: 160px"
          >
            <a-select-option value="DRAFT">草稿</a-select-option>
            <a-select-option value="PUBLISHED">已发布</a-select-option>
            <a-select-option value="ARCHIVED">已归档</a-select-option>
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
        row-key="version_id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" @click="handleEdit(record)">
              编辑计划
            </a-button>
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
import { getPlanList } from '@/api/plan'

const router = useRouter()

// 查询表单
const searchForm = reactive({
  project_code: '',
  project_manager: '',
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
    dataIndex: 'project_manager',
    key: 'project_manager',
    width: 120
  },
  {
    title: '计划状态',
    dataIndex: 'status',
    key: 'status',
    width: 120
  },
  {
    title: '版本号',
    dataIndex: 'version',
    key: 'version',
    width: 100
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
    fixed: 'right'
  }
]

// 状态颜色映射
const getStatusColor = (status) => {
  const colorMap = {
    DRAFT: 'default',
    PUBLISHED: 'blue',
    ARCHIVED: 'purple'
  }
  return colorMap[status] || 'default'
}

// 状态文本映射
const getStatusText = (status) => {
  const textMap = {
    DRAFT: '草稿',
    PUBLISHED: '已发布',
    ARCHIVED: '已归档'
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
    const res = await getPlanList(params)
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
  searchForm.project_manager = ''
  searchForm.status = undefined
  handleSearch()
}

// 表格变化
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchData()
}

// 编辑计划
const handleEdit = (record) => {
  router.push(`/plan/edit/${record.project}`)
}

onMounted(fetchData)
</script>

<style scoped>
.plan-list {
  padding: 24px;
}

.search-form {
  margin-bottom: 24px;
}
</style>
