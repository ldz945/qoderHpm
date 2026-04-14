<template>
  <div class="employee-list-container">
    <!-- 查询区域 -->
    <a-card class="search-card">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="员工工号">
          <a-input v-model:value="searchForm.employee_code" placeholder="请输入员工工号" allow-clear />
        </a-form-item>
        <a-form-item label="员工姓名">
          <a-input v-model:value="searchForm.employee_name" placeholder="请输入员工姓名" allow-clear />
        </a-form-item>
        <a-form-item label="部门">
          <a-input v-model:value="searchForm.department" placeholder="请输入部门" allow-clear />
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
        <PlusOutlined />新增员工
      </a-button>
    </div>

    <!-- 数据表格 -->
    <a-table
      :columns="columns"
      :data-source="dataSource"
      :loading="loading"
      :pagination="pagination"
      row-key="employee_id"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'is_external'">
          <a-tag :color="record.is_external === 'Y' ? 'orange' : 'green'">
            {{ record.is_external === 'Y' ? '是' : '否' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="handleEdit(record)">
              <EditOutlined />编辑
            </a-button>
            <a-popconfirm
              title="确定要删除该员工吗？"
              @confirm="handleDelete(record.employee_id)"
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
      :title="isEdit ? '编辑员工' : '新增员工'"
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
            <a-form-item label="员工工号" name="employee_code">
              <a-input v-model:value="editForm.employee_code" placeholder="请输入员工工号" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="员工全名" name="employee_name">
              <a-input v-model:value="editForm.employee_name" placeholder="请输入员工全名" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="部门" name="department">
              <a-input v-model:value="editForm.department" placeholder="请输入部门" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="邮箱" name="email">
              <a-input v-model:value="editForm.email" placeholder="请输入邮箱" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="来源" name="source">
              <a-input v-model:value="editForm.source" placeholder="请输入来源" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="是否外部" name="is_external">
              <a-select v-model:value="editForm.is_external" placeholder="请选择">
                <a-select-option value="Y">是</a-select-option>
                <a-select-option value="N">否</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="失效日期" name="expiry_date">
              <a-date-picker v-model:value="editForm.expiry_date" value-format="YYYY-MM-DD" style="width: 100%" />
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
import { getEmployees, createEmployee, updateEmployee, deleteEmployee } from '@/api/masterData'

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
  employee_code: '',
  employee_name: '',
  department: ''
})

const editForm = reactive({
  employee_id: null,
  employee_code: '',
  employee_name: '',
  department: '',
  email: '',
  source: '',
  is_external: 'N',
  expiry_date: null
})

const formRules = {
  employee_code: [{ required: true, message: '请输入员工工号', trigger: 'blur' }],
  employee_name: [{ required: true, message: '请输入员工全名', trigger: 'blur' }],
  department: [{ required: true, message: '请输入部门', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }]
}

const columns = [
  { title: '员工工号', dataIndex: 'employee_code', key: 'employee_code', width: 120 },
  { title: '员工全名', dataIndex: 'employee_name', key: 'employee_name', width: 120 },
  { title: '部门', dataIndex: 'department', key: 'department', width: 150 },
  { title: '邮箱', dataIndex: 'email', key: 'email', width: 200 },
  { title: '来源', dataIndex: 'source', key: 'source', width: 100 },
  { title: '是否外部', dataIndex: 'is_external', key: 'is_external', width: 100 },
  { title: '失效日期', dataIndex: 'expiry_date', key: 'expiry_date', width: 120 },
  { title: '操作', key: 'action', fixed: 'right', width: 150 }
]

const resetEditForm = () => {
  Object.assign(editForm, {
    employee_id: null,
    employee_code: '',
    employee_name: '',
    department: '',
    email: '',
    source: '',
    is_external: 'N',
    expiry_date: null
  })
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getEmployees({
      ...searchForm,
      page: pagination.current,
      page_size: pagination.pageSize
    })
    dataSource.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    message.error('获取员工列表失败')
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
  Object.assign(searchForm, { employee_code: '', employee_name: '', department: '' })
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
    await deleteEmployee(id)
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
      await updateEmployee(editForm.employee_id, editForm)
      message.success('编辑成功')
    } else {
      await createEmployee(editForm)
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
.employee-list-container {
  padding: 16px;
}

.search-card {
  margin-bottom: 16px;
}

.table-operations {
  margin-bottom: 16px;
}
</style>
