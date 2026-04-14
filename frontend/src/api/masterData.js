import request from './request'

// ===== 员工管理 =====
export const getEmployees = (params) => request.get('/master-data/employees/', { params })
export const getEmployee = (id) => request.get(`/master-data/employees/${id}/`)
export const createEmployee = (data) => request.post('/master-data/employees/', data)
export const updateEmployee = (id, data) => request.put(`/master-data/employees/${id}/`, data)
export const deleteEmployee = (id) => request.delete(`/master-data/employees/${id}/`)

// ===== 资源管理 =====
export const getResources = (params) => request.get('/master-data/resources/', { params })
export const getResource = (id) => request.get(`/master-data/resources/${id}/`)
export const createResource = (data) => request.post('/master-data/resources/', data)
export const updateResource = (id, data) => request.put(`/master-data/resources/${id}/`, data)
export const deleteResource = (id) => request.delete(`/master-data/resources/${id}/`)

// ===== 价格管理 =====
export const getPriceHeaders = (params) => request.get('/master-data/price-headers/', { params })
export const getPriceHeader = (id) => request.get(`/master-data/price-headers/${id}/`)
export const createPriceHeader = (data) => request.post('/master-data/price-headers/', data)
export const updatePriceHeader = (id, data) => request.put(`/master-data/price-headers/${id}/`, data)
export const deletePriceHeader = (id) => request.delete(`/master-data/price-headers/${id}/`)

export const getPriceLines = (params) => request.get('/master-data/price-lines/', { params })
export const createPriceLine = (data) => request.post('/master-data/price-lines/', data)
export const updatePriceLine = (id, data) => request.put(`/master-data/price-lines/${id}/`, data)
export const deletePriceLine = (id) => request.delete(`/master-data/price-lines/${id}/`)
