import request from './request'

// ===== 计划列表（项目维度） =====
export const getPlanList = (params) => request.get('/plans/plan-versions/', { params })

// ===== 计划任务 =====
export const getPlanTasks = (params) => request.get('/plans/plan-tasks/', { params })
export const getPlanTask = (id) => request.get(`/plans/plan-tasks/${id}/`)
export const createPlanTask = (data) => request.post('/plans/plan-tasks/', data)
export const updatePlanTask = (id, data) => request.put(`/plans/plan-tasks/${id}/`, data)
export const partialUpdatePlanTask = (id, data) => request.patch(`/plans/plan-tasks/${id}/`, data)
export const deletePlanTask = (id) => request.delete(`/plans/plan-tasks/${id}/`)

// ===== 资源计划 =====
export const getResourcePlans = (params) => request.get('/plans/resource-plans/', { params })
export const getResourcePlan = (id) => request.get(`/plans/resource-plans/${id}/`)
export const createResourcePlan = (data) => request.post('/plans/resource-plans/', data)
export const updateResourcePlan = (id, data) => request.put(`/plans/resource-plans/${id}/`, data)
export const deleteResourcePlan = (id) => request.delete(`/plans/resource-plans/${id}/`)

// ===== 资源预留 =====
export const getResourceReserves = (params) => request.get('/plans/resource-reserves/', { params })
export const getResourceReserve = (id) => request.get(`/plans/resource-reserves/${id}/`)
export const createResourceReserve = (data) => request.post('/plans/resource-reserves/', data)
export const updateResourceReserve = (id, data) => request.put(`/plans/resource-reserves/${id}/`, data)
export const deleteResourceReserve = (id) => request.delete(`/plans/resource-reserves/${id}/`)

// ===== 任务批量更新（甘特图用） =====
export const batchUpdatePlanTasks = (data) => request.post('/plans/plan-tasks/batch-update/', data)

// ===== 计划版本 =====
export const getPlanVersions = (params) => request.get('/plans/plan-versions/', { params })
export const getPlanVersion = (id) => request.get(`/plans/plan-versions/${id}/`)
export const createPlanVersion = (data) => request.post('/plans/plan-versions/', data)
export const updatePlanVersion = (id, data) => request.put(`/plans/plan-versions/${id}/`, data)
export const deletePlanVersion = (id) => request.delete(`/plans/plan-versions/${id}/`)
