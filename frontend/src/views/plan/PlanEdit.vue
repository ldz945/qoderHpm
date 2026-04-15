<template>
  <div class="plan-edit">
    <!-- 顶部页头 -->
    <a-page-header
      :title="`${projectInfo.code} - ${projectInfo.name}`"
      sub-title="计划编辑"
      @back="handleBack"
    >
      <template #extra>
        <a-button @click="handleImport">导入</a-button>
        <a-button @click="handleTbqImport">TBQ导入</a-button>
        <a-button type="primary" @click="handleSave">保存</a-button>
        <a-button type="primary" danger @click="handleSubmit">提交审批</a-button>
      </template>
    </a-page-header>

    <!-- 主体区域 -->
    <a-tabs v-model:activeKey="activeTab" class="plan-tabs">
      <!-- Tab1: 任务计划 -->
      <a-tab-pane key="tasks" tab="任务计划">
        <a-table
          :columns="taskColumns"
          :data-source="planTasks"
          :loading="loading"
          row-key="id"
          :pagination="false"
          children-column-name="children"
          :default-expand-all-rows="true"
        >
          <template #bodyCell="{ column, record, index }">
            <!-- 层级编码 -->
            <template v-if="column.key === 'wbsCode'">
              <span>{{ record.wbsCode }}</span>
            </template>

            <!-- 任务名称 - 可编辑 -->
            <template v-if="column.key === 'name'">
              <a-input
                v-if="record.editing"
                v-model:value="record.name"
                size="small"
              />
              <span v-else>{{ record.name }}</span>
            </template>

            <!-- 阶段 -->
            <template v-if="column.key === 'phase'">
              <a-select
                v-if="record.editing"
                v-model:value="record.phase"
                size="small"
                style="width: 100px"
              >
                <a-select-option value="init">立项</a-select-option>
                <a-select-option value="design">设计</a-select-option>
                <a-select-option value="development">开发</a-select-option>
                <a-select-option value="test">测试</a-select-option>
                <a-select-option value="delivery">交付</a-select-option>
              </a-select>
              <span v-else>{{ getPhaseText(record.phase) }}</span>
            </template>

            <!-- 部门 -->
            <template v-if="column.key === 'department'">
              <a-input
                v-if="record.editing"
                v-model:value="record.department"
                size="small"
              />
              <span v-else>{{ record.department }}</span>
            </template>

            <!-- 任务负责人 -->
            <template v-if="column.key === 'owner'">
              <a-input
                v-if="record.editing"
                v-model:value="record.owner"
                size="small"
              />
              <span v-else>{{ record.owner }}</span>
            </template>

            <!-- 被授权人 -->
            <template v-if="column.key === 'delegate'">
              <a-input
                v-if="record.editing"
                v-model:value="record.delegate"
                size="small"
              />
              <span v-else>{{ record.delegate }}</span>
            </template>

            <!-- 逻辑关系 -->
            <template v-if="column.key === 'logicRelation'">
              <a-select
                v-if="record.editing"
                v-model:value="record.logicRelation"
                size="small"
                style="width: 80px"
              >
                <a-select-option value="FS">FS</a-select-option>
                <a-select-option value="SF">SF</a-select-option>
                <a-select-option value="FF">FF</a-select-option>
                <a-select-option value="SS">SS</a-select-option>
              </a-select>
              <span v-else>{{ record.logicRelation }}</span>
            </template>

            <!-- 紧前任务 -->
            <template v-if="column.key === 'preTask'">
              <a-input
                v-if="record.editing"
                v-model:value="record.preTask"
                size="small"
              />
              <span v-else>{{ record.preTask }}</span>
            </template>

            <!-- 计划开始 -->
            <template v-if="column.key === 'planStart'">
              <a-date-picker
                v-if="record.editing"
                v-model:value="record.planStart"
                size="small"
                value-format="YYYY-MM-DD"
              />
              <span v-else>{{ record.planStart }}</span>
            </template>

            <!-- 计划结束 -->
            <template v-if="column.key === 'planEnd'">
              <a-date-picker
                v-if="record.editing"
                v-model:value="record.planEnd"
                size="small"
                value-format="YYYY-MM-DD"
              />
              <span v-else>{{ record.planEnd }}</span>
            </template>

            <!-- 工作量 -->
            <template v-if="column.key === 'workload'">
              <a-input-number
                v-if="record.editing"
                v-model:value="record.workload"
                size="small"
                :min="0"
                style="width: 70px"
              />
              <span v-else>{{ record.workload }}天</span>
            </template>

            <!-- 进度 -->
            <template v-if="column.key === 'progress'">
              <a-input-number
                v-if="record.editing"
                v-model:value="record.progress"
                size="small"
                :min="0"
                :max="100"
                style="width: 70px"
              />
              <span v-else>{{ record.progress }}%</span>
            </template>

            <!-- 工时任务 -->
            <template v-if="column.key === 'isWorkHourTask'">
              <a-checkbox v-model:checked="record.isWorkHourTask" :disabled="!record.editing" />
            </template>

            <!-- 交付物 -->
            <template v-if="column.key === 'hasDeliverable'">
              <a-checkbox v-model:checked="record.hasDeliverable" :disabled="!record.editing" />
            </template>

            <!-- 状态 -->
            <template v-if="column.key === 'status'">
              <a-tag :color="getStatusColor(record.status)">
                {{ getStatusText(record.status) }}
              </a-tag>
            </template>

            <!-- 操作 -->
            <template v-if="column.key === 'action'">
              <a-space>
                <a-button type="link" size="small" @click="handleAddChild(record)">
                  向下添加
                </a-button>
                <a-button type="link" size="small" @click="handleAddSibling(record)">
                  平级添加
                </a-button>
                <a-button
                  v-if="record.status === 'draft'"
                  type="link"
                  danger
                  size="small"
                  @click="handleDelete(record)"
                >
                  删除
                </a-button>
                <a-button
                  v-if="record.editing"
                  type="link"
                  size="small"
                  @click="handleSaveTask(record)"
                >
                  保存
                </a-button>
                <a-button
                  v-else
                  type="link"
                  size="small"
                  @click="handleEditTask(record)"
                >
                  编辑
                </a-button>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-tab-pane>

      <!-- Tab2: 甘特图 -->
      <a-tab-pane key="gantt" tab="甘特图">
        <div class="gantt-tab-content">
          <GanttChart
            ref="ganttRef"
            :tasks="planTasks"
            :flat-tasks="flatTasks"
            :project-id="projectId"
            :active="activeTab === 'gantt'"
            :on-save="handleGanttSave"
            @save="handleGanttSave"
          />
        </div>
      </a-tab-pane>

      <!-- Tab3: 资源计划 -->
      <a-tab-pane key="resources" tab="资源计划">
        <a-row :gutter="16">
          <a-col :span="8">
            <a-card title="选择任务" size="small">
              <a-tree
                :tree-data="taskTreeData"
                :field-names="{ title: 'name', key: 'id', children: 'children' }"
                @select="handleTaskSelect"
              />
            </a-card>
          </a-col>
          <a-col :span="16">
            <a-card
              :title="`资源计划 - ${selectedTask?.name || '请选择任务'}`"
              size="small"
            >
              <template #extra>
                <a-button type="primary" size="small" @click="handleAddResource">
                  新增资源
                </a-button>
              </template>
              <a-table
                :columns="resourceColumns"
                :data-source="resources"
                :loading="resourceLoading"
                row-key="id"
                size="small"
                :pagination="false"
              >
                <template #bodyCell="{ column, record }">
                  <template v-if="column.key === 'resourceType'">
                    <a-tag :color="record.resourceType === 'person' ? 'blue' : record.resourceType === 'equipment' ? 'green' : 'orange'">
                      {{ getResourceTypeText(record.resourceType) }}
                    </a-tag>
                  </template>
                  <template v-if="column.key === 'weekend'">
                    <a-checkbox v-model:checked="record.weekend" disabled />
                  </template>
                  <template v-if="column.key === 'status'">
                    <a-tag :color="getStatusColor(record.status)">
                      {{ getStatusText(record.status) }}
                    </a-tag>
                  </template>
                  <template v-if="column.key === 'action'">
                    <a-button type="link" danger size="small" @click="handleDeleteResource(record)">
                      删除
                    </a-button>
                  </template>
                </template>
              </a-table>
            </a-card>
          </a-col>
        </a-row>
      </a-tab-pane>
    </a-tabs>

    <!-- 新增资源弹窗 -->
    <a-modal
      v-model:open="resourceModalVisible"
      title="新增资源"
      @ok="handleResourceModalOk"
      @cancel="handleResourceModalCancel"
    >
      <a-form :model="resourceForm" layout="vertical">
        <a-form-item label="资源类型" required>
          <a-select v-model:value="resourceForm.resourceType" placeholder="请选择资源类型">
            <a-select-option value="person">人员</a-select-option>
            <a-select-option value="equipment">设备</a-select-option>
            <a-select-option value="platform">台架</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="资源代码" required>
          <a-input v-model:value="resourceForm.resourceCode" placeholder="请输入资源代码" />
        </a-form-item>
        <a-form-item label="资源名称" required>
          <a-input v-model:value="resourceForm.resourceName" placeholder="请输入资源名称" />
        </a-form-item>
        <a-form-item label="资源数量">
          <a-input-number v-model:value="resourceForm.quantity" :min="1" style="width: 100%" />
        </a-form-item>
        <a-form-item label="每天有效时间(小时)">
          <a-input-number v-model:value="resourceForm.dailyHours" :min="1" :max="24" style="width: 100%" />
        </a-form-item>
        <a-form-item label="开始时间">
          <a-date-picker v-model:value="resourceForm.startDate" value-format="YYYY-MM-DD" style="width: 100%" />
        </a-form-item>
        <a-form-item label="结束时间">
          <a-date-picker v-model:value="resourceForm.endDate" value-format="YYYY-MM-DD" style="width: 100%" />
        </a-form-item>
        <a-form-item label="周末工作">
          <a-checkbox v-model:checked="resourceForm.weekend" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  getPlanTasks,
  createPlanTask,
  updatePlanTask,
  partialUpdatePlanTask,
  deletePlanTask,
  getResourcePlans,
  createResourcePlan,
  deleteResourcePlan,
  batchUpdatePlanTasks
} from '@/api/plan'
import GanttChart from './components/GanttChart.vue'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id

const activeTab = ref('tasks')
const planTasks = ref([])
const resources = ref([])
const loading = ref(false)
const resourceLoading = ref(false)
const selectedTask = ref(null)
const resourceModalVisible = ref(false)
const ganttRef = ref(null)

const projectInfo = ref({
  code: '',
  name: ''
})

const resourceForm = reactive({
  resourceType: undefined,
  resourceCode: '',
  resourceName: '',
  quantity: 1,
  dailyHours: 8,
  price: 0,
  unit: '',
  startDate: null,
  endDate: null,
  weekend: false
})

// 任务表格列
const taskColumns = [
  { title: '层级编码', dataIndex: 'wbsCode', key: 'wbsCode', width: 120 },
  { title: '任务名称', dataIndex: 'name', key: 'name', width: 200 },
  { title: '阶段', dataIndex: 'phase', key: 'phase', width: 100 },
  { title: '部门', dataIndex: 'department', key: 'department', width: 120 },
  { title: '任务负责人', dataIndex: 'owner', key: 'owner', width: 120 },
  { title: '被授权人', dataIndex: 'delegate', key: 'delegate', width: 120 },
  { title: '逻辑关系', dataIndex: 'logicRelation', key: 'logicRelation', width: 90 },
  { title: '紧前任务', dataIndex: 'preTask', key: 'preTask', width: 120 },
  { title: '计划开始', dataIndex: 'planStart', key: 'planStart', width: 120 },
  { title: '计划结束', dataIndex: 'planEnd', key: 'planEnd', width: 120 },
  { title: '工作量(天)', dataIndex: 'workload', key: 'workload', width: 100 },
  { title: '进度%', dataIndex: 'progress', key: 'progress', width: 80 },
  { title: '工时任务', dataIndex: 'isWorkHourTask', key: 'isWorkHourTask', width: 80, align: 'center' },
  { title: '交付物', dataIndex: 'hasDeliverable', key: 'hasDeliverable', width: 80, align: 'center' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '操作', key: 'action', width: 200, fixed: 'right' }
]

// 资源表格列
const resourceColumns = [
  { title: '资源类型', dataIndex: 'resourceType', key: 'resourceType', width: 100 },
  { title: '资源代码', dataIndex: 'resourceCode', key: 'resourceCode', width: 120 },
  { title: '资源名称', dataIndex: 'resourceName', key: 'resourceName', width: 150 },
  { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 80 },
  { title: '每天有效时间', dataIndex: 'dailyHours', key: 'dailyHours', width: 120 },
  { title: '价格', dataIndex: 'price', key: 'price', width: 100 },
  { title: '单位', dataIndex: 'unit', key: 'unit', width: 80 },
  { title: '开始时间', dataIndex: 'startDate', key: 'startDate', width: 120 },
  { title: '结束时间', dataIndex: 'endDate', key: 'endDate', width: 120 },
  { title: '周末', dataIndex: 'weekend', key: 'weekend', width: 80, align: 'center' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '操作', key: 'action', width: 100 }
]

// 任务树数据（供资源计划 Tab 的树选择器使用）
const taskTreeData = computed(() => {
  return planTasks.value
})

// 扁平任务列表（供甘特图使用）
const flatTasks = ref([])

// 从扁平列表构建树结构
const buildTree = (flatList) => {
  const map = {}
  const roots = []

  // 第一轮：创建映射
  flatList.forEach(item => {
    const id = item.plan_task_id
    map[id] = {
      ...item,
      id: id,
      name: item.task_name,
      wbsCode: '',
      phase: item.phase || '',
      department: item.department || '',
      owner: item.task_owner || '',
      delegate: item.authorized_owner || '',
      logicRelation: item.logic_relation || 'FS',
      preTask: item.pre_task_code || '',
      planStart: item.planned_start_date,
      planEnd: item.planned_end_date,
      workload: item.workload_days || 0,
      progress: item.progress_percent || 0,
      isWorkHourTask: item.is_hour_task === 'Y',
      hasDeliverable: item.has_deliverable === 'Y',
      status: item.task_status || 'NOT_STARTED',
      editing: false,
      children: []
    }
  })

  // 第二轮：建立父子关系
  flatList.forEach(item => {
    const id = item.plan_task_id
    const parentId = item.parent_task
    if (parentId && map[parentId]) {
      map[parentId].children.push(map[id])
    } else {
      roots.push(map[id])
    }
  })

  return roots
}

// 加载任务
const fetchTasks = async () => {
  loading.value = true
  try {
    const res = await getPlanTasks({ project: projectId, page_size: 999 })
    const list = res.data?.list || res.results || (Array.isArray(res.data) ? res.data : [])
    flatTasks.value = list

    // 构建树形结构供表格和甘特图使用
    planTasks.value = buildTree(list)

    // 尝试从第一条任务获取项目信息
    if (list.length > 0) {
      projectInfo.value.code = list[0].project || ''
      projectInfo.value.name = list[0].task_name || ''
    }
  } catch (error) {
    console.error('加载任务失败:', error)
    message.error('加载任务失败')
  } finally {
    loading.value = false
  }
}

// 加载资源
const fetchResources = async (taskId) => {
  if (!taskId) return
  resourceLoading.value = true
  try {
    const res = await getResourcePlans({ taskId })
    resources.value = res.data || []
  } catch (error) {
    message.error('加载资源失败')
  } finally {
    resourceLoading.value = false
  }
}

// 选择任务
const handleTaskSelect = (selectedKeys, info) => {
  const taskId = selectedKeys[0]
  selectedTask.value = info.node
  fetchResources(taskId)
}

// 添加子任务
const handleAddChild = (parentTask) => {
  const newTask = {
    id: Date.now(),
    projectId,
    parentId: parentTask.id,
    wbsCode: `${parentTask.wbsCode}.1`,
    name: '新任务',
    phase: 'development',
    department: '',
    owner: '',
    delegate: '',
    logicRelation: 'FS',
    preTask: '',
    planStart: null,
    planEnd: null,
    workload: 1,
    progress: 0,
    isWorkHourTask: false,
    hasDeliverable: false,
    status: 'draft',
    editing: true,
    children: []
  }
  if (!parentTask.children) {
    parentTask.children = []
  }
  parentTask.children.push(newTask)
  message.success('已添加子任务，请编辑后保存')
}

// 添加平级任务
const handleAddSibling = (task) => {
  const parent = findParent(planTasks.value, task.id)
  const newTask = {
    id: Date.now(),
    projectId,
    parentId: task.parentId,
    wbsCode: task.wbsCode,
    name: '新任务',
    phase: 'development',
    department: '',
    owner: '',
    delegate: '',
    logicRelation: 'FS',
    preTask: '',
    planStart: null,
    planEnd: null,
    workload: 1,
    progress: 0,
    isWorkHourTask: false,
    hasDeliverable: false,
    status: 'draft',
    editing: true
  }
  if (parent) {
    const index = parent.children.findIndex(item => item.id === task.id)
    parent.children.splice(index + 1, 0, newTask)
  } else {
    const index = planTasks.value.findIndex(item => item.id === task.id)
    planTasks.value.splice(index + 1, 0, newTask)
  }
  message.success('已添加平级任务，请编辑后保存')
}

// 查找父节点
const findParent = (list, id) => {
  for (const item of list) {
    if (item.children) {
      if (item.children.some(child => child.id === id)) {
        return item
      }
      const found = findParent(item.children, id)
      if (found) return found
    }
  }
  return null
}

// 编辑任务
const handleEditTask = (task) => {
  task.editing = true
}

// 保存任务
const handleSaveTask = async (task) => {
  try {
    const payload = {
      task_name: task.name,
      task_owner: task.owner,
      authorized_owner: task.delegate,
      planned_start_date: task.planStart,
      planned_end_date: task.planEnd,
      workload_days: task.workload,
      phase: task.phase,
      logic_relation: task.logicRelation,
      pre_task_code: task.preTask,
      department: task.department,
      progress_percent: task.progress,
      is_hour_task: task.isWorkHourTask ? 'Y' : 'N',
      has_deliverable: task.hasDeliverable ? 'Y' : 'N',
    }

    if (task.id && String(task.id).length < 13) {
      await updatePlanTask(task.id, payload)
    } else {
      payload.project = projectId
      if (task.parentId) {
        payload.parent_task_id = task.parentId
      }
      await createPlanTask(payload)
    }
    task.editing = false
    message.success('保存成功')
    fetchTasks()
  } catch (error) {
    message.error('保存失败')
  }
}

// 删除任务
const handleDelete = (task) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除任务"${task.name}"吗？`,
    onOk: async () => {
      try {
        await deletePlanTask(task.id)
        message.success('删除成功')
        fetchTasks()
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}

// 新增资源
const handleAddResource = () => {
  if (!selectedTask.value) {
    message.warning('请先选择任务')
    return
  }
  resourceModalVisible.value = true
}

// 保存资源
const handleResourceModalOk = async () => {
  try {
    await createResourcePlan({
      ...resourceForm,
      taskId: selectedTask.value.id
    })
    message.success('新增资源成功')
    resourceModalVisible.value = false
    fetchResources(selectedTask.value.id)
  } catch (error) {
    message.error('新增资源失败')
  }
}

const handleResourceModalCancel = () => {
  resourceModalVisible.value = false
}

// 删除资源
const handleDeleteResource = async (record) => {
  try {
    await deleteResourcePlan(record.id)
    message.success('删除成功')
    fetchResources(selectedTask.value.id)
  } catch (error) {
    message.error('删除失败')
  }
}

// 保存计划
const handleSave = async () => {
  // 甘特图页的修改由子组件维护，统一通过其暴露的 saveChanges 落库
  if (activeTab.value === 'gantt') {
    if (!ganttRef.value || typeof ganttRef.value.saveChanges !== 'function') {
      message.warning('甘特图尚未初始化，请稍后重试')
      return
    }
    try {
      await ganttRef.value.saveChanges()
      await fetchTasks()
    } catch (error) {
      message.error('保存失败，请稍后重试')
    }
    return
  }

  message.info('请在任务计划中使用行内“保存”，或切到甘特图后点击“保存修改”')
}

// 提交审批
const handleSubmit = async () => {
  message.success('计划已提交审批')
}

// 导入
const handleImport = () => {
  message.info('导入功能开发中')
}

// TBQ导入
const handleTbqImport = () => {
  message.info('TBQ导入功能开发中')
}

// 甘特图保存
const handleGanttSave = async (tasks) => {
  try {
    const normalizedTasks = (tasks || []).map(task => ({
      ...task,
      plan_task_id: task.plan_task_id || task.id
    }))

    const batchRes = await batchUpdatePlanTasks({ tasks: normalizedTasks })
    const batchData = batchRes?.data && typeof batchRes.data === 'object' ? batchRes.data : batchRes
    const updated = Array.isArray(batchData?.updated) ? batchData.updated : []
    const errors = Array.isArray(batchData?.errors) ? batchData.errors : []

    // 批量接口出现“0更新”或部分失败时，回退到逐条 PATCH，保证尽量落库
    if (normalizedTasks.length > 0 && (updated.length === 0 || errors.length > 0)) {
      const fields = [
        'planned_start_date', 'planned_end_date', 'workload_days',
        'sort_order', 'parent_task_id', 'phase', 'progress_percent',
        'task_name', 'pre_task_code', 'logic_relation', 'dependencies', 'task_level'
      ]
      const failedIdSet = new Set((errors || []).map(item => Number(item?.plan_task_id)).filter(Boolean))
      const fallbackTargets = failedIdSet.size > 0
        ? normalizedTasks.filter(task => failedIdSet.has(Number(task.plan_task_id)))
        : normalizedTasks

      const patchJobs = fallbackTargets.map(task => {
        const payload = {}
        fields.forEach(key => {
          if (Object.prototype.hasOwnProperty.call(task, key)) payload[key] = task[key]
        })
        // 确保 parent_task_id 始终包含（可能为 null 表示根任务）
        if (!Object.prototype.hasOwnProperty.call(payload, 'parent_task_id')) {
          payload.parent_task_id = task.parent_task_id ?? task.parent_task ?? null
        }
        return partialUpdatePlanTask(task.plan_task_id, payload)
      })

      const patchResults = await Promise.allSettled(patchJobs)
      const failed = patchResults.filter(item => item.status === 'rejected')
      if (failed.length > 0) {
        throw new Error(`仍有 ${failed.length} 条任务保存失败`)
      }
    }

    await fetchTasks() // 重新加载数据
    message.success('甘特图修改已同步到数据库')
  } catch (error) {
    message.error('同步失败，请重试')
    throw error // 让 GanttChart 知道保存失败
  }
}

// 返回
const handleBack = () => {
  router.back()
}

// 状态颜色
const getStatusColor = (status) => {
  const colorMap = {
    draft: 'default',
    pending: 'processing',
    approved: 'success',
    rejected: 'error',
    published: 'blue'
  }
  return colorMap[status] || 'default'
}

// 状态文本
const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    pending: '待审批',
    approved: '已批准',
    rejected: '已驳回',
    published: '已发布'
  }
  return textMap[status] || status
}

// 阶段文本
const getPhaseText = (phase) => {
  const textMap = {
    init: '立项',
    design: '设计',
    development: '开发',
    test: '测试',
    delivery: '交付'
  }
  return textMap[phase] || phase
}

// 资源类型文本
const getResourceTypeText = (type) => {
  const textMap = {
    person: '人员',
    equipment: '设备',
    platform: '台架'
  }
  return textMap[type] || type
}

onMounted(fetchTasks)
</script>

<style scoped>
.plan-edit {
  padding: 24px;
}

.plan-tabs {
  margin-top: 16px;
}

.gantt-tab-content {
  height: calc(100vh - 280px);
  min-height: 500px;
}
</style>
