<template>
  <div class="scorecard-list">
    <a-card title="积分卡管理" :bordered="false">
      <!-- 查询区域 -->
      <a-form layout="inline" class="search-form">
        <a-form-item label="项目编码">
          <a-input
            v-model:value="searchForm.projectCode"
            placeholder="请输入项目编码"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="模板类型">
          <a-select
            v-model:value="searchForm.templateType"
            placeholder="请选择模板类型"
            allow-clear
            style="width: 120px"
          >
            <a-select-option value="L1">L1</a-select-option>
            <a-select-option value="L2">L2</a-select-option>
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
          <template v-if="column.key === 'templateType'">
            <a-tag :color="record.templateType === 'L1' ? 'blue' : 'green'">
              {{ record.templateType }}
            </a-tag>
          </template>
          <template v-if="column.key === 'phase'">
            {{ getPhaseText(record.phase) }}
          </template>
          <template v-if="column.key === 'totalScore'">
            <a-progress
              :percent="record.totalScore"
              :status="record.totalScore >= 80 ? 'success' : record.totalScore >= 60 ? 'normal' : 'exception'"
              size="small"
            />
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

    <!-- 新增弹窗 -->
    <a-modal
      v-model:open="addModalVisible"
      title="新增积分卡"
      @ok="handleAddOk"
      @cancel="handleAddCancel"
    >
      <a-form layout="vertical">
        <a-form-item label="项目" required>
          <a-select
            v-model:value="newScorecard.project"
            placeholder="请选择项目"
            show-search
            :filter-option="filterOption"
          >
            <a-select-option v-for="item in projectList" :key="item.id" :value="item.id">
              {{ item.code }} - {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="模板类型" required>
          <a-radio-group v-model:value="newScorecard.templateType">
            <a-radio value="L1">L1</a-radio>
            <a-radio value="L2">L2</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { getScorecards, createScorecard, deleteScorecard } from '@/api/auxiliary'
import { getProjects } from '@/api/project'

const router = useRouter()

// 查询表单
const searchForm = reactive({
  projectCode: '',
  templateType: undefined
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

// 新增弹窗
const addModalVisible = ref(false)
const projectList = ref([])
const newScorecard = reactive({
  project: undefined,
  templateType: 'L1'
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
    title: '项目名称',
    dataIndex: 'projectName',
    key: 'projectName',
    ellipsis: true
  },
  {
    title: '模板类型',
    dataIndex: 'templateType',
    key: 'templateType',
    width: 100
  },
  {
    title: '阶段',
    dataIndex: 'phase',
    key: 'phase',
    width: 120
  },
  {
    title: '总分',
    dataIndex: 'totalScore',
    key: 'totalScore',
    width: 150
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

// 阶段文本映射
const getPhaseText = (phase) => {
  const textMap = {
    phase1: '阶段1',
    phase2: '阶段2',
    phase3: '阶段3'
  }
  return textMap[phase] || phase
}

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
    const res = await getScorecards(params)
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
  searchForm.templateType = undefined
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
  newScorecard.project = undefined
  newScorecard.templateType = 'L1'
  addModalVisible.value = true
  loadProjects()
}

// 新增确认
const handleAddOk = async () => {
  if (!newScorecard.project) {
    message.error('请选择项目')
    return
  }
  
  try {
    const res = await createScorecard({
      project: newScorecard.project,
      templateType: newScorecard.templateType
    })
    message.success('创建成功')
    addModalVisible.value = false
    router.push(`/scorecard/edit/${res.id}`)
  } catch (error) {
    message.error('创建失败')
  }
}

// 新增取消
const handleAddCancel = () => {
  addModalVisible.value = false
}

// 编辑
const handleEdit = (record) => {
  router.push(`/scorecard/edit/${record.id}`)
}

// 删除
const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除积分卡吗？`,
    onOk: async () => {
      try {
        await deleteScorecard(record.id)
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
.scorecard-list {
  padding: 24px;
}

.search-form {
  margin-bottom: 24px;
}

.table-operations {
  margin-bottom: 16px;
}
</style>
