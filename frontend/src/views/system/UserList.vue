<template>
  <div>
    <div style="display:flex;justify-content:space-between;margin-bottom:16px">
      <h3 style="margin:0">用户管理</h3>
      <a-button type="primary" @click="showAdd">新增用户</a-button>
    </div>

    <a-table :dataSource="users" :columns="columns" rowKey="id" :loading="loading" :pagination="false">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'roles'">
          <a-select
            :value="record.roles"
            mode="multiple"
            style="width:320px"
            @change="(val) => handleRoleChange(record, val)"
          >
            <a-select-option v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</a-select-option>
          </a-select>
        </template>
        <template v-if="column.key === 'is_active'">
          <a-switch :checked="record.is_active" @change="(val) => handleToggleActive(record, val)" />
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="handleResetPwd(record)">重置密码</a>
            <a-popconfirm title="确定删除？" @confirm="handleDelete(record)">
              <a style="color:red">删除</a>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 新增用户弹窗 -->
    <a-modal v-model:open="addVisible" title="新增用户" @ok="handleAddOk" :confirmLoading="addLoading">
      <a-form layout="vertical">
        <a-form-item label="用户名" required>
          <a-input v-model:value="addForm.username" />
        </a-form-item>
        <a-form-item label="姓名">
          <a-input v-model:value="addForm.first_name" />
        </a-form-item>
        <a-form-item label="角色（可多选）">
          <a-select v-model:value="addForm.roles" mode="multiple" style="width:100%">
            <a-select-option v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="密码">
          <a-input-password v-model:value="addForm.password" placeholder="默认 hpm123456" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getUsers, createUser, updateUser, deleteUser, setUserRole, resetUserPassword, getRoles } from '@/api/auth'

const loading = ref(false)
const users = ref([])
const roles = ref([])
const addVisible = ref(false)
const addLoading = ref(false)
const addForm = ref({ username: '', first_name: '', roles: ['EXECUTOR'], password: '' })

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '姓名', dataIndex: 'first_name', key: 'first_name' },
  { title: '角色', key: 'roles', width: 360 },
  { title: '启用', key: 'is_active', width: 80 },
  { title: '操作', key: 'action', width: 160 },
]

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await getUsers()
    users.value = res.data?.list || res.data || []
  } finally {
    loading.value = false
  }
}

const fetchRoles = async () => {
  try {
    const res = await getRoles()
    roles.value = res.data || []
  } catch { roles.value = [] }
}

const handleRoleChange = async (record, roles) => {
  try {
    await setUserRole(record.id, roles)
    message.success('角色已更新')
    fetchUsers()
  } catch { /* */ }
}

const handleToggleActive = async (record, val) => {
  try {
    await updateUser(record.id, { is_active: val })
    message.success('状态已更新')
    fetchUsers()
  } catch { /* */ }
}

const handleResetPwd = async (record) => {
  try {
    await resetUserPassword(record.id, 'hpm123456')
    message.success(`已重置 ${record.username} 的密码为 hpm123456`)
  } catch { /* */ }
}

const handleDelete = async (record) => {
  try {
    await deleteUser(record.id)
    message.success('已删除')
    fetchUsers()
  } catch { /* */ }
}

const showAdd = () => {
  addForm.value = { username: '', first_name: '', roles: ['EXECUTOR'], password: '' }
  addVisible.value = true
}

const handleAddOk = async () => {
  if (!addForm.value.username) { message.warning('请输入用户名'); return }
  addLoading.value = true
  try {
    await createUser({
      username: addForm.value.username,
      first_name: addForm.value.first_name,
      last_name: addForm.value.roles.join(','),
      password: addForm.value.password || 'hpm123456',
      is_superuser: addForm.value.roles.includes('SUPER_ADMIN'),
    })
    message.success('用户已创建')
    addVisible.value = false
    fetchUsers()
  } catch { /* */ } finally {
    addLoading.value = false
  }
}

onMounted(() => { fetchUsers(); fetchRoles() })
</script>
