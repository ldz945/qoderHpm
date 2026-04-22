<template>
  <div class="gantt-wrapper">
    <!-- 工具栏 -->
    <div class="gantt-toolbar">
      <div class="toolbar-left">
        <a-radio-group v-model:value="zoomLevel" size="small" @change="handleZoomChange">
          <a-radio-button value="day">日</a-radio-button>
          <a-radio-button value="week">周</a-radio-button>
          <a-radio-button value="month">月</a-radio-button>
          <a-radio-button value="quarter">季</a-radio-button>
        </a-radio-group>
        <a-divider type="vertical" />
        <a-button size="small" @click="handleExpandAll">
          <template #icon><span class="toolbar-icon">⊞</span></template>
          全部展开
        </a-button>
        <a-button size="small" @click="handleCollapseAll">
          <template #icon><span class="toolbar-icon">⊟</span></template>
          全部折叠
        </a-button>
        <a-divider type="vertical" />
        <a-button size="small" @click="handleFitToView">
          <template #icon><span class="toolbar-icon">⊡</span></template>
          适应视图
        </a-button>
      </div>
      <div class="toolbar-right">
        <a-tag v-if="pendingChanges > 0" color="warning">
          {{ pendingChanges }} 项待保存
        </a-tag>
        <a-button
          type="primary"
          size="small"
          :disabled="pendingChanges === 0"
          :loading="saving"
          @click="handleSaveChanges"
        >
          保存修改
        </a-button>
      </div>
    </div>

    <!-- 甘特图容器 -->
    <div ref="ganttContainer" class="gantt-container"></div>

    <!-- 任务基线编辑面板 -->
    <a-drawer
      v-model:open="baselinePanelVisible"
      title="任务基线编辑"
      placement="right"
      width="420"
      :mask="false"
      :destroy-on-close="false"
      @close="handleBaselinePanelClose"
    >
      <template v-if="selectedTaskBaseline.taskId">
        <div class="baseline-panel-summary">
          <div class="baseline-panel-title">{{ selectedTaskBaseline.taskName || '未命名任务' }}</div>
          <div class="baseline-panel-meta">WBS：{{ selectedTaskBaseline.wbsCode || '-' }}</div>
          <div class="baseline-panel-meta">计划日期：{{ selectedTaskBaseline.planStart || '-' }} ~ {{ selectedTaskBaseline.planEnd || '-' }}</div>
        </div>

        <a-form layout="vertical">
          <a-form-item label="基线开始日期">
            <a-date-picker
              v-model:value="selectedTaskBaseline.baselineStart"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="基线结束日期">
            <a-date-picker
              v-model:value="selectedTaskBaseline.baselineEnd"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </a-form-item>
        </a-form>

        <div class="baseline-panel-actions">
          <a-space wrap>
            <a-button size="small" @click="handleSyncSelectedBaselineFromPlan">同步计划日期</a-button>
            <a-button size="small" danger @click="handleClearSelectedBaseline">清空基线</a-button>
          </a-space>
        </div>

        <a-alert
          class="baseline-panel-tip"
          type="info"
          show-icon
          message="基线开始和结束需同时填写。点击“应用到图表”后会立即刷新任务基线条，并进入待保存列表。"
        />

        <div class="baseline-panel-footer">
          <a-space>
            <a-button @click="handleBaselinePanelClose">关闭</a-button>
            <a-button type="primary" @click="handleApplyTaskBaseline">应用到图表</a-button>
          </a-space>
        </div>
      </template>
      <a-empty v-else description="请选择一个任务" />
    </a-drawer>

    <!-- 连线关系编辑弹窗 -->
    <a-modal
      v-model:open="linkModalVisible"
      title="编辑任务依赖关系"
      @ok="handleLinkModalOk"
      @cancel="handleLinkModalCancel"
      width="420px"
    >
      <a-form layout="vertical">
        <a-form-item label="前置任务">
          <a-input :value="linkModalData.sourceName" disabled />
        </a-form-item>
        <a-form-item label="后续任务">
          <a-input :value="linkModalData.targetName" disabled />
        </a-form-item>
        <a-form-item label="依赖类型">
          <a-radio-group v-model:value="linkModalData.type">
            <a-radio-button value="0">FS (完成-开始)</a-radio-button>
            <a-radio-button value="1">SF (开始-完成)</a-radio-button>
            <a-radio-button value="2">FF (完成-完成)</a-radio-button>
            <a-radio-button value="3">SS (开始-开始)</a-radio-button>
          </a-radio-group>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" danger block @click="handleDeleteLink">
            删除此依赖关系
          </a-button>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import { gantt } from 'dhtmlx-gantt'
import 'dhtmlx-gantt/codebase/dhtmlxgantt.css'

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  },
  flatTasks: {
    type: Array,
    default: () => []
  },
  projectId: {
    type: [String, Number],
    required: true
  },
  active: {
    type: Boolean,
    default: false
  },
  onSave: {
    type: Function,
    default: null
  },
  baseline: {
    type: Object,
    default: null
  },
  showBaseline: {
    type: Boolean,
    default: true
  },
  showTaskBaselines: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['save', 'task-updated'])

const ganttContainer = ref(null)
const zoomLevel = ref('day')
const pendingChanges = ref(0)
const saving = ref(false)
const changedTasks = ref(new Map())
const baselinePanelVisible = ref(false)
const selectedTaskBaseline = reactive({
  taskId: null,
  taskName: '',
  wbsCode: '',
  planStart: '',
  planEnd: '',
  baselineStart: null,
  baselineEnd: null
})
const lastEditedTaskId = ref(null)
let ganttInitialized = false
let loadingInProgress = false
let baselineBandEl = null
let taskBaselineLayerId = null
let isRestoringScroll = false

const getLastFocusStorageKey = () => `plan-gantt-last-focus:${String(props.projectId)}`
const getScrollStorageKey = () => `plan-gantt-scroll-x:${String(props.projectId)}`

const persistLastFocusedTask = (taskId) => {
  if (taskId == null) return
  try {
    window.localStorage.setItem(getLastFocusStorageKey(), String(taskId))
  } catch (e) {
    // localStorage 不可用时静默忽略
  }
}

const readLastFocusedTask = () => {
  try {
    return window.localStorage.getItem(getLastFocusStorageKey())
  } catch (e) {
    return null
  }
}

const clearLastFocusedTask = () => {
  try {
    window.localStorage.removeItem(getLastFocusStorageKey())
  } catch (e) {
    // ignore
  }
}

const persistTimelineScrollX = (value) => {
  const x = Number(value)
  if (!Number.isFinite(x)) return
  try {
    window.localStorage.setItem(getScrollStorageKey(), String(Math.max(0, Math.round(x))))
  } catch (e) {
    // localStorage 不可用时静默忽略
  }
}

const readTimelineScrollX = () => {
  try {
    const raw = window.localStorage.getItem(getScrollStorageKey())
    const x = Number(raw)
    return Number.isFinite(x) && x >= 0 ? x : null
  } catch (e) {
    return null
  }
}

const restoreTimelineScrollX = (xValue = null) => {
  const parsedX = xValue == null ? null : Number(xValue)
  const savedX = Number.isFinite(parsedX) && parsedX >= 0 ? parsedX : readTimelineScrollX()
  if (savedX == null || !ganttInitialized) return
  isRestoringScroll = true
  try {
    const state = gantt.getScrollState ? gantt.getScrollState() : { y: 0 }
    gantt.scrollTo(savedX, state.y || 0)
  } catch (e) {
    // ignore
  } finally {
    setTimeout(() => {
      isRestoringScroll = false
    }, 0)
  }
}

const focusTaskInView = (taskId) => {
  if (!taskId || !ganttInitialized) return
  try {
    const task = gantt.getTask(taskId)
    if (!task) return
    gantt.showTask(taskId)
    gantt.selectTask(taskId)
  } catch (e) {
    // 任务不存在则清理无效缓存，避免每次重复报错
    clearLastFocusedTask()
  }
}

// ========================
// 基线辅助函数
// ========================
const parseDateSafe = (value) => {
  if (!value) return null
  if (value instanceof Date) return new Date(value)

  if (typeof value === 'string') {
    const dateOnlyMatch = value.match(/^(\d{4})-(\d{2})-(\d{2})$/)
    if (dateOnlyMatch) {
      const y = Number(dateOnlyMatch[1])
      const m = Number(dateOnlyMatch[2])
      const d = Number(dateOnlyMatch[3])
      return new Date(y, m - 1, d)
    }
  }

  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? null : d
}

const formatDateValue = (value) => {
  const date = parseDateSafe(value)
  return date ? formatDate(date) : ''
}

const resetSelectedTaskBaseline = () => {
  selectedTaskBaseline.taskId = null
  selectedTaskBaseline.taskName = ''
  selectedTaskBaseline.wbsCode = ''
  selectedTaskBaseline.planStart = ''
  selectedTaskBaseline.planEnd = ''
  selectedTaskBaseline.baselineStart = null
  selectedTaskBaseline.baselineEnd = null
}

const syncSelectedTaskBaseline = (task) => {
  if (!task) {
    resetSelectedTaskBaseline()
    return
  }

  selectedTaskBaseline.taskId = task.id
  selectedTaskBaseline.taskName = task.text || ''
  try {
    selectedTaskBaseline.wbsCode = gantt.getWBSCode(task)
  } catch (e) {
    selectedTaskBaseline.wbsCode = ''
  }
  selectedTaskBaseline.planStart = formatDateValue(task.start_date)
  selectedTaskBaseline.planEnd = formatDateValue(task.end_date)
  selectedTaskBaseline.baselineStart = formatDateValue(task.baseline_start_date) || null
  selectedTaskBaseline.baselineEnd = formatDateValue(task.baseline_end_date) || null
}

const openTaskBaselinePanel = (taskId) => {
  try {
    const task = gantt.getTask(taskId)
    gantt.selectTask(taskId)
    syncSelectedTaskBaseline(task)
    baselinePanelVisible.value = true
  } catch (e) {
    resetSelectedTaskBaseline()
  }
}

const handleBaselinePanelClose = () => {
  baselinePanelVisible.value = false
}

const handleSyncSelectedBaselineFromPlan = () => {
  selectedTaskBaseline.baselineStart = selectedTaskBaseline.planStart || null
  selectedTaskBaseline.baselineEnd = selectedTaskBaseline.planEnd || null
}

const handleClearSelectedBaseline = () => {
  selectedTaskBaseline.baselineStart = null
  selectedTaskBaseline.baselineEnd = null
}

const validateSelectedTaskBaseline = () => {
  const { baselineStart, baselineEnd } = selectedTaskBaseline
  const hasStart = Boolean(baselineStart)
  const hasEnd = Boolean(baselineEnd)

  if (hasStart !== hasEnd) {
    message.warning('基线开始日期和基线结束日期必须同时填写或同时清空')
    return false
  }

  if (!hasStart && !hasEnd) return true

  const start = parseDateSafe(baselineStart)
  const end = parseDateSafe(baselineEnd)
  if (!start || !end || end < start) {
    message.warning('基线结束日期不能早于基线开始日期')
    return false
  }

  return true
}

const handleApplyTaskBaseline = () => {
  if (!selectedTaskBaseline.taskId) return
  if (!validateSelectedTaskBaseline()) return

  try {
    const task = gantt.getTask(selectedTaskBaseline.taskId)
    task.baseline_start_date = selectedTaskBaseline.baselineStart || ''
    task.baseline_end_date = selectedTaskBaseline.baselineEnd || ''
    gantt.updateTask(task.id)
    recordChange(task)
    syncSelectedTaskBaseline(task)
    renderProjectBaselineBand()
    renderTaskBaselines()
    message.success('任务基线已应用，请点击“保存修改”落库')
  } catch (e) {
    message.error('任务基线应用失败，请重试')
  }
}

const getProjectBaselineRange = () => {
  if (!props.showBaseline || !props.baseline) return null
  const start = parseDateSafe(props.baseline.baseline_start_date || props.baseline.start_date || props.baseline.planned_start_date)
  const end = parseDateSafe(props.baseline.baseline_end_date || props.baseline.end_date || props.baseline.planned_end_date)
  if (!start || !end || end < start) return null
  return { start, end, label: props.baseline.label || '项目基线' }
}

const getTaskBaselineRange = (task) => {
  if (!task) return null
  const start = parseDateSafe(task.baseline_start_date || task.baselineStart || task.original_start_date)
  const end = parseDateSafe(task.baseline_end_date || task.baselineEnd || task.original_end_date)
  if (!start || !end || end < start) return null
  return { start, end }
}

const renderProjectBaselineBand = () => {
  try {
    if (!ganttInitialized) return
    const timeline = gantt.$task_data
    if (!timeline) return
    if (!baselineBandEl) {
      baselineBandEl = document.createElement('div')
      baselineBandEl.className = 'project-baseline-band'
      timeline.appendChild(baselineBandEl)
    }
    const baseline = getProjectBaselineRange()
    if (!baseline) {
      baselineBandEl.style.display = 'none'
      return
    }
    const startX = gantt.posFromDate(baseline.start)
    const endX = gantt.posFromDate(new Date(baseline.end.getTime() + 86400000))
    if (!Number.isFinite(startX) || !Number.isFinite(endX)) {
      baselineBandEl.style.display = 'none'
      return
    }
    const left = Math.min(startX, endX)
    const width = Math.max(2, Math.abs(endX - startX))
    baselineBandEl.style.display = 'block'
    baselineBandEl.style.left = left + 'px'
    baselineBandEl.style.width = width + 'px'
    baselineBandEl.setAttribute('data-label', baseline.label)
    baselineBandEl.title = baseline.label + ': ' + formatDate(baseline.start) + ' ~ ' + formatDate(baseline.end)
  } catch (e) {
    // 基线渲染失败不影响主功能
  }
}

// ========================
// 连线编辑弹窗
// ========================

/**
 * 手动绘制任务级基线条（兼容 GPL 版本，不依赖 addTaskLayer）
 * 在 gantt 的 timeline 区域为每个有基线数据的任务画一条灰色小条
 */
const renderTaskBaselines = () => {
  try {
    if (!ganttInitialized) return

    const timeline = gantt.$task_data
    if (!timeline) return

    // 清除旧的基线条
    const oldBars = timeline.querySelectorAll('.gantt-task-baseline-bar')
    oldBars.forEach(el => el.remove())

    if (!props.showTaskBaselines) return

    gantt.eachTask(function (task) {
      const baseline = getTaskBaselineRange(task)
      if (!baseline) return
      const bStart = baseline.start
      const bEnd = baseline.end

      // 检查任务是否在可见区域（已展开且未被折叠隐藏）
      if (!gantt.isTaskVisible(task.id)) return

      const pos = gantt.getTaskPosition(task, bStart, bEnd)
      if (!pos) return

      const el = document.createElement('div')
      el.className = 'gantt-task-baseline-bar'
      el.style.left = pos.left + 'px'
      el.style.width = Math.max(4, pos.width) + 'px'
      // 任务条在行内垂直居中，计算任务条底部位置
      const barTop = pos.top + (gantt.config.row_height - gantt.config.bar_height) / 2
      el.style.top = (barTop + gantt.config.bar_height) + 'px'
      el.title = '基线: ' + task.baseline_start_date + ' ~ ' + task.baseline_end_date
      timeline.appendChild(el)
    })
  } catch (e) {
    // 基线渲染失败不影响主功能
  }
}
const linkModalVisible = ref(false)
const linkModalData = reactive({
  linkId: null,
  sourceName: '',
  targetName: '',
  type: '0'
})

const handleLinkModalOk = () => {
  if (linkModalData.linkId == null) return
  try {
    const link = gantt.getLink(linkModalData.linkId)
    link.type = linkModalData.type
    gantt.updateLink(linkModalData.linkId)

    // 更新目标任务的 logic_relation
    const targetTask = gantt.getTask(link.target)
    targetTask.logic_relation = reverseLinkTypeMap[String(linkModalData.type)] || 'FS'
    gantt.updateTask(link.target)
    recordChange(targetTask)

    // 按新的依赖类型级联调整（延迟确保 link 数据已同步）
    const sourceId = link.source
    setTimeout(() => {
      cascadeInProgress = true
      try {
        cascadeByLinks(sourceId)
        gantt.render()
      } finally {
        cascadeInProgress = false
      }
    }, 0)

    message.success('依赖关系已更新')
  } catch (e) {
    console.warn('更新连线失败:', e)
  }
  linkModalVisible.value = false
}

const handleLinkModalCancel = () => {
  linkModalVisible.value = false
}

const handleDeleteLink = () => {
  if (linkModalData.linkId == null) return
  try {
    // 仅执行删除，依赖快照由 onAfterLinkDelete 统一记录
    gantt.deleteLink(linkModalData.linkId)
    message.success('依赖关系已删除')
  } catch (e) {
    console.warn('删除连线失败:', e)
  }
  linkModalVisible.value = false
}

// ========================
// 阶段(Phase)配色
// ========================
const phaseColorMap = {
  'init': { bar: '#52c41a', text: '立项' },
  '立项': { bar: '#52c41a', text: '立项' },
  '立项阶段': { bar: '#52c41a', text: '立项' },
  'design': { bar: '#1890ff', text: '设计' },
  '设计': { bar: '#1890ff', text: '设计' },
  '设计阶段': { bar: '#1890ff', text: '设计' },
  'development': { bar: '#722ed1', text: '开发' },
  '开发': { bar: '#722ed1', text: '开发' },
  '开发阶段': { bar: '#722ed1', text: '开发' },
  'test': { bar: '#fa8c16', text: '测试' },
  '测试': { bar: '#fa8c16', text: '测试' },
  '测试阶段': { bar: '#fa8c16', text: '测试' },
  'delivery': { bar: '#13c2c2', text: '交付' },
  '交付': { bar: '#13c2c2', text: '交付' },
  '交付阶段': { bar: '#13c2c2', text: '交付' },
  '需求': { bar: '#eb2f96', text: '需求' },
  '需求阶段': { bar: '#eb2f96', text: '需求' },
}
const defaultPhaseColor = { bar: '#8c8c8c', text: '未分类' }
const getPhaseColor = (phase) => {
  const normalized = phase == null ? '' : String(phase).trim()
  if (phaseColorMap[normalized]) return phaseColorMap[normalized]
  if (normalized) {
    return { bar: defaultPhaseColor.bar, text: normalized }
  }
  return defaultPhaseColor
}

// 依赖类型映射：后端 FS/SF/FF/SS <-> dhtmlx link type 0/1/2/3
const linkTypeMap = { 'FS': '0', 'SF': '1', 'FF': '2', 'SS': '3' }
const reverseLinkTypeMap = { '0': 'FS', '1': 'SF', '2': 'FF', '3': 'SS' }

const normalizeTaskId = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

/**
 * 获取任务的所有入向连线（当前任务为 target）
 */
const getIncomingLinks = (taskId) => {
  let task
  try {
    task = gantt.getTask(taskId)
  } catch (e) {
    return []
  }

  if (task.$target && Array.isArray(task.$target) && task.$target.length > 0) {
    return task.$target.map(linkId => {
      try { return gantt.getLink(linkId) } catch (e) { return null }
    }).filter(Boolean)
  }

  const result = []
  try {
    const allLinkIds = gantt.getLinks()
    if (Array.isArray(allLinkIds)) {
      allLinkIds.forEach(lid => {
        try {
          const l = gantt.getLink(lid)
          if (l && normalizeTaskId(l.target) === normalizeTaskId(taskId)) result.push(l)
        } catch (e) { /* skip */ }
      })
    }
  } catch (e) { /* getLinks not available */ }

  return result
}

const buildDependenciesFromIncomingLinks = (taskId) => {
  const incomingLinks = getIncomingLinks(taskId)
  if (!Array.isArray(incomingLinks) || incomingLinks.length === 0) return []

  return incomingLinks
    .filter(link => link && link.source)
    .map((link, index) => ({
      predecessor_task_id: Number(link.source),
      logic_relation: reverseLinkTypeMap[String(link.type)] || 'FS',
      lag_days: 0,
      sort_order: index
    }))
    .filter(dep => Number.isFinite(dep.predecessor_task_id) && dep.predecessor_task_id > 0)
}

// ========================
// 缩放配置
// ========================
const zoomConfig = {
  levels: [
    {
      name: 'day',
      scale_height: 54,
      min_column_width: 40,
      scales: [
        { unit: 'month', step: 1, format: '%Y年%M' },
        { unit: 'day', step: 1, format: '%d' }
      ]
    },
    {
      name: 'week',
      scale_height: 54,
      min_column_width: 60,
      scales: [
        { unit: 'month', step: 1, format: '%Y年%M' },
        { unit: 'week', step: 1, format: '第%W周' }
      ]
    },
    {
      name: 'month',
      scale_height: 54,
      min_column_width: 80,
      scales: [
        { unit: 'year', step: 1, format: '%Y年' },
        { unit: 'month', step: 1, format: '%M' }
      ]
    },
    {
      name: 'quarter',
      scale_height: 54,
      min_column_width: 100,
      scales: [
        { unit: 'year', step: 1, format: '%Y年' },
        { unit: 'quarter', step: 1, format: 'Q%q' }
      ]
    }
  ]
}

// ========================
// 初始化甘特图
// ========================
const initGantt = () => {
  if (!ganttContainer.value) return

  // 基本配置
  gantt.config.date_format = '%Y-%m-%d'
  gantt.config.xml_date = '%Y-%m-%d'
  gantt.config.fit_tasks = true
  gantt.config.auto_scheduling = false
  gantt.config.round_dnd_dates = true
  gantt.config.open_tree_initially = true
  gantt.config.row_height = 40
  gantt.config.bar_height = 24
  gantt.config.scale_height = 54

  // 启用拖拽功能
  gantt.config.drag_move = true      // 拖拽任务条移动
  gantt.config.drag_resize = true    // 拉伸任务条
  gantt.config.drag_progress = true  // 拖拽进度
  gantt.config.drag_links = true     // 启用连线拖拽创建
  gantt.config.order_branch = true
  gantt.config.order_branch_free = true

  // 连线显示 — 显示箭头类型标签
  gantt.config.show_links = true

  // 中文本地化
  gantt.locale = {
    date: {
      month_full: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
      month_short: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
      day_full: ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'],
      day_short: ['日', '一', '二', '三', '四', '五', '六']
    },
    labels: {
      new_task: '新任务',
      dhx_cal_today_button: '今天',
      day_tab: '日',
      week_tab: '周',
      month_tab: '月',
      new_event: '新建',
      icon_save: '保存',
      icon_cancel: '取消',
      icon_details: '详情',
      icon_edit: '编辑',
      icon_delete: '删除',
      confirm_closing: '',
      confirm_deleting: '确定删除此任务吗？',
      section_description: '描述',
      section_time: '时间',
      section_type: '类型',
      column_wbs: 'WBS',
      column_text: '任务名称',
      column_start_date: '开始日期',
      column_duration: '持续天数',
      column_add: '',
      link: '关联',
      confirm_link_deleting: '将被删除',
      link_start: '(开始)',
      link_end: '(结束)',
      type_task: '任务',
      type_project: '项目',
      type_milestone: '里程碑',
      minutes: '分钟',
      hours: '小时',
      days: '天',
      weeks: '周',
      months: '月',
      years: '年'
    }
  }

  // 左侧列配置
  gantt.config.columns = [
    {
      name: 'wbs',
      label: 'WBS',
      width: 60,
      align: 'center',
      template: function (task) {
        return gantt.getWBSCode(task)
      }
    },
    {
      name: 'text',
      label: '任务名称',
      tree: true,
      width: 200,
      resize: true
    },
    {
      name: 'phase',
      label: '阶段',
      width: 70,
      align: 'center',
      template: function (task) {
        const p = getPhaseColor(task.phase)
        return `<span class="gantt-phase-tag" style="background:${p.bar}22;color:${p.bar};border:1px solid ${p.bar}44">${p.text}</span>`
      }
    },
    {
      name: 'start_date',
      label: '开始日期',
      width: 90,
      align: 'center'
    },
    {
      name: 'end_date',
      label: '结束日期',
      width: 90,
      align: 'center'
    },
    {
      name: 'duration',
      label: '持续(天)',
      width: 65,
      align: 'center'
    },
    {
      name: 'owner',
      label: '负责人',
      width: 80,
      align: 'center'
    }
  ]

  // 任务条模板
  gantt.templates.task_class = function () { return '' }
  gantt.templates.task_cell_class = function () { return '' }
  gantt.templates.grid_row_class = function () { return '' }

  // 进度条文字
  gantt.templates.progress_text = function (start, end, task) {
    return `<span class="gantt-progress-text">${Math.round((task.progress || 0) * 100)}%</span>`
  }

  // 任务条文字
  gantt.templates.task_text = function (start, end, task) {
    return task.text
  }

  // 连线标签 — 在连线中点显示类型
  gantt.templates.link_class = function (link) {
    return 'gantt-link-interactive'
  }

  // 提示框
  gantt.templates.tooltip_text = function (start, end, task) {
    const phase = getPhaseColor(task.phase)
    const preInfo = task.pre_task_code ? `<br/><span>前置任务: ${task.pre_task_code} (${task.logic_relation || 'FS'})</span>` : ''
    return `<div class="gantt-tooltip-content">
      <div class="tooltip-title">${task.text}</div>
      <div class="tooltip-info">
        <span>阶段: ${phase.text}</span><br/>
        <span>开始: ${gantt.templates.tooltip_date_format(start)}</span><br/>
        <span>结束: ${gantt.templates.tooltip_date_format(end)}</span><br/>
        <span>持续: ${task.duration} 天</span><br/>
        <span>进度: ${Math.round((task.progress || 0) * 100)}%</span>
        ${task.owner ? '<br/><span>负责人: ' + task.owner + '</span>' : ''}
        ${preInfo}
      </div>
    </div>`
  }

  gantt.templates.tooltip_date_format = function (date) {
    const y = date.getFullYear()
    const m = String(date.getMonth() + 1).padStart(2, '0')
    const d = String(date.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  }

  // 今日线
  gantt.plugins({
    marker: true,
    tooltip: true,
    quick_info: false
  })

  const today = new Date()
  gantt.addMarker({
    start_date: today,
    css: 'today-marker',
    text: '今天',
    title: `今天: ${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  })

  // ========================
  // 事件监听
  // ========================

  // 级联保护标志：防止 cascadeByLinks 内部调用 gantt.updateTask() 触发 onAfterTaskUpdate 导致无限递归
  let cascadeInProgress = false

  // 拖拽开始前：记录原始日期
  let dragStartDate = null
  let dragEndDate = null

  gantt.attachEvent('onBeforeTaskDrag', function (id, mode, e) {
    const task = gantt.getTask(id)
    dragStartDate = new Date(task.start_date)
    dragEndDate = new Date(task.end_date)
    return true
  })

   // 拖拽完成后：执行级联调整
   gantt.attachEvent('onAfterTaskDrag', function (id, mode, e) {
     const task = gantt.getTask(id)
     
     recordChange(task)

     cascadeInProgress = true
     try {
       // 父任务移动时，子任务跟随移动
       if (mode === gantt.config.drag_mode.move) {
         cascadeChildren(task, dragStartDate)
       }

       // 基于依赖链级联更新后继任务（move 和 resize 都触发）
       cascadeByLinks(id)

       // 也回溯更新前驱任务的父任务日期范围
       updateParentDates(task)

       // 强制全量刷新，确保视觉同步
       gantt.render()
     } finally {
       cascadeInProgress = false
     }
     return true
   })

  /**
   * 级联更新子任务：当父任务整体移动时，所有子任务跟随移动相同偏移量
   */
  function cascadeChildren(parentTask, originalStart) {
    if (!originalStart) return

    const delta = parentTask.start_date.getTime() - originalStart.getTime()
    if (delta === 0) return

    const children = gantt.getChildren(parentTask.id)

    // Phase 1: 先保存所有子任务的原始位置，防止兄弟的 cascadeByLinks 修改后再叠加 delta
    const originals = new Map()
    children.forEach(childId => {
      const child = gantt.getTask(childId)
      originals.set(childId, { start: new Date(child.start_date), end: new Date(child.end_date) })
    })

    // 基于原始位置统一移动所有子任务
    children.forEach(childId => {
      const child = gantt.getTask(childId)
      const orig = originals.get(childId)
      child.start_date = new Date(orig.start.getTime() + delta)
      child.end_date = new Date(orig.end.getTime() + delta)
      child.duration = gantt.calculateDuration(child.start_date, child.end_date)
      recordChange(child)

      // 递归子节点
      cascadeChildren(child, orig.start)
    })

    // Phase 2: 所有子任务统一移动完成后，再统一处理依赖约束
    // 避免兄弟 A 的 cascadeByLinks 修改兄弟 B 后，B 再被 Phase 1 叠加 delta
    children.forEach(childId => {
      cascadeByLinks(childId)
    })
  }

  /**
   * 获取任务的所有出向连线（当前任务为 source）
   * 使用 task.$source（dhtmlx-gantt 内部维护的出向连线数组），
   * 如果不存在则回退到手动遍历所有连线。
   */
  function getOutgoingLinks(taskId) {
    let task
    try {
      task = gantt.getTask(taskId)
    } catch (e) {
      return []
    }

    // 优先使用 $source（dhtmlx-gantt 自动维护的出向连线 ID 列表）
    if (task.$source && Array.isArray(task.$source) && task.$source.length > 0) {
      return task.$source.map(linkId => {
        try { return gantt.getLink(linkId) } catch (e) { return null }
      }).filter(Boolean)
    }

    // 回退：遍历 gantt 内部数据存储
    const result = []
    try {
      // 尝试 gantt.getLinks()（部分版本可用）
      const allLinkIds = gantt.getLinks()
      if (Array.isArray(allLinkIds)) {
        allLinkIds.forEach(lid => {
          try {
            const l = gantt.getLink(lid)
            if (l && String(l.source) === String(taskId)) result.push(l)
          } catch (e) { /* skip */ }
        })
        if (result.length > 0) return result
      }
    } catch (e) { /* getLinks not available */ }

    // 最终回退：直接访问内部 links 存储
    try {
      const linksStore = gantt.$data && gantt.$data.linksStore
      if (linksStore) {
        const items = linksStore.getItems ? linksStore.getItems() : []
        items.forEach(l => {
          if (l && String(l.source) === String(taskId)) result.push(l)
        })
      }
    } catch (e) { /* skip */ }


    return result
  }

  /**
   * 基于依赖链级联更新后继任务
   * 前驱变了 → 强制后继满足约束
   */
  function cascadeByLinks(taskId) {
    
    const queue = [String(taskId)]
    const inQueue = new Set(queue)

    const maxDate = (base, candidate) => {
      if (!candidate) return base
      if (!base || candidate.getTime() > base.getTime()) return new Date(candidate)
      return base
    }

    const isAncestorTask = (ancestorId, taskId) => {
      const normalizedAncestorId = String(ancestorId)
      let currentId = taskId
      while (currentId && currentId !== 0 && currentId !== '0') {
        let currentTask
        try {
          currentTask = gantt.getTask(currentId)
        } catch (e) {
          return false
        }
        const parentId = currentTask.parent
        if (!parentId || parentId === 0 || parentId === '0') return false
        if (String(parentId) === normalizedAncestorId) return true
        currentId = parentId
      }
      return false
    }

    const hasDescendantPredecessorInIncoming = (incomingLinks, sourceId, targetId) => {
      const normalizedSourceId = String(sourceId)
      return incomingLinks.some(link => {
        if (!link || String(link.target) !== String(targetId)) return false
        const linkSourceId = String(link.source)
        if (linkSourceId === normalizedSourceId) return false
        // 若同一目标同时存在“父任务前置”和“其子孙任务前置”，优先子孙任务，避免父任务汇总链路压制前移
        return isAncestorTask(normalizedSourceId, linkSourceId)
      })
    }

    const applyIncomingConstraints = (targetId) => {
      let targetTask
      try {
        targetTask = gantt.getTask(targetId)
      } catch (e) {
        return false
      }

      const incomingLinks = getIncomingLinks(targetId)
      if (!incomingLinks.length) return false

      let requiredStart = null
      let requiredEnd = null
      incomingLinks.forEach(link => {
        // 父任务由子任务汇总得出，父->子依赖属于展示/汇总关系，不应锁死子任务前移。
        if (isAncestorTask(link.source, targetId)) {
          return
        }

        // 同一目标已存在该前置任务子孙节点的连线时，忽略父级汇总连线
        // 典型场景：阶段父任务与末级任务都连到后续阶段，拖动末级任务时应按末级任务优先传播
        let sourceTaskForSummaryCheck = null
        try {
          sourceTaskForSummaryCheck = gantt.getTask(link.source)
        } catch (e) {
          sourceTaskForSummaryCheck = null
        }
        if (
          sourceTaskForSummaryCheck &&
          gantt.hasChild && gantt.hasChild(link.source) &&
          hasDescendantPredecessorInIncoming(incomingLinks, link.source, targetId)
        ) {
          return
        }

        let sourceTask
        try {
          sourceTask = gantt.getTask(link.source)
        } catch (e) {
          return
        }

        const linkType = reverseLinkTypeMap[String(link.type)] || 'FS'
        if (linkType === 'FS') {
          requiredStart = maxDate(requiredStart, sourceTask.end_date)
        } else if (linkType === 'SS') {
          requiredStart = maxDate(requiredStart, sourceTask.start_date)
        } else if (linkType === 'FF') {
          requiredEnd = maxDate(requiredEnd, sourceTask.end_date)
        } else if (linkType === 'SF') {
          requiredEnd = maxDate(requiredEnd, sourceTask.start_date)
        }
      })

      const duration = targetTask.duration || 1
      const originalStart = new Date(targetTask.start_date)
      const originalEnd = new Date(targetTask.end_date || gantt.calculateEndDate(targetTask.start_date, duration))
      let newStart = new Date(originalStart)
      let newEnd = new Date(originalEnd)

      // 按约束精确重算：允许前移和后移。
      if (requiredStart) {
        newStart = new Date(requiredStart)
        newEnd = gantt.calculateEndDate(newStart, duration)
      }
      if (requiredEnd) {
        if (!requiredStart) {
          newEnd = new Date(requiredEnd)
          newStart = gantt.calculateEndDate(newEnd, -duration)
        } else if (newEnd.getTime() < requiredEnd.getTime()) {
          // 同时有开始/结束约束时，取更严格的结束约束，再保证开始约束不被破坏
          newEnd = new Date(requiredEnd)
          newStart = gantt.calculateEndDate(newEnd, -duration)
          if (newStart.getTime() < requiredStart.getTime()) {
            newStart = new Date(requiredStart)
            newEnd = gantt.calculateEndDate(newStart, duration)
          }
        }
      }

      if (originalStart.getTime() === newStart.getTime() && originalEnd.getTime() === newEnd.getTime()) {
        return false
      }

      targetTask.start_date = newStart
      targetTask.end_date = newEnd
      targetTask.duration = gantt.calculateDuration(newStart, newEnd)
      recordChange(targetTask)
      
      const delta = newStart.getTime() - originalStart.getTime()
      if (delta !== 0) {
        cascadeChildren(targetTask, originalStart)
      }
      // 依赖级联导致子任务移动后，同步刷新其父任务汇总区间，并继续触发父任务后续依赖
      updateParentDates(targetTask)
      return true
    }

    while (queue.length > 0) {
      const currentId = String(queue.shift())
      inQueue.delete(currentId)

      const outLinks = getOutgoingLinks(currentId)
      const targetIds = [...new Set(outLinks.map(link => String(link.target)))]
      targetIds.forEach(targetId => {
        const changed = applyIncomingConstraints(targetId)
        if (changed && !inQueue.has(targetId)) {
          queue.push(targetId)
          inQueue.add(targetId)
        }
      })
    }
  }

   /**
    * 更新父任务日期范围：使父任务包含所有子任务
    * 并级联调整与父任务有FS关系的后续任务
    */
   function updateParentDates(task, options = {}) {
     const { cascadeForParentLinks = true } = options
     const parentId = task.parent
     if (!parentId || parentId == 0) return

     try {
       const parent = gantt.getTask(parentId)
       const children = gantt.getChildren(parentId)
       if (children.length === 0) return

       let minStart = null
       let maxEnd = null
       children.forEach(childId => {
         const child = gantt.getTask(childId)
         if (!minStart || child.start_date < minStart) minStart = new Date(child.start_date)
         const childEnd = child.end_date || gantt.calculateEndDate(child.start_date, child.duration)
         if (!maxEnd || childEnd > maxEnd) maxEnd = new Date(childEnd)
       })

       if (minStart && maxEnd) {
         const changed = parent.start_date.getTime() !== minStart.getTime() ||
                         parent.end_date.getTime() !== maxEnd.getTime()
         if (changed) {
           parent.start_date = minStart
           parent.end_date = maxEnd
           parent.duration = gantt.calculateDuration(minStart, maxEnd)
           recordChange(parent)

           // 父任务日期变化后，按需要级联调整父任务后续任务
           if (cascadeForParentLinks) {
             cascadeByLinks(parentId)
           }

           // 递归向上
           updateParentDates(parent, { cascadeForParentLinks })
         }
       }
     } catch (e) {
       // parent doesn't exist
     }
   }

  // 拖拽排序后
  gantt.attachEvent('onRowDragEnd', function (id, target) {
    const task = gantt.getTask(id)

    const newParentId = task.parent || 0
    let newLevel = 1
    if (newParentId && newParentId != 0) {
      try {
        const parentTask = gantt.getTask(newParentId)
        newLevel = (parentTask.task_level || 1) + 1
      } catch (e) {
        newLevel = 1
      }
    }
    task.task_level = newLevel
    recordChange(task)

    function updateChildrenLevel(parentId, parentLevel) {
      const children = gantt.getChildren(parentId)
      children.forEach((childId, index) => {
        const child = gantt.getTask(childId)
        child.task_level = parentLevel + 1
        child.sort_order = index
        recordChange(child)
        updateChildrenLevel(childId, parentLevel + 1)
      })
    }
    updateChildrenLevel(id, newLevel)

    const siblings = gantt.getChildren(newParentId)
    siblings.forEach((childId, index) => {
      const child = gantt.getTask(childId)
      child.sort_order = index
      recordChange(child)
    })

    return true
  })

  // 任务编辑后：记录变更，并在非级联状态下触发依赖传播
  gantt.attachEvent('onAfterTaskUpdate', function (id, task) {
    // 数据加载期间不记录变更也不级联，避免 parse() 触发二次调度
    if (loadingInProgress) return true

    if (baselinePanelVisible.value && String(selectedTaskBaseline.taskId) === String(id)) {
      syncSelectedTaskBaseline(task)
    }

    recordChange(task)
    
    if (!cascadeInProgress) {
      cascadeInProgress = true
      try {
        cascadeByLinks(id)
        updateParentDates(task)
        gantt.render()
      } finally {
        cascadeInProgress = false
      }
    }
    return true
  })

  // ========================
  // 连线事件
  // ========================

  // 点击连线：打开编辑弹窗
  gantt.attachEvent('onLinkClick', function (id, e) {
    try {
      const link = gantt.getLink(id)
      const sourceTask = gantt.getTask(link.source)
      const targetTask = gantt.getTask(link.target)

      linkModalData.linkId = id
      linkModalData.sourceName = `${gantt.getWBSCode(sourceTask)} ${sourceTask.text}`
      linkModalData.targetName = `${gantt.getWBSCode(targetTask)} ${targetTask.text}`
      linkModalData.type = String(link.type)
      linkModalVisible.value = true
    } catch (e) {
      console.warn('获取连线信息失败:', e)
    }
    return false  // 阻止默认行为
  })

  // 新增依赖连线时
  gantt.attachEvent('onAfterLinkAdd', function (id, link) {
    try {
      const targetTask = gantt.getTask(link.target)
      targetTask.pre_task_code = String(link.source)
      targetTask.logic_relation = reverseLinkTypeMap[String(link.type)] || 'FS'
      gantt.updateTask(link.target)
      recordChange(targetTask)

      // 立即按新依赖关系调整时间（使用 setTimeout 确保 link 已完全入库）
      setTimeout(() => {
        cascadeInProgress = true
        try {
          cascadeByLinks(link.source)
          gantt.render()
        } finally {
          cascadeInProgress = false
        }
      }, 0)
    } catch (e) {
      console.warn('处理连线新增失败:', e)
    }
    return true
  })

  // 删除依赖连线时
  gantt.attachEvent('onAfterLinkDelete', function (id, link) {
    try {
      const targetTask = gantt.getTask(link.target)
      targetTask.pre_task_code = ''
      targetTask.logic_relation = 'FS'
      recordChange(targetTask, { clearDependencies: true })
    } catch (e) { /* ignore */ }
    return true
  })

  // 连线验证：防止自引用和重复连线
  gantt.attachEvent('onBeforeLinkAdd', function (id, link) {
    if (link.source === link.target) {
      message.warning('不允许任务引用自身')
      return false
    }
    // 检查是否已存在同方向的连线（使用 $target 属性）
    try {
      const targetTask = gantt.getTask(link.target)
      if (targetTask.$target && Array.isArray(targetTask.$target)) {
        for (const existingLinkId of targetTask.$target) {
          if (existingLinkId === id) continue
          try {
            const existing = gantt.getLink(existingLinkId)
            if (String(existing.source) === String(link.source)) {
              message.warning('这两个任务之间已存在依赖关系')
              return false
            }
          } catch (e) { /* skip */ }
        }
      }
    } catch (e) { /* skip check */ }
    return true
  })

  // 双击连线也打开编辑弹窗
  gantt.attachEvent('onLinkDblClick', function (id, e) {
    try {
      const link = gantt.getLink(id)
      const sourceTask = gantt.getTask(link.source)
      const targetTask = gantt.getTask(link.target)

      linkModalData.linkId = id
      linkModalData.sourceName = `${gantt.getWBSCode(sourceTask)} ${sourceTask.text}`
      linkModalData.targetName = `${gantt.getWBSCode(targetTask)} ${targetTask.text}`
      linkModalData.type = String(link.type)
      linkModalVisible.value = true
    } catch (e) {
      console.warn('获取连线信息失败:', e)
    }
    return false
  })

  // 缩放
  gantt.attachEvent('onTaskClick', function (id, e) {
    openTaskBaselinePanel(id)
    return true
  })

  gantt.attachEvent('onGanttScroll', function (left, top) {
    if (loadingInProgress || isRestoringScroll) return true
    persistTimelineScrollX(left)
    return true
  })

  gantt.ext.zoom.init(zoomConfig)
  gantt.ext.zoom.setLevel('day')

  // 初始化
  gantt.init(ganttContainer.value)
  ganttInitialized = true

  // 注册基线渲染（通过 onGanttRender 事件手动绘制，兼容 GPL 版本）
  gantt.attachEvent('onGanttRender', function () {
    renderProjectBaselineBand()
    renderTaskBaselines()
    return true
  })
  gantt.attachEvent('onDataRender', function () {
    renderProjectBaselineBand()
    renderTaskBaselines()
    return true
  })

  // 加载数据
  loadTasks()
}

// ========================
// 记录变更
// ========================
const recordChange = (task, options = {}) => {
  const { clearDependencies = false } = options
  const startDate = task.start_date instanceof Date
    ? formatDate(task.start_date)
    : task.start_date
  const endDate = task.end_date instanceof Date
    ? formatDate(task.end_date)
    : task.end_date

  // 根据日期重新计算 workload_days（天数差 = end - start，不加1）
  let workloadDays = task.duration || 0
  if (startDate && endDate) {
    const s = new Date(startDate)
    const e = new Date(endDate)
    const diffTime = e.getTime() - s.getTime()
    workloadDays = Math.max(1, Math.round(diffTime / (1000 * 60 * 60 * 24)))
  }
  if (workloadDays <= 0) workloadDays = 1

  const rawParent = task.parent
  const normalizedParent = (rawParent === 0 || rawParent === '0' || rawParent === '' || rawParent == null)
    ? null
    : rawParent

  // 从入向连线构建依赖数组，支持一个任务多个前置任务。
  const previous = changedTasks.value.get(task.id)
  let dependencies = buildDependenciesFromIncomingLinks(task.id)
  if (!clearDependencies && dependencies.length === 0 && Array.isArray(previous?.dependencies)) {
    dependencies = previous.dependencies
  }

  const primaryDependency = dependencies[0] || null
  const preTaskCode = primaryDependency ? String(primaryDependency.predecessor_task_id) : ''
  const logicRelation = primaryDependency?.logic_relation || 'FS'

  changedTasks.value.set(task.id, {
    plan_task_id: task.id,
    planned_start_date: startDate,
    planned_end_date: endDate,
    baseline_start_date: task.baseline_start_date || null,
    baseline_end_date: task.baseline_end_date || null,
    workload_days: workloadDays,
    sort_order: task.sort_order || 0,
    parent_task_id: normalizedParent,
    phase: task.phase || '',
    progress_percent: Math.round((task.progress || 0) * 100),
    task_name: task.text,
    pre_task_code: preTaskCode,
    logic_relation: logicRelation,
    dependencies: dependencies,
    task_level: task.task_level || 1
  })
  lastEditedTaskId.value = task.id
  pendingChanges.value = changedTasks.value.size
}

const formatDate = (date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

// ========================
// 加载任务数据
// ========================
const loadTasks = () => {
  if (!ganttInitialized) return
  loadingInProgress = true
  const savedScrollX = readTimelineScrollX()
  try {
    gantt.clearAll()

    let ganttData, ganttLinks
    if (props.flatTasks.length > 0) {
      const result = convertFlatTasks(props.flatTasks)
      ganttData = result.data
      ganttLinks = result.links
    } else {
      const result = flattenTreeTasks(props.tasks)
      ganttData = result.data
      ganttLinks = result.links
    }

    if (ganttData.length === 0) {
      gantt.render()
      return
    }

    gantt.parse({
      data: ganttData,
      links: ganttLinks
    })

    // 全部展开
    gantt.eachTask(function (task) {
      task.$open = true
    })
    gantt.render()

    const targetFocusId = lastEditedTaskId.value != null
      ? String(lastEditedTaskId.value)
      : readLastFocusedTask()
    nextTick(() => {
      if (targetFocusId) {
        focusTaskInView(targetFocusId)
      }
      // showTask 可能改写横向滚动，最后再恢复一次用户的时间轴位置
      restoreTimelineScrollX(savedScrollX)
      // 某些渲染阶段会在下一帧再次改写 scroll，做一次延迟兜底恢复
      setTimeout(() => restoreTimelineScrollX(savedScrollX), 80)
    })
  } finally {
    loadingInProgress = false
  }
}

// 将后端扁平数据直接转换为甘特图格式
const convertFlatTasks = (tasks) => {
  if (!tasks || !Array.isArray(tasks)) return { data: [], links: [] }

  const ganttData = []
  const ganttLinks = []
  const taskIdMap = new Map()
  const linkKeySet = new Set()
  let linkId = 1

  const registerTaskId = (value) => {
    const normalized = normalizeTaskId(value)
    if (!normalized) return
    taskIdMap.set(normalized, value)
    const numeric = Number(normalized)
    if (!Number.isNaN(numeric)) {
      taskIdMap.set(String(numeric), value)
    }
  }

  const resolveTaskId = (value) => {
    const normalized = normalizeTaskId(value)
    if (!normalized) return null
    if (taskIdMap.has(normalized)) return taskIdMap.get(normalized)
    const numeric = Number(normalized)
    if (!Number.isNaN(numeric)) {
      const numericKey = String(numeric)
      if (taskIdMap.has(numericKey)) return taskIdMap.get(numericKey)
    }
    return null
  }

  tasks.forEach((task, index) => {
    const startDate = task.planned_start_date
    const endDate = task.planned_end_date

    // 优先使用后端的 workload_days（天数差 = end - start，不加1）
    let duration = Number(task.workload_days) || 0
    if (duration <= 0 && startDate && endDate) {
      const start = new Date(startDate)
      const end = new Date(endDate)
      const diffTime = end.getTime() - start.getTime()
      duration = Math.max(1, Math.round(diffTime / (1000 * 60 * 60 * 24)))
    }
    if (duration <= 0) duration = 1

    const phase = task.phase || ''
    const phaseInfo = getPhaseColor(phase)

    ganttData.push({
      id: task.plan_task_id,
      text: task.task_name || '未命名任务',
      start_date: startDate || formatDate(new Date()),
      duration: duration,
      progress: Number(task.progress_percent || 0) / 100,
      parent: task.parent_task || 0,
      phase: phase,
      owner: task.task_owner || '',
      sort_order: task.sort_order || index,
      open: true,
      color: phaseInfo.bar,
      pre_task_code: task.pre_task_code || '',
      logic_relation: task.logic_relation || 'FS',
      task_level: task.task_level || 1,
      baseline_start_date: task.baseline_start_date || '',
      baseline_end_date: task.baseline_end_date || ''
    })
    registerTaskId(task.plan_task_id)
  })

  // 优先使用 dependencies 构建连线，向后兼容预留字段 pre_task_code。
  tasks.forEach(task => {
    const rawDependencies = Array.isArray(task.dependencies) && task.dependencies.length > 0
      ? task.dependencies
      : (task.pre_task_code
        ? [{ predecessor_task_id: task.pre_task_code, logic_relation: task.logic_relation || 'FS', sort_order: 0 }]
        : [])

    rawDependencies.forEach(dep => {
      const sourceId = resolveTaskId(dep.predecessor_task_id)
      const targetId = resolveTaskId(task.plan_task_id) || task.plan_task_id
      if (sourceId == null || targetId == null) return
      if (normalizeTaskId(sourceId) === normalizeTaskId(targetId)) return

      const linkKey = `${normalizeTaskId(sourceId)}->${normalizeTaskId(targetId)}:${dep.logic_relation || 'FS'}`
      if (linkKeySet.has(linkKey)) return
      linkKeySet.add(linkKey)

      ganttLinks.push({
        id: linkId++,
        source: sourceId,
        target: targetId,
        type: linkTypeMap[dep.logic_relation] || '0'
      })
    })
  })

  return { data: ganttData, links: ganttLinks }
}

// 从树形数据展开为甘特图格式
const flattenTreeTasks = (tasks, parentId = 0, sortStart = 0) => {
  const result = []
  if (!tasks || !Array.isArray(tasks)) return { data: result, links: [] }

  tasks.forEach((task, index) => {
    const startDate = task.planned_start_date || task.planStart
    const endDate = task.planned_end_date || task.planEnd

    // 优先使用后端的 workload_days（天数差 = end - start，不加1）
    let duration = Number(task.workload_days || task.workload) || 0
    if (duration <= 0 && startDate && endDate) {
      const start = new Date(startDate)
      const end = new Date(endDate)
      const diffTime = end.getTime() - start.getTime()
      duration = Math.max(1, Math.round(diffTime / (1000 * 60 * 60 * 24)))
    }
    if (duration <= 0) duration = 1

    const phase = task.phase || ''
    const phaseInfo = getPhaseColor(phase)

    const ganttTask = {
      id: task.plan_task_id || task.id,
      text: task.task_name || task.name || '未命名任务',
      start_date: startDate || formatDate(new Date()),
      duration: duration,
      progress: (task.progress_percent || task.progress || 0) / 100,
      parent: parentId,
      phase: phase,
      owner: task.task_owner || task.owner || '',
      sort_order: task.sort_order || sortStart + index,
      open: true,
      color: phaseInfo.bar,
      pre_task_code: task.pre_task_code || task.preTask || '',
      logic_relation: task.logic_relation || task.logicRelation || 'FS',
      task_level: task.task_level || 1,
      baseline_start_date: task.baseline_start_date || '',
      baseline_end_date: task.baseline_end_date || ''
    }

    result.push(ganttTask)

    if (task.children && task.children.length > 0) {
      const childrenResult = flattenTreeTasks(task.children, ganttTask.id, 0)
      result.push(...childrenResult.data)
    }
  })

  return { data: result, links: [] }
}

// ========================
// 工具栏操作
// ========================
const handleZoomChange = () => {
  gantt.ext.zoom.setLevel(zoomLevel.value)
}

const handleExpandAll = () => {
  gantt.eachTask(function (task) {
    task.$open = true
  })
  gantt.render()
}

const handleCollapseAll = () => {
  gantt.eachTask(function (task) {
    task.$open = false
  })
  gantt.render()
}

const handleFitToView = () => {
  const taskCount = gantt.getTaskCount()
  if (taskCount === 0) return

  let minDate = null
  let maxDate = null
  gantt.eachTask(function (task) {
    if (!minDate || task.start_date < minDate) minDate = new Date(task.start_date)
    const endDate = task.end_date || gantt.calculateEndDate(task.start_date, task.duration)
    if (!maxDate || endDate > maxDate) maxDate = new Date(endDate)
  })

  if (minDate && maxDate) {
    minDate.setDate(minDate.getDate() - 7)
    maxDate.setDate(maxDate.getDate() + 7)
    gantt.config.start_date = minDate
    gantt.config.end_date = maxDate
    gantt.render()
  }
}

const syncParentRangesBeforeSave = () => {
  if (!ganttInitialized) return

  const ids = []
  gantt.eachTask(function (task) {
    ids.push(task.id)
  })

  const calcDepth = (taskId) => {
    let depth = 0
    let currentId = taskId
    const visited = new Set()
    while (currentId && currentId !== 0 && currentId !== '0') {
      if (visited.has(String(currentId))) break
      visited.add(String(currentId))
      let currentTask
      try {
        currentTask = gantt.getTask(currentId)
      } catch (e) {
        break
      }
      const parentId = currentTask.parent
      if (!parentId || parentId === 0 || parentId === '0') break
      depth += 1
      currentId = parentId
    }
    return depth
  }

  ids
    .sort((a, b) => calcDepth(b) - calcDepth(a))
    .forEach(taskId => {
      try {
        const task = gantt.getTask(taskId)
        updateParentDates(task, { cascadeForParentLinks: false })
      } catch (e) {
        // skip invalid task
      }
    })
}

// ========================
// 保存变更
// ========================
const handleSaveChanges = async () => {
  // 保存前兜底：强制按当前子任务区间回写父任务，避免落库后父子不对齐
  syncParentRangesBeforeSave()

  try {
    const scrollState = gantt.getScrollState ? gantt.getScrollState() : null
    persistTimelineScrollX(scrollState?.x)
  } catch (e) {
    // ignore
  }

  if (changedTasks.value.size === 0) return

  saving.value = true
  try {
    const tasks = Array.from(changedTasks.value.values())
    if (typeof props.onSave === 'function') {
      await props.onSave(tasks)
    } else {
      // 向后兼容旧事件方式（不保证可等待父组件异步结果）
      emit('save', tasks)
    }
    persistLastFocusedTask(lastEditedTaskId.value)
    try {
      const scrollState = gantt.getScrollState ? gantt.getScrollState() : null
      persistTimelineScrollX(scrollState?.x)
    } catch (e) {
      // ignore
    }
    changedTasks.value.clear()
    pendingChanges.value = 0
    message.success(`成功保存 ${tasks.length} 项任务修改`)
  } catch (error) {
    message.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

// 监听任务数据变化
watch([() => props.tasks, () => props.flatTasks], () => {
  if (ganttInitialized) {
    loadTasks()

    if (baselinePanelVisible.value && selectedTaskBaseline.taskId != null) {
      nextTick(() => {
        try {
          const task = gantt.getTask(selectedTaskBaseline.taskId)
          syncSelectedTaskBaseline(task)
        } catch (e) {
          handleBaselinePanelClose()
          resetSelectedTaskBaseline()
        }
      })
    }
  }
}, { deep: true })

// 监听 active 变化
watch(() => props.active, (isActive) => {
  if (isActive) {
    nextTick(() => {
      if (!ganttInitialized) {
        initGantt()
      } else {
        gantt.render()
      }
    })
  }
}, { immediate: true })

// 监听基线参数变化
watch(() => props.baseline, () => {
  if (ganttInitialized) nextTick(() => renderProjectBaselineBand())
}, { deep: true })

watch(() => props.showBaseline, () => {
  if (ganttInitialized) nextTick(() => renderProjectBaselineBand())
})

watch(() => props.showTaskBaselines, () => {
  if (ganttInitialized) nextTick(() => renderTaskBaselines())
})

// 对外暴露方法
defineExpose({
  refresh: loadTasks,
  saveChanges: handleSaveChanges
})

onMounted(() => {
  if (props.active) {
    nextTick(() => {
      if (!ganttInitialized) {
        initGantt()
      }
    })
  }
})

onBeforeUnmount(() => {
  try {
    const scrollState = gantt.getScrollState ? gantt.getScrollState() : null
    persistTimelineScrollX(scrollState?.x)
  } catch (e) {
    // ignore
  }
  resetSelectedTaskBaseline()
  // 清理项目基线带
  if (baselineBandEl && baselineBandEl.parentNode) {
    baselineBandEl.parentNode.removeChild(baselineBandEl)
    baselineBandEl = null
  }
  if (ganttInitialized) {
    gantt.clearAll()
  }
})
</script>

<style>
/* ========================
   甘特图全局样式（非 scoped，dhtmlx-gantt 需要全局样式覆盖）
   ======================== */

.gantt-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 500px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  overflow: hidden;
  background: #fff;
}

/* 工具栏 */
.gantt-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #fafafa;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 4px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-icon {
  font-size: 14px;
  line-height: 1;
}

/* 甘特图容器 */
.gantt-container {
  flex: 1;
  width: 100%;
  min-height: 400px;
}

.baseline-panel-summary {
  margin-bottom: 16px;
  padding: 12px;
  background: #fafafa;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
}

.baseline-panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 8px;
}

.baseline-panel-meta {
  font-size: 13px;
  line-height: 1.8;
  color: #595959;
}

.baseline-panel-actions {
  margin-bottom: 16px;
}

.baseline-panel-tip {
  margin-bottom: 16px;
}

.baseline-panel-footer {
  display: flex;
  justify-content: flex-end;
}

/* ========================
   dhtmlx-gantt 主题覆盖
   ======================== */

/* 头部刻度 */
.gantt_scale_line {
  border-bottom: 1px solid #e8e8e8 !important;
}

.gantt_scale_cell {
  color: #595959 !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  border-right: 1px solid #f0f0f0 !important;
}

/* 网格区域 */
.gantt_grid_head_cell {
  color: #262626 !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  background: #fafafa !important;
  border-bottom: 1px solid #e8e8e8 !important;
}

.gantt_grid_data .gantt_cell {
  color: #434343 !important;
  font-size: 13px !important;
  border-bottom: 1px solid #f5f5f5 !important;
  border-right: 1px solid #f0f0f0 !important;
}

.gantt_tree_content {
  overflow: hidden;
  text-overflow: ellipsis;
}

.gantt_row {
  border-bottom: 1px solid #f5f5f5 !important;
}

.gantt_row:hover,
.gantt_row.odd:hover {
  background: #e6f7ff !important;
}

.gantt_row.odd {
  background: #fafafa !important;
}

.gantt_row.gantt_selected,
.gantt_row.odd.gantt_selected {
  background: #bae7ff !important;
}

/* 任务条 - 默认样式 */
.gantt_task_line {
  border-radius: 4px !important;
  border: none !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12) !important;
}

.gantt_task_line .gantt_task_content {
  color: #fff !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.15) !important;
}

/* 进度条 */
.gantt_task_progress {
  border-radius: 4px !important;
  opacity: 0.3 !important;
  background: rgba(255, 255, 255, 0.4) !important;
}

.gantt-progress-text {
  font-size: 11px;
  color: #fff;
}

/* 拖拽手柄 */
.gantt_task_drag {
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.2s;
}

.gantt_task_line:hover .gantt_task_drag {
  visibility: visible;
  opacity: 0.6;
}

/* 任务条颜色由 task.color 内联设置，不需要额外 CSS 类 */

/* 今日标记线 */
.today-marker .gantt_marker_content {
  background: #ff4d4f !important;
  color: #fff !important;
  font-size: 11px !important;
  padding: 2px 6px !important;
  border-radius: 2px !important;
}

.today-marker {
  background: #ff4d4f !important;
  width: 2px !important;
  opacity: 0.7 !important;
}

/* 阶段标签 */
.gantt-phase-tag {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 11px;
  line-height: 18px;
  white-space: nowrap;
}

/* 提示框 */
.gantt_tooltip {
  background: #fff !important;
  border: 1px solid #e8e8e8 !important;
  border-radius: 6px !important;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.12) !important;
  padding: 10px 14px !important;
  font-size: 12px !important;
  color: #434343 !important;
  max-width: 280px !important;
}

.gantt-tooltip-content .tooltip-title {
  font-weight: 600;
  font-size: 13px;
  color: #262626;
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid #f0f0f0;
}

.gantt-tooltip-content .tooltip-info {
  line-height: 1.8;
  color: #595959;
}

/* 连接线 — 可交互 */
.gantt_task_link .gantt_line_wrapper {
  opacity: 0.5;
  transition: opacity 0.2s;
}

.gantt_task_link:hover .gantt_line_wrapper {
  opacity: 1;
}

/* 增加连线点击区域 */
.gantt-link-interactive .gantt_line_wrapper div {
  cursor: pointer !important;
}

/* 连线高亮色 */
.gantt_task_link:hover .gantt_line_wrapper div {
  background-color: #1890ff !important;
}

.gantt_task_link:hover .gantt_link_arrow {
  border-color: #1890ff !important;
}

/* 连线拖拽端点 */
.gantt_link_control {
  opacity: 0;
  transition: opacity 0.15s;
}

.gantt_task_line:hover .gantt_link_control {
  opacity: 1;
}

.gantt_link_control .gantt_link_point {
  background: #1890ff !important;
  border: 2px solid #fff !important;
  box-shadow: 0 0 3px rgba(0, 0, 0, 0.3) !important;
  width: 10px !important;
  height: 10px !important;
  border-radius: 50% !important;
  cursor: crosshair !important;
}

/* 连线拖拽高亮 */
.gantt_link_direction {
  border-color: #1890ff !important;
}

/* 滚动条美化 */
.gantt_ver_scroll,
.gantt_hor_scroll {
  background: #f5f5f5 !important;
}

.gantt_ver_scroll::-webkit-scrollbar,
.gantt_hor_scroll::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.gantt_ver_scroll::-webkit-scrollbar-thumb,
.gantt_hor_scroll::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 4px;
}

.gantt_ver_scroll::-webkit-scrollbar-thumb:hover,
.gantt_hor_scroll::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}

/* 分隔线 */
.gantt_grid_column_resize_wrap {
  cursor: col-resize;
}

/* 拖拽时的行高亮 */
.gantt_drag_marker {
  opacity: 0.6 !important;
}

.gantt_drag_marker .gantt_row {
  border: 2px dashed #1890ff !important;
  background: #e6f7ff !important;
}

/* 基线样式 */
.gantt_task_baseline {
  position: absolute;
  z-index: 1;
  border-radius: 4px;
  opacity: 0.2;
}

.gantt_task_baseline_line {
  position: absolute;
  z-index: 1;
  border-radius: 4px;
  opacity: 0.4;
}

/* 隐藏基线任务的默认文本 */
.gantt_task_baseline .gantt_task_content {
  display: none;
}

/* 项目周期基线带 */
.project-baseline-band {
  position: absolute;
  top: 0;
  bottom: 0;
  background: rgba(24, 144, 255, 0.08);
  border-left: 1px dashed #1890ff;
  border-right: 1px dashed #1890ff;
  pointer-events: none;
  z-index: 1;
}

.project-baseline-band::after {
  content: attr(data-label);
  position: sticky;
  left: 6px;
  top: 6px;
  display: inline-block;
  padding: 1px 6px;
  font-size: 11px;
  line-height: 16px;
  color: #0958d9;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #91caff;
  border-radius: 3px;
  white-space: nowrap;
}

/* 任务级基线条 */
.gantt-task-baseline-bar {
  position: absolute;
  height: 4px;
  border-radius: 3px;
  background: #000;
  border: 1px solid #000;
  box-sizing: border-box;
  pointer-events: none;
  z-index: 5;
  opacity: 0.5;
}

.ant-drawer-content-wrapper {
  max-width: calc(100vw - 48px);
}
</style>
