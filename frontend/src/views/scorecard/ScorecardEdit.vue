<template>
  <div class="scorecard-edit">
    <a-card :bordered="false">
      <!-- 头部信息 -->
      <div class="header-section">
        <a-row :gutter="24">
          <a-col :span="16">
            <h2>积分卡编辑 - {{ scorecardData.projectName }}</h2>
            <p>
              项目编码: {{ scorecardData.projectCode }} | 
              模板类型: <a-tag :color="scorecardData.templateType === 'L1' ? 'blue' : 'green'">{{ scorecardData.templateType }}</a-tag> | 
              总分: <strong>{{ totalScore }}</strong>
            </p>
          </a-col>
          <a-col :span="8" style="text-align: right;">
            <a-button type="primary" @click="handleSave" :loading="saveLoading">保存</a-button>
            <a-dropdown style="margin-left: 8px;">
              <a-button>
                导出 <DownOutlined />
              </a-button>
              <template #overlay>
                <a-menu @click="handleExport">
                  <template v-if="scorecardData.templateType === 'L1'">
                    <a-menu-item key="all">导出全部</a-menu-item>
                  </template>
                  <template v-else>
                    <a-menu-item key="phase1">导出阶段1</a-menu-item>
                    <a-menu-item key="phase2">导出阶段2</a-menu-item>
                    <a-menu-item key="phase3">导出阶段3</a-menu-item>
                    <a-menu-item key="all">导出全部</a-menu-item>
                  </template>
                </a-menu>
              </template>
            </a-dropdown>
            <a-button style="margin-left: 8px" @click="handleAuthorize">授权</a-button>
          </a-col>
        </a-row>
      </div>

      <a-divider />

      <!-- L1模板：单页表单 -->
      <template v-if="scorecardData.templateType === 'L1'">
        <a-table
          :columns="scoreColumns"
          :data-source="scoreItems"
          :pagination="false"
          row-key="id"
          bordered
        >
          <template #bodyCell="{ column, record, index }">
            <template v-if="column.key === 'seq'">
              {{ index + 1 }}
            </template>
            <template v-if="column.key === 'category'">
              <a-input v-model:value="record.category" placeholder="请输入类别" />
            </template>
            <template v-if="column.key === 'item'">
              <a-input v-model:value="record.item" placeholder="请输入评分项" />
            </template>
            <template v-if="column.key === 'description'">
              <a-textarea v-model:value="record.description" :rows="2" placeholder="请输入描述" />
            </template>
            <template v-if="column.key === 'weight'">
              <a-input-number v-model:value="record.weight" :min="0" :max="100" style="width: 100%" />
            </template>
            <template v-if="column.key === 'score'">
              <a-input-number v-model:value="record.score" :min="0" :max="record.weight || 100" style="width: 100%" />
            </template>
            <template v-if="column.key === 'remark'">
              <a-input v-model:value="record.remark" placeholder="请输入备注" />
            </template>
            <template v-if="column.key === 'action'">
              <a-button type="link" danger @click="handleDeleteItem(index)">
                <DeleteOutlined />
              </a-button>
            </template>
          </template>
        </a-table>
        <div class="add-row-btn">
          <a-button type="dashed" block @click="handleAddItem">
            <PlusOutlined /> 新增评分项
          </a-button>
        </div>
      </template>

      <!-- L2模板：3个Tab页 -->
      <template v-else>
        <a-tabs v-model:activeKey="activeTabKey">
          <a-tab-pane key="phase1" tab="阶段1">
            <a-table
              :columns="scoreColumns"
              :data-source="phase1Items"
              :pagination="false"
              row-key="id"
              bordered
            >
              <template #bodyCell="{ column, record, index }">
                <template v-if="column.key === 'seq'">
                  {{ index + 1 }}
                </template>
                <template v-if="column.key === 'category'">
                  <a-input v-model:value="record.category" placeholder="请输入类别" />
                </template>
                <template v-if="column.key === 'item'">
                  <a-input v-model:value="record.item" placeholder="请输入评分项" />
                </template>
                <template v-if="column.key === 'description'">
                  <a-textarea v-model:value="record.description" :rows="2" placeholder="请输入描述" />
                </template>
                <template v-if="column.key === 'weight'">
                  <a-input-number v-model:value="record.weight" :min="0" :max="100" style="width: 100%" />
                </template>
                <template v-if="column.key === 'score'">
                  <a-input-number v-model:value="record.score" :min="0" :max="record.weight || 100" style="width: 100%" />
                </template>
                <template v-if="column.key === 'remark'">
                  <a-input v-model:value="record.remark" placeholder="请输入备注" />
                </template>
                <template v-if="column.key === 'action'">
                  <a-button type="link" danger @click="handleDeletePhaseItem('phase1', index)">
                    <DeleteOutlined />
                  </a-button>
                </template>
              </template>
            </a-table>
            <div class="add-row-btn">
              <a-button type="dashed" block @click="handleAddPhaseItem('phase1')">
                <PlusOutlined /> 新增评分项
              </a-button>
            </div>
          </a-tab-pane>

          <a-tab-pane key="phase2" tab="阶段2">
            <a-table
              :columns="scoreColumns"
              :data-source="phase2Items"
              :pagination="false"
              row-key="id"
              bordered
            >
              <template #bodyCell="{ column, record, index }">
                <template v-if="column.key === 'seq'">
                  {{ index + 1 }}
                </template>
                <template v-if="column.key === 'category'">
                  <a-input v-model:value="record.category" placeholder="请输入类别" />
                </template>
                <template v-if="column.key === 'item'">
                  <a-input v-model:value="record.item" placeholder="请输入评分项" />
                </template>
                <template v-if="column.key === 'description'">
                  <a-textarea v-model:value="record.description" :rows="2" placeholder="请输入描述" />
                </template>
                <template v-if="column.key === 'weight'">
                  <a-input-number v-model:value="record.weight" :min="0" :max="100" style="width: 100%" />
                </template>
                <template v-if="column.key === 'score'">
                  <a-input-number v-model:value="record.score" :min="0" :max="record.weight || 100" style="width: 100%" />
                </template>
                <template v-if="column.key === 'remark'">
                  <a-input v-model:value="record.remark" placeholder="请输入备注" />
                </template>
                <template v-if="column.key === 'action'">
                  <a-button type="link" danger @click="handleDeletePhaseItem('phase2', index)">
                    <DeleteOutlined />
                  </a-button>
                </template>
              </template>
            </a-table>
            <div class="add-row-btn">
              <a-button type="dashed" block @click="handleAddPhaseItem('phase2')">
                <PlusOutlined /> 新增评分项
              </a-button>
            </div>
          </a-tab-pane>

          <a-tab-pane key="phase3" tab="阶段3">
            <a-table
              :columns="scoreColumns"
              :data-source="phase3Items"
              :pagination="false"
              row-key="id"
              bordered
            >
              <template #bodyCell="{ column, record, index }">
                <template v-if="column.key === 'seq'">
                  {{ index + 1 }}
                </template>
                <template v-if="column.key === 'category'">
                  <a-input v-model:value="record.category" placeholder="请输入类别" />
                </template>
                <template v-if="column.key === 'item'">
                  <a-input v-model:value="record.item" placeholder="请输入评分项" />
                </template>
                <template v-if="column.key === 'description'">
                  <a-textarea v-model:value="record.description" :rows="2" placeholder="请输入描述" />
                </template>
                <template v-if="column.key === 'weight'">
                  <a-input-number v-model:value="record.weight" :min="0" :max="100" style="width: 100%" />
                </template>
                <template v-if="column.key === 'score'">
                  <a-input-number v-model:value="record.score" :min="0" :max="record.weight || 100" style="width: 100%" />
                </template>
                <template v-if="column.key === 'remark'">
                  <a-input v-model:value="record.remark" placeholder="请输入备注" />
                </template>
                <template v-if="column.key === 'action'">
                  <a-button type="link" danger @click="handleDeletePhaseItem('phase3', index)">
                    <DeleteOutlined />
                  </a-button>
                </template>
              </template>
            </a-table>
            <div class="add-row-btn">
              <a-button type="dashed" block @click="handleAddPhaseItem('phase3')">
                <PlusOutlined /> 新增评分项
              </a-button>
            </div>
          </a-tab-pane>
        </a-tabs>
      </template>
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
import { getScorecard, updateScorecard } from '@/api/auxiliary'
import { getEmployees } from '@/api/masterData'

const route = useRoute()
const router = useRouter()

const scorecardId = computed(() => route.params.id)

// 积分卡数据
const scorecardData = reactive({
  projectCode: '',
  projectName: '',
  templateType: 'L1'
})

// L1评分项
const scoreItems = ref([])

// L2各阶段评分项
const phase1Items = ref([])
const phase2Items = ref([])
const phase3Items = ref([])

// 当前Tab
const activeTabKey = ref('phase1')

// 员工列表
const employeeList = ref([])

// 保存加载
const saveLoading = ref(false)

// 授权弹窗
const authorizeModalVisible = ref(false)
const authorizedUsers = ref([])

// 评分列定义
const scoreColumns = [
  { title: '序号', key: 'seq', width: 60, align: 'center' },
  { title: '类别', key: 'category', width: 120 },
  { title: '评分项', key: 'item', width: 200 },
  { title: '描述', key: 'description', width: 250 },
  { title: '权重', key: 'weight', width: 80 },
  { title: '得分', key: 'score', width: 80 },
  { title: '备注', key: 'remark', width: 150 },
  { title: '操作', key: 'action', width: 60, fixed: 'right' }
]

// 计算总分
const totalScore = computed(() => {
  if (scorecardData.templateType === 'L1') {
    const total = scoreItems.value.reduce((sum, item) => sum + (item.score || 0), 0)
    const weight = scoreItems.value.reduce((sum, item) => sum + (item.weight || 0), 0)
    return weight > 0 ? Math.round((total / weight) * 100) : 0
  } else {
    const p1 = phase1Items.value.reduce((sum, item) => sum + (item.score || 0), 0)
    const p2 = phase2Items.value.reduce((sum, item) => sum + (item.score || 0), 0)
    const p3 = phase3Items.value.reduce((sum, item) => sum + (item.score || 0), 0)
    const total = p1 + p2 + p3
    const count = phase1Items.value.length + phase2Items.value.length + phase3Items.value.length
    return count > 0 ? Math.round(total / count) : 0
  }
})

// 加载积分卡详情
const loadScorecardDetail = async () => {
  try {
    const res = await getScorecard(scorecardId.value)
    Object.assign(scorecardData, res)
    
    if (res.templateType === 'L1') {
      scoreItems.value = res.items || []
    } else {
      phase1Items.value = res.phase1Items || []
      phase2Items.value = res.phase2Items || []
      phase3Items.value = res.phase3Items || []
    }
    
    authorizedUsers.value = res.authorizedUsers || []
  } catch (error) {
    message.error('加载积分卡详情失败')
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

// L1新增评分项
const handleAddItem = () => {
  scoreItems.value.push({
    id: Date.now(),
    category: '',
    item: '',
    description: '',
    weight: 0,
    score: 0,
    remark: ''
  })
}

// L1删除评分项
const handleDeleteItem = (index) => {
  scoreItems.value.splice(index, 1)
}

// L2新增阶段评分项
const handleAddPhaseItem = (phase) => {
  const newItem = {
    id: Date.now(),
    category: '',
    item: '',
    description: '',
    weight: 0,
    score: 0,
    remark: ''
  }
  
  if (phase === 'phase1') phase1Items.value.push(newItem)
  else if (phase === 'phase2') phase2Items.value.push(newItem)
  else if (phase === 'phase3') phase3Items.value.push(newItem)
}

// L2删除阶段评分项
const handleDeletePhaseItem = (phase, index) => {
  if (phase === 'phase1') phase1Items.value.splice(index, 1)
  else if (phase === 'phase2') phase2Items.value.splice(index, 1)
  else if (phase === 'phase3') phase3Items.value.splice(index, 1)
}

// 保存
const handleSave = async () => {
  saveLoading.value = true
  try {
    const submitData = {
      totalScore: totalScore.value,
      authorizedUsers: authorizedUsers.value
    }
    
    if (scorecardData.templateType === 'L1') {
      submitData.items = scoreItems.value
    } else {
      submitData.phase1Items = phase1Items.value
      submitData.phase2Items = phase2Items.value
      submitData.phase3Items = phase3Items.value
    }
    
    await updateScorecard(scorecardId.value, submitData)
    message.success('保存成功')
  } catch (error) {
    message.error('保存失败')
  } finally {
    saveLoading.value = false
  }
}

// 导出
const handleExport = ({ key }) => {
  const exportType = {
    phase1: '阶段1',
    phase2: '阶段2',
    phase3: '阶段3',
    all: '全部'
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
    await updateScorecard(scorecardId.value, { authorizedUsers: authorizedUsers.value })
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
  loadScorecardDetail()
  loadEmployees()
})
</script>

<style scoped>
.scorecard-edit {
  padding: 24px;
}

.header-section {
  margin-bottom: 16px;
}

.add-row-btn {
  margin-top: 16px;
}
</style>
