<template>
  <div class="action-item-list">
    <a-card title="行动项管理" :bordered="false">
      <!-- 查询区域 -->
      <a-form layout="inline" class="search-form">
        <a-form-item label="项目编码">
          <a-input
            v-model:value="searchForm.projectCode"
            placeholder="请输入项目编码"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="负责人">
          <a-select
            v-model:value="searchForm.responsible"
            placeholder="请选择负责人"
            allow-clear
            style="width: 140px"
            show-search
            :filter-option="filterOption"
          >
            <a-select-option v-for="item in employeeList" :key="item.id" :value="item.id">
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-select
            v-model:value="searchForm.status"
            placeholder="请选择状态"
            allow-clear
            style="width: 120px"
          >
            <a-select-option value="in_progress">进行中</a-select-option>
            <a-select-option value="cancelled">取消</a-select-option>
            <a-select-option value="completed">已完成</a-select-option>
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
        row-key="id"
        @change="handleTableChange"
        :row-class-name="getRowClassName"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'description'">
            <a-typography-text :ellipsis="{ rows: 2 }" :content="record.description" />
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status, record.isOverdue)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" @click="handleEdit(record)">编辑</a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 编辑弹窗 -->
    <a-modal
      v-model:open="editModalVisible"
      title="编辑行动项"
      @ok="handleEditOk"
      @cancel="handleEditCancel"
    >
      <a-form :model="editForm" layout="vertical">
        <a-form-item label="状态">
          <a-select v-model:value="editForm.status" placeholder="请选择状态">
            <a-select-option value="in_progress">进行中</a-select-option>
            <a-select-option value="cancelled">取消</a-select-option>
            <a-select-option value="completed">已完成</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="负责人">
          <a-select
            v-model:value="editForm.responsible"
            placeholder="请选择负责人"
            show-search
            :filter-option="filterOption"
          >
            <a-select-option v-for="item in employeeList" :key="item.id" :value="item.id">
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="实际完成时间">
          <a-date-picker v-model:value="editForm.actualCompleteDate" style="width: 100%" placeholder="请选择日期" />
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model:value="editForm.remark" :rows="3" placeholder="请输入备注" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { getActionItems, updateActionItem } from '@/api/auxiliary'
import { getEmployees } from '@/api/masterData'
import dayjs from 'dayjs'

// 查询表单
const searchForm = reactive({
  projectCode: '',
  responsible: undefined,
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

// 员工列表
const employeeList = ref([])

// 编辑弹窗
const editModalVisible = ref(false)
const editForm = reactive({
  id: null,
  status: '',
  responsible: undefined,
  actualCompleteDate: null,
  remark: ''
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
    title: '描述',
    dataIndex: 'description',
    key: 'description',
    ellipsis: true
  },
  {
    title: '记录人',
    dataIndex: 'recorderName',
    key: 'recorderName',
    width: 100
  },
  {
    title: '当前负责人',
    dataIndex: 'responsibleName',
    key: 'responsibleName',
    width: 100
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100
  },
  {
    title: '计划完成时间',
    dataIndex: 'planCompleteDate',
    key: 'planCompleteDate',
    width: 140
  },
  {
    title: '实际完成时间',
    dataIndex: 'actualCompleteDate',
    key: 'actualCompleteDate',
    width: 140
  },
  {
    title: '操作',
    key: 'action',
    width: 80,
    fixed: 'right'
  }
]

// 当前日期
const today = computed(() => dayjs().startOf('day'))

// 加载数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      ...searchForm
    }
    const res = await getActionItems(params)
    
    // 处理逾期判断
    tableData.value = (res.results || []).map(item => {
      const planDate = item.planCompleteDate ? dayjs(item.planCompleteDate) : null
      const isOverdue = item.status === 'in_progress' && planDate && planDate.isBefore(today.value)
      return {
        ...item,
        isOverdue
      }
    })
    
    pagination.total = res.count || 0
  } catch (error) {
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 状态颜色映射
const getStatusColor = (status, isOverdue) => {
  if (isOverdue) return 'error'
  const colorMap = {
    in_progress: 'processing',
    cancelled: 'default',
    completed: 'success'
  }
  return colorMap[status] || 'default'
}

// 状态文本映射
const getStatusText = (status) => {
  const textMap = {
    in_progress: '进行中',
    cancelled: '取消',
    completed: '已完成'
  }
  return textMap[status] || status
}

// 行样式 - 逾期标红
const getRowClassName = (record) => {
  return record.isOverdue ? 'overdue-row' : ''
}

// 加载员工列表
const loadEmployees = async () => {
  try {
    const res = await getEmployees({ page_size: 9999 })
    employeeList.value = res.results || []
  } catch (error) {
    console.error('加载员工失败', error)
  }
}

// 筛选选项
const filterOption = (input, option) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

// 查询
const handleSearch = () => {
  pagination.current = 1
  fetchData()
}

// 重置
const handleReset = () => {
  searchForm.projectCode = ''
  searchForm.responsible = undefined
  searchForm.status = undefined
  handleSearch()
}

// 表格变化
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchData()
}

// 编辑
const handleEdit = (record) => {
  editForm.id = record.id
  editForm.status = record.status
  editForm.responsible = record.responsible
  editForm.actualCompleteDate = record.actualCompleteDate ? dayjs(record.actualCompleteDate) : null
  editForm.remark = record.remark || ''
  editModalVisible.value = true
}

// 编辑确认
const handleEditOk = async () => {
  try {
    const submitData = {
      status: editForm.status,
      responsible: editForm.responsible,
      actualCompleteDate: editForm.actualCompleteDate ? dayjs(editForm.actualCompleteDate).format('YYYY-MM-DD') : null,
      remark: editForm.remark
    }
    await updateActionItem(editForm.id, submitData)
    message.success('更新成功')
    editModalVisible.value = false
    fetchData()
  } catch (error) {
    message.error('更新失败')
  }
}

// 编辑取消
const handleEditCancel = () => {
  editModalVisible.value = false
}

onMounted(() => {
  fetchData()
  loadEmployees()
})
</script>

<style scoped>
.action-item-list {
  padding: 24px;
}

.search-form {
  margin-bottom: 24px;
}

:deep(.overdue-row) {
  background-color: #fff1f0;
}

:deep(.overdue-row:hover) {
  background-color: #ffccc7;
}
</style>
