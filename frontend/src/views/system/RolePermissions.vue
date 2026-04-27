<template>
  <div>
    <h3 style="margin-bottom:16px">角色权限说明</h3>
    <a-collapse v-model:activeKey="activeKeys">
      <a-collapse-panel v-for="role in roles" :key="role.key" :header="role.label">
        <p style="color:#666;margin-bottom:12px">{{ role.description }}</p>
        <a-table
          :dataSource="role.permissions"
          :columns="permColumns"
          :pagination="false"
          size="small"
          rowKey="module"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'actions'">
              <a-tag v-for="a in record.actions" :key="a" :color="actionColor(a)">{{ a }}</a-tag>
            </template>
          </template>
        </a-table>
      </a-collapse-panel>
    </a-collapse>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeKeys = ref(['SUPER_ADMIN'])

const permColumns = [
  { title: '功能模块', dataIndex: 'module', key: 'module', width: 200 },
  { title: '权限', key: 'actions' },
]

const actionColor = (a) => {
  if (a.includes('写') || a.includes('创建') || a.includes('删除')) return 'red'
  if (a.includes('读') || a.includes('查看')) return 'blue'
  if (a.includes('更新') || a.includes('编辑')) return 'orange'
  return 'default'
}

const roles = [
  {
    key: 'SUPER_ADMIN', label: '超级管理员',
    description: '拥有系统所有功能的完整权限，包括用户管理、角色分配等系统级操作。',
    permissions: [
      { module: '所有模块', actions: ['完整读写权限'] },
      { module: '系统管理', actions: ['用户管理', '角色分配', '重置密码'] },
    ]
  },
  {
    key: 'MD_ADMIN', label: '主数据管理员',
    description: '负责维护系统基础数据，包括人员、部门、资源和价格信息。',
    permissions: [
      { module: '人员维护', actions: ['查看', '创建', '编辑', '删除'] },
      { module: '部门维护', actions: ['查看', '创建', '编辑', '删除'] },
      { module: '资源管理', actions: ['查看', '创建', '编辑', '删除'] },
      { module: '价格管理', actions: ['查看', '创建', '编辑', '删除'] },
    ]
  },
  {
    key: 'PMO', label: 'PMO（项目管理办公室）',
    description: '负责项目全生命周期管理，可创建项目、编辑计划、查看执行情况和工时数据；可调整项目经理。',
    permissions: [
      { module: '项目管理', actions: ['查看', '创建', '编辑', '状态更新', '修改项目经理'] },
      { module: '计划管理', actions: ['查看', '创建/编辑任务', '批量更新', '版本读写'] },
      { module: '项目执行', actions: ['查看', '执行详情', '工时查看'] },
    ]
  },
  {
    key: 'PROJECT_MANAGER', label: '项目经理',
    description: '只能管理自己负责的项目（数据隔离）；可创建项目、编辑计划、查看执行进度；不能修改自己项目的项目经理。',
    permissions: [
      { module: '项目管理', actions: ['查看(仅自己的项目)', '创建', '编辑', '状态更新'] },
      { module: '计划管理', actions: ['查看', '创建/编辑任务', '批量更新', '版本读写'] },
      { module: '项目执行', actions: ['查看', '执行详情'] },
    ]
  },
  {
    key: 'PLAN_ENGINEER', label: '计划工程师',
    description: '专注于项目计划的制定和维护，可编辑任务和查看相关主数据。',
    permissions: [
      { module: '计划管理', actions: ['查看', '创建/编辑任务', '批量更新'] },
      { module: '计划版本', actions: ['查看'] },
      { module: '主数据（只读）', actions: ['查看部门', '查看人员'] },
    ]
  },
  {
    key: 'EXECUTOR', label: '执行人',
    description: '负责执行具体任务，可更新任务进度和查看工时。',
    permissions: [
      { module: '项目执行', actions: ['查看', '执行详情', '更新进度', '工时查看'] },
      { module: '主数据（只读）', actions: ['查看部门', '查看人员'] },
    ]
  },
  {
    key: 'AUDITOR', label: '审计 / 只读',
    description: '拥有全系统只读权限，用于审计和监督，不能做任何修改操作。',
    permissions: [
      { module: '项目管理', actions: ['查看'] },
      { module: '计划管理', actions: ['查看任务', '查看版本'] },
      { module: '项目执行', actions: ['查看', '执行详情'] },
      { module: '主数据', actions: ['查看人员', '查看部门', '查看资源', '查看价格'] },
    ]
  },
]
</script>

