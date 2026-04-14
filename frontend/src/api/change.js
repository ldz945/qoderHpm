import request from './request'

// ===== 变更单 =====
export const getChangeOrders = (params) => request.get('/changes/change-orders/', { params })
export const getChangeOrder = (id) => request.get(`/changes/change-orders/${id}/`)
export const createChangeOrder = (data) => request.post('/changes/change-orders/', data)
export const updateChangeOrder = (id, data) => request.put(`/changes/change-orders/${id}/`, data)
export const deleteChangeOrder = (id) => request.delete(`/changes/change-orders/${id}/`)

// ===== 别名，供组件引用 =====
export const getChangeList = getChangeOrders
export const getChangeDetail = getChangeOrder
export const createChange = createChangeOrder
export const updateChange = updateChangeOrder
export const submitChange = (id) => request.post(`/changes/change-orders/${id}/`, { status: 'PENDING' })
