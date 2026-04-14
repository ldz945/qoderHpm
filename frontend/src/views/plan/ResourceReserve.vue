<template>
  <div class="resource-reserve">
    <a-card title="资源预占管理" :bordered="false">
      <a-tabs v-model:activeKey="activeTab">
        <!-- 台架预占 -->
        <a-tab-pane key="platform" tab="台架预占">
          <ResourceReserveTab
            resource-type="platform"
            :columns="platformColumns"
          />
        </a-tab-pane>

        <!-- 人员预占 -->
        <a-tab-pane key="person" tab="人员预占">
          <ResourceReserveTab
            resource-type="person"
            :columns="personColumns"
          />
        </a-tab-pane>

        <!-- 设备预占 -->
        <a-tab-pane key="equipment" tab="设备预占">
          <ResourceReserveTab
            resource-type="equipment"
            :columns="equipmentColumns"
          />
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </div>
</template>

<script setup>
import { ref, h } from 'vue'
import ResourceReserveTab from './components/ResourceReserveTab.vue'

const activeTab = ref('platform')

// 台架列定义
const platformColumns = [
  { title: '项目短码', dataIndex: 'project_short_code', key: 'project_short_code', width: 120 },
  { title: '资源类型', dataIndex: 'resource_type', key: 'resourceType', width: 100 },
  { title: '台架编号', dataIndex: 'resource_code', key: 'resource_code', width: 120 },
  { title: '台架名称', dataIndex: 'resource_name', key: 'resource_name', width: 150 },
  { title: '预占开始', dataIndex: 'reserve_start_time', key: 'reserve_start_time', width: 150 },
  { title: '预占结束', dataIndex: 'reserve_end_time', key: 'reserve_end_time', width: 150 },
  { title: '状态', dataIndex: 'reserve_status', key: 'status', width: 100 },
  { title: '操作', key: 'action', width: 150, fixed: 'right' }
]

// 人员列定义
const personColumns = [
  { title: '项目短码', dataIndex: 'project_short_code', key: 'project_short_code', width: 120 },
  { title: '资源类型', dataIndex: 'resource_type', key: 'resourceType', width: 100 },
  { title: '人员编码', dataIndex: 'resource_code', key: 'resource_code', width: 120 },
  { title: '人员姓名', dataIndex: 'resource_name', key: 'resource_name', width: 120 },
  { title: '预占开始', dataIndex: 'reserve_start_time', key: 'reserve_start_time', width: 150 },
  { title: '预占结束', dataIndex: 'reserve_end_time', key: 'reserve_end_time', width: 150 },
  { title: '状态', dataIndex: 'reserve_status', key: 'status', width: 100 },
  { title: '操作', key: 'action', width: 150, fixed: 'right' }
]

// 设备列定义
const equipmentColumns = [
  { title: '项目短码', dataIndex: 'project_short_code', key: 'project_short_code', width: 120 },
  { title: '资源类型', dataIndex: 'resource_type', key: 'resourceType', width: 100 },
  { title: '设备编码', dataIndex: 'resource_code', key: 'resource_code', width: 120 },
  { title: '设备名称', dataIndex: 'resource_name', key: 'resource_name', width: 150 },
  { title: '预占开始', dataIndex: 'reserve_start_time', key: 'reserve_start_time', width: 150 },
  { title: '预占结束', dataIndex: 'reserve_end_time', key: 'reserve_end_time', width: 150 },
  { title: '状态', dataIndex: 'reserve_status', key: 'status', width: 100 },
  { title: '操作', key: 'action', width: 150, fixed: 'right' }
]
</script>

<style scoped>
.resource-reserve {
  padding: 24px;
}
</style>
