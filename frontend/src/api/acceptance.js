import request from './request'

// ===== 验收管理 =====
export const getAcceptances = (params) => request.get('/acceptances/acceptances/', { params })
export const getAcceptance = (id) => request.get(`/acceptances/acceptances/${id}/`)
export const createAcceptance = (data) => request.post('/acceptances/acceptances/', data)
export const updateAcceptance = (id, data) => request.put(`/acceptances/acceptances/${id}/`, data)
export const deleteAcceptance = (id) => request.delete(`/acceptances/acceptances/${id}/`)

// ===== 别名，供组件引用 =====
export const getAcceptanceList = getAcceptances
export const getAcceptanceDetail = getAcceptance
export const submitAcceptance = (id) => request.post(`/acceptances/acceptances/${id}/`, { acceptance_status: 'IN_PROGRESS' })
export const confirmAcceptance = (id) => request.post(`/acceptances/acceptances/${id}/`, { acceptance_status: 'COMPLETED' })
