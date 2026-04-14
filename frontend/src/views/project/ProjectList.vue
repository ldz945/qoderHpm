<template>
  <div class="project-list-container">
    <!-- 查询区域 -->
    <a-card class="search-card">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="项目编码">
          <a-input v-model:value="searchForm.project_code" placeholder="请输入项目编码" allow-clear />
        </a-form-item>
        <a-form-item label="项目名称">
          <a-input v-model:value="searchForm.project_name" placeholder="请输入项目名称" allow-clear />
        </a-form-item>
        <a-form-item label="项目类型">
          <a-select v-model:value="searchForm.project_type" placeholder="请选择项目类型" allow-clear style="width: 160px">
            <a-select-option value="VPI">VPI</a-select-option>
            <a-select-option value="VPC">VPC</a-select-option>
            <a-select-option value="CPS">CPS</a-select-option>
            <a-select-option value="Other">Other</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="项目状态">
          <a-select v-model:value="searchForm.status" placeholder="请选择项目状态" allow-clear style="width: 160px">
            <a-select-option value="DRAFT">草稿</a-select-option>
            <a-select-option value="ONGOING">进行中</a-select-option>
            <a-select-option value="HOLD">暂停</a-select-option>
            <a-select-option value="CLOSURE">已关闭</a-select-option>
            <a-select-option value="CANCEL">已取消</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="项目经理">
          <a-input v-model:value="searchForm.project_manager" placeholder="请输入项目经理" allow-clear />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="handleSearch">
            <SearchOutlined />查询
          </a-button>
          <a-button style="margin-left: 8px" @click="handleReset">
            <ReloadOutlined />重置
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 操作按钮区域 -->
    <div class="table-operations">
      <a-button type="primary" @click="handleAdd">
        <PlusOutlined />新增项目
      </a-button>
    </div>

    <!-- 数据表格 -->
    <a-table
      :columns="columns"
      :data-source="dataSource"
      :loading="loading"
      :pagination="pagination"
      row-key="project_id"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="getStatusColor(record.status)">
            {{ getStatusText(record.status) }}
          </a-tag>
        </template>
        <template v-if="column.key === 'health_status'">
          <a-badge :color="getHealthColor(record.health_status)" :text="getHealthText(record.health_status)" />
        </template>
        <template v-if="column.key === 'contract_amount'">
          {{ record.contract_amount ? `${record.currency} ${record.contract_amount}` : '-' }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="handleView(record)">
              <EyeOutlined />查看详情
            </a-button>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined, PlusOutlined, EyeOutlined } from '@ant-design/icons-vue'
import { getProjects } from '@/api/project'

const router = useRouter()
const loading = ref(false)
const dataSource = ref([])

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`
})

const searchForm = reactive({
  project_code: '',
  project_name: '',
  project_type: undefined,
  status: undefined,
  project_manager: ''
})

const statusMap = {
  'DRAFT': { text: '草稿', color: 'default' },
  'ONGOING': { text: '进行中', color: 'blue' },
  'HOLD': { text: '暂停', color: 'orange' },
  'CLOSURE': { text: '已关闭', color: 'green' },
  'CANCEL': { text: '已取消', color: 'red' }
}

const healthStatusMap = {
  'GREEN': { text: '健康', color: 'green' },
  'BLUE': { text: '良好', color: 'blue' },
  'YELLOW': { text: '警告', color: 'yellow' },
  'RED': { text: '危险', color: 'red' }
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusColor = (status) => statusMap[status]?.color || 'default'
const getHealthText = (health) => healthStatusMap[health]?.text || health
const getHealthColor = (health) => healthStatusMap[health]?.color || 'default'

const columns = [
  { title: '项目编码', dataIndex: 'project_code', key: 'project_code', width: 120, fixed: 'left' },
  { title: '项目名称', dataIndex: 'project_name', key: 'project_name', width: 200 },
  { title: '项目类型', dataIndex: 'project_type', key: 'project_type', width: 100 },
  { title: '版本', dataIndex: 'version', key: 'version', width: 80 },
  { title: '合同金额', dataIndex: 'contract_amount', key: 'contract_amount', width: 150 },
  { title: '币种', dataIndex: 'currency', key: 'currency', width: 80 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '项目经理', dataIndex: 'project_manager', key: 'project_manager', width: 120 },
  { title: '客户名称', dataIndex: 'customer_name', key: 'customer_name', width: 150 },
  { title: '项目等级', dataIndex: 'project_level', key: 'project_level', width: 100 },
  { title: '健康状态', dataIndex: 'health_status', key: 'health_status', width: 100 },
  { title: '操作', key: 'action', fixed: 'right', width: 120 }
]

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getProjects({
      ...searchForm,
      page: pagination.current,
      page_size: pagination.pageSize
    })
    dataSource.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    message.error('获取项目列表失败')
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchData()
}

const handleSearch = () => {
  pagination.current = 1
  fetchData()
}

const handleReset = () => {
  Object.assign(searchForm, {
    project_code: '',
    project_name: '',
    project_type: undefined,
    status: undefined,
    project_manager: ''
  })
  handleSearch()
}

const handleAdd = () => {
  router.push('/projects/create')
}

const handleView = (record) => {
  router.push(`/projects/${record.project_id}`)
}

onMounted(fetchData)
</script>

<style scoped>
.project-list-container {
  padding: 16px;
}

.search-card {
  margin-bottom: 16px;
}

.table-operations {
  margin-bottom: 16px;
}
</style>
