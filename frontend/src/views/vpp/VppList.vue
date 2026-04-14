<template>
  <div class="vpp-list">
    <a-card title="VPP管理" :bordered="false">
      <!-- 查询区域 -->
      <a-form layout="inline" class="search-form">
        <a-form-item label="项目编码">
          <a-input
            v-model:value="searchForm.projectCode"
            placeholder="请输入项目编码"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="项目名称">
          <a-input
            v-model:value="searchForm.projectName"
            placeholder="请输入项目名称"
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
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" @click="handleView(record)">查看</a-button>
            <a-button type="link" @click="handleEdit(record)">编辑</a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 新增弹窗 - 选择项目 -->
    <a-modal
      v-model:open="projectModalVisible"
      title="选择项目"
      @ok="handleProjectSelectOk"
      @cancel="handleProjectSelectCancel"
    >
      <a-select
        v-model:value="selectedProjectId"
        placeholder="请选择项目"
        style="width: 100%"
        show-search
        :filter-option="filterOption"
      >
        <a-select-option v-for="item in projectList" :key="item.id" :value="item.id">
          {{ item.code }} - {{ item.name }}
        </a-select-option>
      </a-select>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { getVpps, createVpp } from '@/api/auxiliary'
import { getProjects } from '@/api/project'

const router = useRouter()

// 查询表单
const searchForm = reactive({
  projectCode: '',
  projectName: ''
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

// 项目选择弹窗
const projectModalVisible = ref(false)
const projectList = ref([])
const selectedProjectId = ref(null)

// 表格列定义
const columns = [
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
    title: '版本号',
    dataIndex: 'version',
    key: 'version',
    width: 100
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100
  },
  {
    title: '创建人',
    dataIndex: 'createdByName',
    key: 'createdByName',
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
    width: 150,
    fixed: 'right'
  }
]

// 状态颜色映射
const getStatusColor = (status) => {
  const colorMap = {
    draft: 'default',
    active: 'processing',
    archived: 'success'
  }
  return colorMap[status] || 'default'
}

// 状态文本映射
const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    active: '生效中',
    archived: '已归档'
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
    const res = await getVpps(params)
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
  searchForm.projectName = ''
  handleSearch()
}

// 表格变化
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchData()
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

// 筛选选项
const filterOption = (input, option) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

// 新增
const handleAdd = () => {
  selectedProjectId.value = null
  projectModalVisible.value = true
  loadProjects()
}

// 查看
const handleView = (record) => {
  router.push(`/vpp/detail/${record.id}`)
}

// 编辑
const handleEdit = (record) => {
  router.push(`/vpp/detail/${record.id}`)
}

// 项目选择确认
const handleProjectSelectOk = async () => {
  if (!selectedProjectId.value) {
    message.error('请选择项目')
    return
  }
  
  try {
    const res = await createVpp({ project: selectedProjectId.value })
    message.success('创建成功')
    projectModalVisible.value = false
    router.push(`/vpp/detail/${res.id}`)
  } catch (error) {
    message.error('创建失败')
  }
}

// 项目选择取消
const handleProjectSelectCancel = () => {
  projectModalVisible.value = false
}

onMounted(fetchData)
</script>

<style scoped>
.vpp-list {
  padding: 24px;
}

.search-form {
  margin-bottom: 24px;
}

.table-operations {
  margin-bottom: 16px;
}
</style>
