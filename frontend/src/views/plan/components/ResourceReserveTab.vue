<template>
  <div class="resource-reserve-tab">
    <!-- 查询区域 -->
    <a-form layout="inline" class="search-form">
      <a-form-item label="项目短码">
        <a-input
          v-model:value="searchForm.project_short_code"
          placeholder="请输入项目短码"
          allow-clear
        />
      </a-form-item>
      <a-form-item label="资源代码">
        <a-input
          v-model:value="searchForm.resource_code"
          placeholder="请输入资源代码"
          allow-clear
        />
      </a-form-item>
      <a-form-item label="预占状态">
        <a-select
          v-model:value="searchForm.reserve_status"
          placeholder="请选择状态"
          allow-clear
          style="width: 160px"
        >
          <a-select-option value="RESERVED">已预占</a-select-option>
          <a-select-option value="USED">已使用</a-select-option>
          <a-select-option value="RELEASED">已释放</a-select-option>
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
          新增
        </a-button>
      </a-form-item>
    </a-form>

    <!-- 表格区域 -->
    <a-table
      :columns="tableColumns"
      :data-source="tableData"
      :loading="loading"
      :pagination="pagination"
      row-key="reserve_id"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'resourceType'">
          <a-tag :color="getResourceTypeColor(record.resource_type)">
            {{ getResourceTypeText(record.resource_type) }}
          </a-tag>
        </template>
        <template v-if="column.key === 'status'">
          <a-tag :color="getStatusColor(record.reserve_status)">
            {{ getStatusText(record.reserve_status) }}
          </a-tag>
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="handleEdit(record)">
              编辑
            </a-button>
            <a-button type="link" danger size="small" @click="handleDelete(record)">
              删除
            </a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 新增/编辑弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
    >
      <a-form :model="formData" layout="vertical">
        <a-form-item label="项目" required>
          <a-select
            v-model:value="formData.projectId"
            placeholder="请选择项目"
            show-search
            :filter-option="filterProject"
          >
            <a-select-option
              v-for="proj in projectOptions"
              :key="proj.id"
              :value="proj.id"
            >
              {{ proj.code }} - {{ proj.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item :label="resourceTypeLabel" required>
          <a-select
            v-model:value="formData.resourceId"
            placeholder="请选择资源"
            show-search
            :filter-option="filterResource"
          >
            <a-select-option
              v-for="res in resourceOptions"
              :key="res.id"
              :value="res.id"
            >
              {{ res.code }} - {{ res.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="预占开始时间" required>
          <a-date-picker
            v-model:value="formData.reserveStart"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="预占结束时间" required>
          <a-date-picker
            v-model:value="formData.reserveEnd"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model:value="formData.remark" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { getResourceReserves, createResourceReserve, updateResourceReserve, deleteResourceReserve } from '@/api/plan'
import { getProjectList } from '@/api/project'

const props = defineProps({
  resourceType: {
    type: String,
    required: true
  },
  columns: {
    type: Array,
    required: true
  }
})

// 查询表单
const searchForm = reactive({
  project_short_code: '',
  resource_code: '',
  reserve_status: undefined
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
const modalTitle = ref('新增预占')
const isEdit = ref(false)
const currentId = ref(null)

const formData = reactive({
  projectId: undefined,
  resourceId: undefined,
  reserveStart: null,
  reserveEnd: null,
  remark: ''
})

// 选项数据
const projectOptions = ref([])
const resourceOptions = ref([])

// 表格列（添加操作列）
const tableColumns = computed(() => {
  return [...props.columns]
})

// 资源类型标签
const resourceTypeLabel = computed(() => {
  const labelMap = {
    platform: '台架',
    person: '人员',
    equipment: '设备'
  }
  return labelMap[props.resourceType] || '资源'
})

// 加载数据
const fetchData = async () => {
  loading.value = true
  try {
    // Map frontend resource type to backend format
    const resourceTypeMap = {
      platform: 'BENCH',
      person: 'PERSON',
      equipment: 'EQUIPMENT'
    }
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      resource_type: resourceTypeMap[props.resourceType],
      ...searchForm
    }
    const res = await getResourceReserves(params)
    tableData.value = res.data?.list || res.results || []
    pagination.total = res.data?.total || res.count || 0
  } catch (error) {
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 加载项目选项
const fetchProjects = async () => {
  try {
    const res = await getProjectList({ page_size: 1000 })
    projectOptions.value = res.data?.list || res.results || []
  } catch (error) {
    console.error('加载项目失败', error)
  }
}

// 查询
const handleSearch = () => {
  pagination.current = 1
  fetchData()
}

// 重置
const handleReset = () => {
  searchForm.project_short_code = ''
  searchForm.resource_code = ''
  searchForm.reserve_status = undefined
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
  modalTitle.value = '新增预占'
  currentId.value = null
  formData.projectId = undefined
  formData.resourceId = undefined
  formData.reserveStart = null
  formData.reserveEnd = null
  formData.remark = ''
  modalVisible.value = true
}

// 编辑
const handleEdit = (record) => {
  isEdit.value = true
  modalTitle.value = '编辑预占'
  currentId.value = record.reserve_id
  formData.projectId = record.project
  formData.resourceId = record.resource_code
  formData.reserveStart = record.reserve_start_time?.split(' ')[0]
  formData.reserveEnd = record.reserve_end_time?.split(' ')[0]
  formData.remark = record.remark || ''
  modalVisible.value = true
}

// 保存
const handleModalOk = async () => {
  try {
    const data = {
      ...formData,
      resourceType: props.resourceType
    }
    if (isEdit.value) {
      await updateResourceReserve(currentId.value, data)
      message.success('更新成功')
    } else {
      await createResourceReserve(data)
      message.success('新增成功')
    }
    modalVisible.value = false
    fetchData()
  } catch (error) {
    message.error(isEdit.value ? '更新失败' : '新增失败')
  }
}

const handleModalCancel = () => {
  modalVisible.value = false
}

// 删除
const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这条预占记录吗？',
    onOk: async () => {
      try {
        await deleteResourceReserve(record.reserve_id)
        message.success('删除成功')
        fetchData()
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}

// 筛选项目
const filterProject = (input, option) => {
  return option.children.toLowerCase().includes(input.toLowerCase())
}

// 筛选资源
const filterResource = (input, option) => {
  return option.children.toLowerCase().includes(input.toLowerCase())
}

// 资源类型颜色
const getResourceTypeColor = (type) => {
  const colorMap = {
    BENCH: 'orange',
    PERSON: 'blue',
    EQUIPMENT: 'green'
  }
  return colorMap[type] || 'default'
}

// 资源类型文本
const getResourceTypeText = (type) => {
  const textMap = {
    BENCH: '台架',
    PERSON: '人员',
    EQUIPMENT: '设备'
  }
  return textMap[type] || type
}

// 状态颜色
const getStatusColor = (status) => {
  const colorMap = {
    RESERVED: 'processing',
    USED: 'success',
    RELEASED: 'default'
  }
  return colorMap[status] || 'default'
}

// 状态文本
const getStatusText = (status) => {
  const textMap = {
    RESERVED: '已预占',
    USED: '已使用',
    RELEASED: '已释放'
  }
  return textMap[status] || status
}

onMounted(() => {
  fetchData()
  fetchProjects()
})
</script>

<style scoped>
.resource-reserve-tab {
  padding: 16px 0;
}

.search-form {
  margin-bottom: 16px;
}
</style>
