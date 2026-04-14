<template>
  <div class="resource-list-container">
    <!-- 查询区域 -->
    <a-card class="search-card">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="资源代码">
          <a-input v-model:value="searchForm.resource_code" placeholder="请输入资源代码" allow-clear />
        </a-form-item>
        <a-form-item label="资源名称">
          <a-input v-model:value="searchForm.resource_name" placeholder="请输入资源名称" allow-clear />
        </a-form-item>
        <a-form-item label="资源类型">
          <a-select v-model:value="searchForm.resource_type" placeholder="请选择资源类型" allow-clear style="width: 160px">
            <a-select-option value="LABOR">人工</a-select-option>
            <a-select-option value="LAB">实验室</a-select-option>
            <a-select-option value="TEST_ROOM">测试间</a-select-option>
            <a-select-option value="MISC">杂项</a-select-option>
          </a-select>
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
        <PlusOutlined />新增资源
      </a-button>
    </div>

    <!-- 数据表格 -->
    <a-table
      :columns="columns"
      :data-source="dataSource"
      :loading="loading"
      :pagination="pagination"
      row-key="resource_id"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'resource_type'">
          <a-tag>{{ getResourceTypeText(record.resource_type) }}</a-tag>
        </template>
        <template v-if="column.key === 'is_active'">
          <a-badge :status="record.is_active ? 'success' : 'default'" :text="record.is_active ? '启用' : '禁用'" />
        </template>
        <template v-if="column.key === 'charge_per_day'">
          {{ record.charge_per_day ? `¥${record.charge_per_day}` : '-' }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="handleEdit(record)">
              <EditOutlined />编辑
            </a-button>
            <a-popconfirm
              title="确定要删除该资源吗？"
              @confirm="handleDelete(record.resource_id)"
            >
              <a-button type="link" danger size="small">
                <DeleteOutlined />删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 新增/编辑弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑资源' : '新增资源'"
      :confirm-loading="submitLoading"
      @ok="handleSubmit"
      @cancel="handleCancel"
      width="700px"
    >
      <a-form
        ref="formRef"
        :model="editForm"
        :rules="formRules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="资源代码" name="resource_code">
              <a-input v-model:value="editForm.resource_code" placeholder="请输入资源代码" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="资源类型" name="resource_type">
              <a-select v-model:value="editForm.resource_type" placeholder="请选择资源类型">
                <a-select-option value="LABOR">人工</a-select-option>
                <a-select-option value="LAB">实验室</a-select-option>
                <a-select-option value="TEST_ROOM">测试间</a-select-option>
                <a-select-option value="MISC">杂项</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="资源名称" name="resource_name">
              <a-input v-model:value="editForm.resource_name" placeholder="请输入资源名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="资源短名" name="resource_short_name">
              <a-input v-model:value="editForm.resource_short_name" placeholder="请输入资源短名" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="资源负责人" name="resource_manager">
              <a-input v-model:value="editForm.resource_manager" placeholder="请输入资源负责人" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="是否启用" name="is_active">
              <a-switch v-model:checked="editForm.is_active" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="按天收费" name="charge_per_day">
              <a-input-number v-model:value="editForm.charge_per_day" :min="0" :precision="2" style="width: 100%" placeholder="请输入按天收费金额" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined, PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { getResources, createResource, updateResource, deleteResource } from '@/api/masterData'

const loading = ref(false)
const submitLoading = ref(false)
const dataSource = ref([])
const modalVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`
})

const searchForm = reactive({
  resource_code: '',
  resource_name: '',
  resource_type: undefined
})

const editForm = reactive({
  resource_id: null,
  resource_code: '',
  resource_type: undefined,
  resource_name: '',
  resource_short_name: '',
  resource_manager: '',
  is_active: true,
  charge_per_day: null
})

const formRules = {
  resource_code: [{ required: true, message: '请输入资源代码', trigger: 'blur' }],
  resource_type: [{ required: true, message: '请选择资源类型', trigger: 'change' }],
  resource_name: [{ required: true, message: '请输入资源名称', trigger: 'blur' }]
}

const resourceTypeMap = {
  'LABOR': '人工',
  'LAB': '实验室',
  'TEST_ROOM': '测试间',
  'MISC': '杂项'
}

const getResourceTypeText = (type) => {
  return resourceTypeMap[type] || type
}

const columns = [
  { title: '资源代码', dataIndex: 'resource_code', key: 'resource_code', width: 120 },
  { title: '资源类型', dataIndex: 'resource_type', key: 'resource_type', width: 100 },
  { title: '资源名称', dataIndex: 'resource_name', key: 'resource_name', width: 150 },
  { title: '资源短名', dataIndex: 'resource_short_name', key: 'resource_short_name', width: 120 },
  { title: '资源负责人', dataIndex: 'resource_manager', key: 'resource_manager', width: 120 },
  { title: '是否启用', dataIndex: 'is_active', key: 'is_active', width: 100 },
  { title: '按天收费', dataIndex: 'charge_per_day', key: 'charge_per_day', width: 120 },
  { title: '操作', key: 'action', fixed: 'right', width: 150 }
]

const resetEditForm = () => {
  Object.assign(editForm, {
    resource_id: null,
    resource_code: '',
    resource_type: undefined,
    resource_name: '',
    resource_short_name: '',
    resource_manager: '',
    is_active: true,
    charge_per_day: null
  })
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getResources({
      ...searchForm,
      page: pagination.current,
      page_size: pagination.pageSize
    })
    dataSource.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    message.error('获取资源列表失败')
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
  Object.assign(searchForm, { resource_code: '', resource_name: '', resource_type: undefined })
  handleSearch()
}

const handleAdd = () => {
  isEdit.value = false
  resetEditForm()
  modalVisible.value = true
}

const handleEdit = (record) => {
  isEdit.value = true
  Object.assign(editForm, record)
  modalVisible.value = true
}

const handleDelete = async (id) => {
  try {
    await deleteResource(id)
    message.success('删除成功')
    fetchData()
  } catch (error) {
    message.error('删除失败')
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    if (isEdit.value) {
      await updateResource(editForm.resource_id, editForm)
      message.success('编辑成功')
    } else {
      await createResource(editForm)
      message.success('新增成功')
    }
    
    modalVisible.value = false
    fetchData()
  } catch (error) {
    if (error.errorFields) return
    message.error(isEdit.value ? '编辑失败' : '新增失败')
  } finally {
    submitLoading.value = false
  }
}

const handleCancel = () => {
  modalVisible.value = false
  formRef.value?.resetFields()
}

onMounted(fetchData)
</script>

<style scoped>
.resource-list-container {
  padding: 16px;
}

.search-card {
  margin-bottom: 16px;
}

.table-operations {
  margin-bottom: 16px;
}
</style>
