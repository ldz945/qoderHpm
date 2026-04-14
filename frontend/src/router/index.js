import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/dashboard/Index.vue'), meta: { title: '看板' } },
      // 主数据
      { path: 'master-data/employees', name: 'EmployeeList', component: () => import('@/views/masterData/EmployeeList.vue'), meta: { title: '员工管理' } },
      { path: 'master-data/resources', name: 'ResourceList', component: () => import('@/views/masterData/ResourceList.vue'), meta: { title: '资源管理' } },
      { path: 'master-data/prices', name: 'PriceList', component: () => import('@/views/masterData/PriceList.vue'), meta: { title: '价格管理' } },
      // 项目
      { path: 'project/list', name: 'ProjectList', component: () => import('@/views/project/ProjectList.vue'), meta: { title: '项目立项' } },
      { path: 'project/detail/:id', name: 'ProjectDetail', component: () => import('@/views/project/ProjectDetail.vue'), meta: { title: '项目详情' } },
      // 计划
      { path: 'plan/list', name: 'PlanList', component: () => import('@/views/plan/PlanList.vue'), meta: { title: '项目计划' } },
      { path: 'plan/edit/:id', name: 'PlanEdit', component: () => import('@/views/plan/PlanEdit.vue'), meta: { title: '计划编辑' } },
      { path: 'plan/reserve', name: 'ResourceReserve', component: () => import('@/views/plan/ResourceReserve.vue'), meta: { title: '资源预占' } },
      // 执行
      { path: 'execution/list', name: 'ExecutionList', component: () => import('@/views/execution/ExecutionList.vue'), meta: { title: '项目执行' } },
      { path: 'execution/detail/:id', name: 'ExecutionDetail', component: () => import('@/views/execution/ExecutionDetail.vue'), meta: { title: '执行详情' } },
      // 变更
      { path: 'change/list', name: 'ChangeList', component: () => import('@/views/change/ChangeList.vue'), meta: { title: '变更管理' } },
      { path: 'change/form/:id?', name: 'ChangeForm', component: () => import('@/views/change/ChangeForm.vue'), meta: { title: '变更单' } },
      // 验收
      { path: 'acceptance/list', name: 'AcceptanceList', component: () => import('@/views/acceptance/AcceptanceList.vue'), meta: { title: '验收管理' } },
      { path: 'acceptance/form/:id?', name: 'AcceptanceForm', component: () => import('@/views/acceptance/AcceptanceForm.vue'), meta: { title: '验收单' } },
      // 辅助功能
      { path: 'issue/list', name: 'IssueList', component: () => import('@/views/issue/IssueList.vue'), meta: { title: '问题/风险' } },
      { path: 'issue/form/:id?', name: 'IssueForm', component: () => import('@/views/issue/IssueForm.vue'), meta: { title: '问题/风险' } },
      { path: 'seven-step/list', name: 'SevenStepList', component: () => import('@/views/sevenStep/SevenStepList.vue'), meta: { title: '七步法' } },
      { path: 'seven-step/form/:id?', name: 'SevenStepForm', component: () => import('@/views/sevenStep/SevenStepForm.vue'), meta: { title: '七步法' } },
      { path: 'document/list', name: 'DocumentTree', component: () => import('@/views/document/DocumentTree.vue'), meta: { title: '文档管理' } },
      { path: 'vpp/list', name: 'VppList', component: () => import('@/views/vpp/VppList.vue'), meta: { title: 'VPP管理' } },
      { path: 'vpp/detail/:id', name: 'VppDetail', component: () => import('@/views/vpp/VppDetail.vue'), meta: { title: 'VPP详情' } },
      { path: 'scorecard/list', name: 'ScorecardList', component: () => import('@/views/scorecard/ScorecardList.vue'), meta: { title: '积分卡' } },
      { path: 'scorecard/edit/:id?', name: 'ScorecardEdit', component: () => import('@/views/scorecard/ScorecardEdit.vue'), meta: { title: '积分卡编辑' } },
      { path: 'meeting/list', name: 'MeetingList', component: () => import('@/views/meeting/MeetingList.vue'), meta: { title: '会议管理' } },
      { path: 'meeting/form/:id?', name: 'MeetingForm', component: () => import('@/views/meeting/MeetingForm.vue'), meta: { title: '会议' } },
      { path: 'action-item/list', name: 'ActionItemList', component: () => import('@/views/meeting/ActionItemList.vue'), meta: { title: '行动项' } },
      { path: 'expense/list', name: 'ExpenseList', component: () => import('@/views/expense/ExpenseList.vue'), meta: { title: '杂项费用' } },
      { path: 'expense/form/:id?', name: 'ExpenseForm', component: () => import('@/views/expense/ExpenseForm.vue'), meta: { title: '杂项费用' } },
      { path: 'scope/list', name: 'ScopeList', component: () => import('@/views/scope/ScopeList.vue'), meta: { title: '项目范围' } },
      { path: 'scope/form/:id?', name: 'ScopeForm', component: () => import('@/views/scope/ScopeForm.vue'), meta: { title: '项目范围' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
