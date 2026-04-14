<template>
  <div class="price-list-container">
    <a-tabs v-model:activeKey="activeTab" @change="handleTabChange">
      <!-- Tab1: 价格版本 -->
      <a-tab-pane key="header" tab="价格版本">
        <div class="tab-content">
          <div class="table-operations">
            <a-button type="primary" @click="handleAddHeader">
              <PlusOutlined />新增版本
            </a-button>
          </div>
          <a-table
            :columns="headerColumns"
            :data-source="headerDataSource"
            :loading="headerLoading"
            :pagination="headerPagination"
            row-key="price_header_id"
            @change="handleHeaderTableChange"
            @row-click="handleHeaderRowClick"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag :color="getStatusColor(record.status)">
                  {{ getStatusText(record.status) }}
                </a-tag>
              </template>
              <template v-if="column.key === 'action'">
                <a-space>
                  <a-button type="link" size="small" @click.stop="handleEditHeader(record)">
                    <EditOutlined />编辑
                  </a-button>
                  <a-popconfirm
                    title="确定要删除该价格版本吗？"
                    @confirm.stop="handleDeleteHeader(record.price_header_id)"
                  >
                    <a-button type="link" danger size="small" @click.stop>
                      <DeleteOutlined />删除
                    </a-button>
                  </a-popconfirm>
                </a-space>
              </template>
            </template>
          </a-table>
        </div>
      </a-tab-pane>

      <!-- Tab2: 价格明细 -->
      <a-tab-pane key="line" tab="价格明细">
        <div class="tab-content">
          <a-card class="select-header-card" size="small">
            <a-space>
              <span>选择价格版本:</span>
              <a-select
                v-model:value="selectedHeaderId"
                placeholder="请选择价格版本"
                style="width: 300px"
                @change="handleHeaderSelect"
              >
                <a-select-option
                  v-for="header in headerOptions"
                  :key="header.price_header_id"
                  :value="header.price_header_id"
                >
                  {{ header.version_name }} ({{ header.version_number }})
                </a-select-option>
              </a-select>
              <a-button type="primary" :disabled="!selectedHeaderId" @click="handleAddLine">
                <PlusOutlined />新增明细
              </a-button>
            </a-space>
          </a-card>
          <a-table
            :columns="lineColumns"
            :data-source="lineDataSource"
            :loading="lineLoading"
            :pagination="linePagination"
            row-key="price_line_id"
            @change="handleLineTableChange"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'price'">
                {{ record.price }} {{ record.currency }}
              </template>
              <template v-if="column.key === 'action'">
                <a-space>
                  <a-button type="link" size="small" @click="handleEditLine(record)">
                    <EditOutlined />编辑
                  </a-button>
                  <a-popconfirm
                    title="确定要删除该价格明细吗？"
                    @confirm="handleDeleteLine(record.price_line_id)"
                  >
                    <a-button type="link" danger size="small">
                      <DeleteOutlined />删除
                    </a-button>
                  </a-popconfirm>
                </a-space>
              </template>
            </template>
          </a-table>
        </div>
      </a-tab-pane>
    </a-tabs>

    <!-- 新增/编辑价格版本弹窗 -->
    <a-modal
      v-model:open="headerModalVisible"
      :title="isEditHeader ? '编辑价格版本' : '新增价格版本'"
      :confirm-loading="headerSubmitLoading"
      @ok="handleSubmitHeader"
      @cancel="handleCancelHeader"
      width="700px"
    >
      <a-form
        ref="headerFormRef"
        :model="headerForm"
        :rules="headerFormRules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="版本名" name="version_name">
              <a-input v-model:value="headerForm.version_name" placeholder="请输入版本名" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="版本号" name="version_number">
              <a-input v-model:value="headerForm.version_number" placeholder="请输入版本号" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="货币" name="currency">
              <a-select v-model:value="headerForm.currency" placeholder="请选择货币">
                <a-select-option value="CNY">人民币 (CNY)</a-select-option>
                <a-select-option value="USD">美元 (USD)</a-select-option>
                <a-select-option value="EUR">欧元 (EUR)</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="状态" name="status">
              <a-select v-model:value="headerForm.status" placeholder="请选择状态">
                <a-select-option value="DRAFT">草稿</a-select-option>
                <a-select-option value="ACTIVE">生效中</a-select-option>
                <a-select-option value="EXPIRED">已过期</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="生效日期" name="effective_date">
              <a-date-picker v-model:value="headerForm.effective_date" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="失效日期" name="expiration_date">
              <a-date-picker v-model:value="headerForm.expiration_date" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 新增/编辑价格明细弹窗 -->
    <a-modal
      v-model:open="lineModalVisible"
      :title="isEditLine ? '编辑价格明细' : '新增价格明细'"
      :confirm-loading="lineSubmitLoading"
      @ok="handleSubmitLine"
      @cancel="handleCancelLine"
      width="600px"
    >
      <a-form
        ref="lineFormRef"
        :model="lineForm"
        :rules="lineFormRules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="价格版本" name="price_header_id">
          <a-select v-model:value="lineForm.price_header_id" placeholder="请选择价格版本" disabled>
            <a-select-option
              v-for="header in headerOptions"
              :key="header.price_header_id"
              :value="header.price_header_id"
            >
              {{ header.version_name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="资源类型" name="resource_type">
          <a-select v-model:value="lineForm.resource_type" placeholder="请选择资源类型">
            <a-select-option value="LABOR">人工</a-select-option>
            <a-select-option value="LAB">实验室</a-select-option>
            <a-select-option value="TEST_ROOM">测试间</a-select-option>
            <a-select-option value="MISC">杂项</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="资源代码" name="resource_code">
          <a-input v-model:value="lineForm.resource_code" placeholder="请输入资源代码" />
        </a-form-item>
        <a-form-item label="价格" name="price">
          <a-input-number v-model:value="lineForm.price" :min="0" :precision="2" style="width: 100%" placeholder="请输入价格" />
        </a-form-item>
        <a-form-item label="单位" name="unit">
          <a-input v-model:value="lineForm.unit" placeholder="请输入单位，如：天、小时" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import {
  getPriceHeaders,
  createPriceHeader,
  updatePriceHeader,
  deletePriceHeader,
  getPriceLines,
  createPriceLine,
  updatePriceLine,
  deletePriceLine
} from '@/api/masterData'

const activeTab = ref('header')

// ===== 价格版本相关 =====
const headerLoading = ref(false)
const headerSubmitLoading = ref(false)
const headerDataSource = ref([])
const headerOptions = ref([])
const headerModalVisible = ref(false)
const isEditHeader = ref(false)
const headerFormRef = ref(null)

const headerPagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`
})

const headerForm = reactive({
  price_header_id: null,
  version_name: '',
  version_number: '',
  currency: 'CNY',
  status: 'DRAFT',
  effective_date: null,
  expiration_date: null
})

const headerFormRules = {
  version_name: [{ required: true, message: '请输入版本名', trigger: 'blur' }],
  version_number: [{ required: true, message: '请输入版本号', trigger: 'blur' }],
  currency: [{ required: true, message: '请选择货币', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const statusMap = {
  'DRAFT': { text: '草稿', color: 'default' },
  'ACTIVE': { text: '生效中', color: 'green' },
  'EXPIRED': { text: '已过期', color: 'red' }
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusColor = (status) => statusMap[status]?.color || 'default'

const headerColumns = [
  { title: '版本名', dataIndex: 'version_name', key: 'version_name', width: 150 },
  { title: '版本号', dataIndex: 'version_number', key: 'version_number', width: 120 },
  { title: '货币', dataIndex: 'currency', key: 'currency', width: 100 },
  { title: '生效日期', dataIndex: 'effective_date', key: 'effective_date', width: 120 },
  { title: '失效日期', dataIndex: 'expiration_date', key: 'expiration_date', width: 120 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '操作', key: 'action', fixed: 'right', width: 150 }
]

const resetHeaderForm = () => {
  Object.assign(headerForm, {
    price_header_id: null,
    version_name: '',
    version_number: '',
    currency: 'CNY',
    status: 'DRAFT',
    effective_date: null,
    expiration_date: null
  })
}

const fetchHeaderData = async () => {
  headerLoading.value = true
  try {
    const res = await getPriceHeaders({
      page: headerPagination.current,
      page_size: headerPagination.pageSize
    })
    headerDataSource.value = res.results || []
    headerOptions.value = res.results || []
    headerPagination.total = res.count || 0
  } catch (error) {
    message.error('获取价格版本列表失败')
  } finally {
    headerLoading.value = false
  }
}

const handleHeaderTableChange = (pag) => {
  headerPagination.current = pag.current
  headerPagination.pageSize = pag.pageSize
  fetchHeaderData()
}

const handleAddHeader = () => {
  isEditHeader.value = false
  resetHeaderForm()
  headerModalVisible.value = true
}

const handleEditHeader = (record) => {
  isEditHeader.value = true
  Object.assign(headerForm, record)
  headerModalVisible.value = true
}

const handleDeleteHeader = async (id) => {
  try {
    await deletePriceHeader(id)
    message.success('删除成功')
    fetchHeaderData()
  } catch (error) {
    message.error('删除失败')
  }
}

const handleSubmitHeader = async () => {
  try {
    await headerFormRef.value.validate()
    headerSubmitLoading.value = true
    
    if (isEditHeader.value) {
      await updatePriceHeader(headerForm.price_header_id, headerForm)
      message.success('编辑成功')
    } else {
      await createPriceHeader(headerForm)
      message.success('新增成功')
    }
    
    headerModalVisible.value = false
    fetchHeaderData()
  } catch (error) {
    if (error.errorFields) return
    message.error(isEditHeader.value ? '编辑失败' : '新增失败')
  } finally {
    headerSubmitLoading.value = false
  }
}

const handleCancelHeader = () => {
  headerModalVisible.value = false
  headerFormRef.value?.resetFields()
}

// ===== 价格明细相关 =====
const lineLoading = ref(false)
const lineSubmitLoading = ref(false)
const lineDataSource = ref([])
const selectedHeaderId = ref(null)
const lineModalVisible = ref(false)
const isEditLine = ref(false)
const lineFormRef = ref(null)

const linePagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`
})

const lineForm = reactive({
  price_line_id: null,
  price_header_id: null,
  resource_type: undefined,
  resource_code: '',
  price: null,
  unit: ''
})

const lineFormRules = {
  price_header_id: [{ required: true, message: '请选择价格版本', trigger: 'change' }],
  resource_type: [{ required: true, message: '请选择资源类型', trigger: 'change' }],
  resource_code: [{ required: true, message: '请输入资源代码', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }]
}

const lineColumns = [
  { title: '资源类型', dataIndex: 'resource_type', key: 'resource_type', width: 120 },
  { title: '资源代码', dataIndex: 'resource_code', key: 'resource_code', width: 150 },
  { title: '价格', dataIndex: 'price', key: 'price', width: 150 },
  { title: '单位', dataIndex: 'unit', key: 'unit', width: 100 },
  { title: '操作', key: 'action', fixed: 'right', width: 150 }
]

const resetLineForm = () => {
  Object.assign(lineForm, {
    price_line_id: null,
    price_header_id: selectedHeaderId.value,
    resource_type: undefined,
    resource_code: '',
    price: null,
    unit: ''
  })
}

const fetchLineData = async () => {
  if (!selectedHeaderId.value) {
    lineDataSource.value = []
    return
  }
  lineLoading.value = true
  try {
    const res = await getPriceLines({
      price_header_id: selectedHeaderId.value,
      page: linePagination.current,
      page_size: linePagination.pageSize
    })
    lineDataSource.value = res.results || []
    linePagination.total = res.count || 0
  } catch (error) {
    message.error('获取价格明细列表失败')
  } finally {
    lineLoading.value = false
  }
}

const handleLineTableChange = (pag) => {
  linePagination.current = pag.current
  linePagination.pageSize = pag.pageSize
  fetchLineData()
}

const handleHeaderSelect = () => {
  linePagination.current = 1
  fetchLineData()
}

const handleHeaderRowClick = (record) => {
  activeTab.value = 'line'
  selectedHeaderId.value = record.price_header_id
  linePagination.current = 1
  fetchLineData()
}

const handleAddLine = () => {
  isEditLine.value = false
  resetLineForm()
  lineModalVisible.value = true
}

const handleEditLine = (record) => {
  isEditLine.value = true
  Object.assign(lineForm, record)
  lineModalVisible.value = true
}

const handleDeleteLine = async (id) => {
  try {
    await deletePriceLine(id)
    message.success('删除成功')
    fetchLineData()
  } catch (error) {
    message.error('删除失败')
  }
}

const handleSubmitLine = async () => {
  try {
    await lineFormRef.value.validate()
    lineSubmitLoading.value = true
    
    if (isEditLine.value) {
      await updatePriceLine(lineForm.price_line_id, lineForm)
      message.success('编辑成功')
    } else {
      await createPriceLine(lineForm)
      message.success('新增成功')
    }
    
    lineModalVisible.value = false
    fetchLineData()
  } catch (error) {
    if (error.errorFields) return
    message.error(isEditLine.value ? '编辑失败' : '新增失败')
  } finally {
    lineSubmitLoading.value = false
  }
}

const handleCancelLine = () => {
  lineModalVisible.value = false
  lineFormRef.value?.resetFields()
}

const handleTabChange = () => {
  if (activeTab.value === 'header') {
    fetchHeaderData()
  } else {
    fetchLineData()
  }
}

onMounted(() => {
  fetchHeaderData()
})
</script>

<style scoped>
.price-list-container {
  padding: 16px;
}

.tab-content {
  padding-top: 16px;
}

.table-operations {
  margin-bottom: 16px;
}

.select-header-card {
  margin-bottom: 16px;
}
</style>
