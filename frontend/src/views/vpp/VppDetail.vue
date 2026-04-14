<template>
  <div class="vpp-detail">
    <a-card :bordered="false">
      <!-- 顶部信息 -->
      <div class="header-section">
        <a-row :gutter="24">
          <a-col :span="16">
            <h2>VPP详情 - {{ vppData.projectName }}</h2>
            <p>项目编码: {{ vppData.projectCode }} | 当前版本: {{ vppData.version }} | 状态: 
              <a-tag :color="getStatusColor(vppData.status)">{{ getStatusText(vppData.status) }}</a-tag>
            </p>
          </a-col>
          <a-col :span="8" style="text-align: right;">
            <a-button type="primary" @click="handleSave" :loading="saveLoading">保存(升级版本)</a-button>
            <a-dropdown style="margin-left: 8px;">
              <a-button>
                导出 <DownOutlined />
              </a-button>
              <template #overlay>
                <a-menu @click="handleExport">
                  <a-menu-item key="main">导出主表</a-menu-item>
                  <a-menu-item key="history">导出版本记录</a-menu-item>
                  <a-menu-item key="all">导出主表+版本记录</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
            <a-button style="margin-left: 8px" @click="handleAuthorize">授权</a-button>
          </a-col>
        </a-row>
      </div>

      <a-divider />

      <!-- 版本历史 -->
      <div class="version-section">
        <h3>版本历史</h3>
        <a-timeline mode="left">
          <a-timeline-item
            v-for="version in versionHistory"
            :key="version.id"
            :color="version.version === vppData.version ? 'blue' : 'gray'"
          >
            <template #label>
              <span :style="{ fontWeight: version.version === vppData.version ? 'bold' : 'normal' }">
                V{{ version.version }}
              </span>
            </template>
            <div class="version-item">
              <p>更新人: {{ version.updatedByName }} | 更新时间: {{ version.updatedAt }}</p>
              <p>说明: {{ version.description || '-' }}</p>
            </div>
          </a-timeline-item>
        </a-timeline>
      </div>

      <a-divider />

      <!-- VPP内容编辑区 -->
      <div class="content-section">
        <h3>VPP内容</h3>
        <a-table
          :columns="contentColumns"
          :data-source="vppContent"
          :pagination="false"
          row-key="id"
          bordered
        >
          <template #bodyCell="{ column, record, index }">
            <template v-if="column.key === 'seq'">
              {{ index + 1 }}
            </template>
            <template v-if="column.key === 'item'">
              <a-input v-model:value="record.item" placeholder="请输入项目" />
            </template>
            <template v-if="column.key === 'description'">
              <a-textarea v-model:value="record.description" :rows="2" placeholder="请输入描述" />
            </template>
            <template v-if="column.key === 'responsible'">
              <a-select
                v-model:value="record.responsible"
                placeholder="请选择负责人"
                style="width: 100%"
                show-search
                :filter-option="filterOption"
              >
                <a-select-option v-for="item in employeeList" :key="item.id" :value="item.id">
                  {{ item.name }}
                </a-select-option>
              </a-select>
            </template>
            <template v-if="column.key === 'planDate'">
              <a-date-picker v-model:value="record.planDate" style="width: 100%" placeholder="请选择计划日期" />
            </template>
            <template v-if="column.key === 'actualDate'">
              <a-date-picker v-model:value="record.actualDate" style="width: 100%" placeholder="请选择实际日期" />
            </template>
            <template v-if="column.key === 'status'">
              <a-select v-model:value="record.status" placeholder="请选择状态" style="width: 100%">
                <a-select-option value="not_started">未开始</a-select-option>
                <a-select-option value="in_progress">进行中</a-select-option>
                <a-select-option value="completed">已完成</a-select-option>
                <a-select-option value="delayed">延期</a-select-option>
              </a-select>
            </template>
            <template v-if="column.key === 'remark'">
              <a-input v-model:value="record.remark" placeholder="请输入备注" />
            </template>
            <template v-if="column.key === 'action'">
              <a-button type="link" danger @click="handleDeleteRow(index)">
                <DeleteOutlined />
              </a-button>
            </template>
          </template>
        </a-table>
        <div class="add-row-btn">
          <a-button type="dashed" block @click="handleAddRow">
            <PlusOutlined /> 新增行
          </a-button>
        </div>
      </div>
    </a-card>

    <!-- 授权弹窗 -->
    <a-modal
      v-model:open="authorizeModalVisible"
      title="授权管理"
      @ok="handleAuthorizeOk"
      @cancel="handleAuthorizeCancel"
    >
      <a-form layout="vertical">
        <a-form-item label="选择授权人">
          <a-select
            v-model:value="authorizedUsers"
            mode="multiple"
            placeholder="请选择授权人"
            style="width: 100%"
            show-search
            :filter-option="filterOption"
          >
            <a-select-option v-for="item in employeeList" :key="item.id" :value="item.id">
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { DownOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { getVpp, updateVpp } from '@/api/auxiliary'
import { getEmployees } from '@/api/masterData'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const vppId = computed(() => route.params.id)

// VPP数据
const vppData = reactive({
  projectCode: '',
  projectName: '',
  version: '1.0',
  status: 'draft'
})

// 版本历史
const versionHistory = ref([])

// VPP内容
const vppContent = ref([])

// 员工列表
const employeeList = ref([])

// 保存加载
const saveLoading = ref(false)

// 授权弹窗
const authorizeModalVisible = ref(false)
const authorizedUsers = ref([])

// 内容列定义
const contentColumns = [
  { title: '序号', key: 'seq', width: 60, align: 'center' },
  { title: '项目', key: 'item', width: 150 },
  { title: '描述', key: 'description', width: 200 },
  { title: '负责人', key: 'responsible', width: 120 },
  { title: '计划日期', key: 'planDate', width: 140 },
  { title: '实际日期', key: 'actualDate', width: 140 },
  { title: '状态', key: 'status', width: 100 },
  { title: '备注', key: 'remark', width: 150 },
  { title: '操作', key: 'action', width: 60, fixed: 'right' }
]

// 状态颜色映射
const getStatusColor = (status) => {
  const colorMap = {
    draft: 'default',
    active: 'processing',
    archived: 'success'
  }
  return colorMap[status] || 'default'
}

// 状态文本映射
const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    active: '生效中',
    archived: '已归档'
  }
  return textMap[status] || status
}

// 加载VPP详情
const loadVppDetail = async () => {
  try {
    const res = await getVpp(vppId.value)
    Object.assign(vppData, res)
    versionHistory.value = res.versionHistory || []
    vppContent.value = res.content?.map(item => ({
      ...item,
      planDate: item.planDate ? dayjs(item.planDate) : null,
      actualDate: item.actualDate ? dayjs(item.actualDate) : null
    })) || []
    authorizedUsers.value = res.authorizedUsers || []
  } catch (error) {
    message.error('加载VPP详情失败')
  }
}

// 加载员工列表
const loadEmployees = async () => {
  try {
    const res = await getEmployees({ page_size: 9999 })
    employeeList.value = res.results || []
  } catch (error) {
    console.error('加载员工失败', error)
  }
}

// 筛选选项
const filterOption = (input, option) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

// 新增行
const handleAddRow = () => {
  vppContent.value.push({
    id: Date.now(),
    item: '',
    description: '',
    responsible: undefined,
    planDate: null,
    actualDate: null,
    status: 'not_started',
    remark: ''
  })
}

// 删除行
const handleDeleteRow = (index) => {
  vppContent.value.splice(index, 1)
}

// 保存
const handleSave = async () => {
  saveLoading.value = true
  try {
    const submitData = {
      content: vppContent.value.map(item => ({
        ...item,
        planDate: item.planDate ? dayjs(item.planDate).format('YYYY-MM-DD') : null,
        actualDate: item.actualDate ? dayjs(item.actualDate).format('YYYY-MM-DD') : null
      })),
      authorizedUsers: authorizedUsers.value
    }
    await updateVpp(vppId.value, submitData)
    message.success('保存成功，版本已升级')
    loadVppDetail()
  } catch (error) {
    message.error('保存失败')
  } finally {
    saveLoading.value = false
  }
}

// 导出
const handleExport = ({ key }) => {
  const exportType = {
    main: '主表',
    history: '版本记录',
    all: '主表+版本记录'
  }
  message.info(`导出${exportType[key]}功能开发中`)
}

// 授权
const handleAuthorize = () => {
  authorizeModalVisible.value = true
}

// 授权确认
const handleAuthorizeOk = async () => {
  try {
    await updateVpp(vppId.value, { authorizedUsers: authorizedUsers.value })
    message.success('授权成功')
    authorizeModalVisible.value = false
  } catch (error) {
    message.error('授权失败')
  }
}

// 授权取消
const handleAuthorizeCancel = () => {
  authorizeModalVisible.value = false
}

onMounted(() => {
  loadVppDetail()
  loadEmployees()
})
</script>

<style scoped>
.vpp-detail {
  padding: 24px;
}

.header-section {
  margin-bottom: 16px;
}

.version-section {
  margin-bottom: 24px;
}

.version-item {
  font-size: 12px;
  color: #666;
}

.version-item p {
  margin: 0;
}

.content-section {
  margin-top: 24px;
}

.add-row-btn {
  margin-top: 16px;
}
</style>
