<template>
  <div class="department-list-container">
    <a-card class="search-card">
      <a-form layout="inline">
        <a-form-item label="部门名称">
          <a-input v-model:value="keyword" placeholder="请输入部门名称" allow-clear @pressEnter="fetchData" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="fetchData">查询</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <div class="table-operations">
      <a-space>
        <a-input v-model:value="newDepartment" placeholder="请输入部门名称" style="width: 260px" @pressEnter="handleCreate" />
        <a-button type="primary" :loading="submitting" @click="handleCreate">新增部门</a-button>
      </a-space>
    </div>

    <a-table
      :columns="columns"
      :data-source="dataSource"
      :loading="loading"
      row-key="category_id"
      :pagination="false"
      bordered
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'category_value'">
          <a-input v-model:value="record.category_value" size="small" />
        </template>
        <template v-else-if="column.key === 'enabled'">
          <a-switch :checked="record.enabled === 'Y'" @change="checked => (record.enabled = checked ? 'Y' : 'N')" />
        </template>
        <template v-else-if="column.key === 'sort_order'">
          <a-input-number v-model:value="record.sort_order" :min="0" size="small" style="width: 100%" />
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" :loading="submitting" @click="handleUpdate(record)">保存</a-button>
            <a-button type="link" danger size="small" :loading="submitting" @click="handleDelete(record)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { getTaskCategories, createTaskCategory, updateTaskCategory, deleteTaskCategory } from '@/api/plan'

const CATEGORY_TYPE = 'DEPARTMENT'

const loading = ref(false)
const submitting = ref(false)
const keyword = ref('')
const newDepartment = ref('')
const dataSource = ref([])

const columns = [
  { title: '部门名称', dataIndex: 'category_value', key: 'category_value' },
  { title: '启用', dataIndex: 'enabled', key: 'enabled', width: 90 },
  { title: '排序', dataIndex: 'sort_order', key: 'sort_order', width: 120 },
  { title: '操作', key: 'action', width: 160 }
]

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      category_type: CATEGORY_TYPE,
      page_size: 500,
      ordering: 'sort_order,category_id'
    }
    if (keyword.value.trim()) {
      params.search = keyword.value.trim()
    }
    const res = await getTaskCategories(params)
    dataSource.value = res.results || res.data?.list || res.data || []
  } catch (error) {
    message.error('加载部门列表失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  keyword.value = ''
  fetchData()
}

const handleCreate = async () => {
  const categoryValue = newDepartment.value.trim()
  if (!categoryValue) {
    message.warning('请输入部门名称')
    return
  }

  submitting.value = true
  try {
    await createTaskCategory({
      category_type: CATEGORY_TYPE,
      category_value: categoryValue,
      enabled: 'Y',
      sort_order: 0
    })
    newDepartment.value = ''
    await fetchData()
    message.success('新增部门成功')
  } catch (error) {
    message.error('新增失败，可能存在重复部门')
  } finally {
    submitting.value = false
  }
}

const handleUpdate = async (record) => {
  const categoryValue = String(record.category_value || '').trim()
  if (!categoryValue) {
    message.warning('部门名称不能为空')
    return
  }

  submitting.value = true
  try {
    await updateTaskCategory(record.category_id, {
      category_value: categoryValue,
      enabled: record.enabled === 'Y' ? 'Y' : 'N',
      sort_order: Number(record.sort_order || 0)
    })
    await fetchData()
    message.success('保存成功')
  } catch (error) {
    message.error('保存失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定删除部门“${record.category_value}”吗？`,
    onOk: async () => {
      submitting.value = true
      try {
        await deleteTaskCategory(record.category_id)
        await fetchData()
        message.success('删除成功')
      } catch (error) {
        message.error('删除失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(fetchData)
</script>

<style scoped>
.department-list-container {
  padding: 16px;
}

.search-card {
  margin-bottom: 16px;
}

.table-operations {
  margin-bottom: 16px;
}
</style>

