<template>
  <div style="padding:16px">
    <h3 style="margin-bottom:16px">计划/基线变更记录</h3>
    <a-form layout="inline" style="margin-bottom:16px">
      <a-form-item label="项目编码">
        <a-input v-model:value="filters.project_code" placeholder="请输入" allow-clear />
      </a-form-item>
      <a-form-item label="变更类型">
        <a-select v-model:value="filters.change_type" placeholder="请选择" allow-clear style="width:140px">
          <a-select-option value="PLAN">计划变更</a-select-option>
          <a-select-option value="BASELINE">基线变更</a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item label="操作人">
        <a-input v-model:value="filters.operator" placeholder="请输入" allow-clear />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" @click="handleSearch">查询</a-button>
        <a-button style="margin-left:8px" @click="handleReset">重置</a-button>
      </a-form-item>
    </a-form>

    <a-table
      :columns="columns"
      :dataSource="dataSource"
      :loading="loading"
      :pagination="pagination"
      rowKey="log_id"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'change_type'">
          <a-tag :color="record.change_type === 'BASELINE' ? 'orange' : 'blue'">
            {{ record.change_type_display || record.change_type }}
          </a-tag>
        </template>
        <template v-if="column.key === 'change_reason'">
          <a-tooltip :title="record.change_reason">
            <span style="display:inline-block;max-width:360px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;vertical-align:bottom">
              {{ record.change_reason }}
            </span>
          </a-tooltip>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getPlanChangeLogs } from '@/api/plan'

const loading = ref(false)
const dataSource = ref([])
const filters = reactive({ project_code: '', change_type: undefined, operator: '' })
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: total => `共 ${total} 条`
})

const columns = [
  { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '项目编码', dataIndex: 'project_code', key: 'project_code', width: 130 },
  { title: '项目名称', dataIndex: 'project_name', key: 'project_name', width: 200, ellipsis: true },
  { title: '变更类型', key: 'change_type', width: 110 },
  { title: '变更原因', key: 'change_reason' },
  { title: '影响任务数', dataIndex: 'affected_count', key: 'affected_count', width: 110, align: 'right' },
  { title: '操作人', dataIndex: 'operator', key: 'operator', width: 120 },
]

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      ...filters
    }
    const res = await getPlanChangeLogs(params)
    dataSource.value = res.data?.list || res.results || []
    pagination.total = res.data?.total || res.count || 0
  } catch {
    message.error('加载变更记录失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { pagination.current = 1; fetchData() }
const handleReset = () => {
  filters.project_code = ''
  filters.change_type = undefined
  filters.operator = ''
  handleSearch()
}
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchData()
}

onMounted(fetchData)
</script>

