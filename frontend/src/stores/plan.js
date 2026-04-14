// 管理计划编辑状态
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePlanStore = defineStore('plan', () => {
  const currentPlanTasks = ref([])    // 当前编辑的任务列表
  const currentResources = ref([])     // 当前编辑的资源列表
  const editMode = ref(false)          // 是否编辑模式
  const planVersion = ref(null)        // 当前计划版本

  const setEditMode = (mode) => { editMode.value = mode }
  const setPlanTasks = (tasks) => { currentPlanTasks.value = tasks }
  const setResources = (resources) => { currentResources.value = resources }
  const setPlanVersion = (version) => { planVersion.value = version }
  const resetPlan = () => {
    currentPlanTasks.value = []
    currentResources.value = []
    editMode.value = false
    planVersion.value = null
  }

  return { currentPlanTasks, currentResources, editMode, planVersion, setEditMode, setPlanTasks, setResources, setPlanVersion, resetPlan }
})
