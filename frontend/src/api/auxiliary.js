import request from './request'

// ===== 问题与风险 =====
export const getIssueRisks = (params) => request.get('/auxiliary/issue-risks/', { params })
export const getIssueRisk = (id) => request.get(`/auxiliary/issue-risks/${id}/`)
export const createIssueRisk = (data) => request.post('/auxiliary/issue-risks/', data)
export const updateIssueRisk = (id, data) => request.put(`/auxiliary/issue-risks/${id}/`, data)
export const deleteIssueRisk = (id) => request.delete(`/auxiliary/issue-risks/${id}/`)

// ===== 七步法 =====
export const getSevenSteps = (params) => request.get('/auxiliary/seven-steps/', { params })
export const getSevenStep = (id) => request.get(`/auxiliary/seven-steps/${id}/`)
export const createSevenStep = (data) => request.post('/auxiliary/seven-steps/', data)
export const updateSevenStep = (id, data) => request.put(`/auxiliary/seven-steps/${id}/`, data)
export const deleteSevenStep = (id) => request.delete(`/auxiliary/seven-steps/${id}/`)

// ===== VPP =====
export const getVpps = (params) => request.get('/auxiliary/vpps/', { params })
export const getVpp = (id) => request.get(`/auxiliary/vpps/${id}/`)
export const createVpp = (data) => request.post('/auxiliary/vpps/', data)
export const updateVpp = (id, data) => request.put(`/auxiliary/vpps/${id}/`, data)
export const deleteVpp = (id) => request.delete(`/auxiliary/vpps/${id}/`)

// ===== 计分卡 =====
export const getScorecards = (params) => request.get('/auxiliary/scorecards/', { params })
export const getScorecard = (id) => request.get(`/auxiliary/scorecards/${id}/`)
export const createScorecard = (data) => request.post('/auxiliary/scorecards/', data)
export const updateScorecard = (id, data) => request.put(`/auxiliary/scorecards/${id}/`, data)
export const deleteScorecard = (id) => request.delete(`/auxiliary/scorecards/${id}/`)

// ===== 会议 =====
export const getMeetings = (params) => request.get('/auxiliary/meetings/', { params })
export const getMeeting = (id) => request.get(`/auxiliary/meetings/${id}/`)
export const createMeeting = (data) => request.post('/auxiliary/meetings/', data)
export const updateMeeting = (id, data) => request.put(`/auxiliary/meetings/${id}/`, data)
export const deleteMeeting = (id) => request.delete(`/auxiliary/meetings/${id}/`)

// ===== 行动项 =====
export const getActionItems = (params) => request.get('/auxiliary/action-items/', { params })
export const getActionItem = (id) => request.get(`/auxiliary/action-items/${id}/`)
export const createActionItem = (data) => request.post('/auxiliary/action-items/', data)
export const updateActionItem = (id, data) => request.put(`/auxiliary/action-items/${id}/`, data)
export const deleteActionItem = (id) => request.delete(`/auxiliary/action-items/${id}/`)

// ===== 杂费 =====
export const getMiscExpenses = (params) => request.get('/auxiliary/misc-expenses/', { params })
export const getMiscExpense = (id) => request.get(`/auxiliary/misc-expenses/${id}/`)
export const createMiscExpense = (data) => request.post('/auxiliary/misc-expenses/', data)
export const updateMiscExpense = (id, data) => request.put(`/auxiliary/misc-expenses/${id}/`, data)
export const deleteMiscExpense = (id) => request.delete(`/auxiliary/misc-expenses/${id}/`)

// ===== 项目范围 =====
export const getProjectScopes = (params) => request.get('/auxiliary/project-scopes/', { params })
export const getProjectScope = (id) => request.get(`/auxiliary/project-scopes/${id}/`)
export const createProjectScope = (data) => request.post('/auxiliary/project-scopes/', data)
export const updateProjectScope = (id, data) => request.put(`/auxiliary/project-scopes/${id}/`, data)
export const deleteProjectScope = (id) => request.delete(`/auxiliary/project-scopes/${id}/`)

// ===== 文档 =====
export const getDocuments = (params) => request.get('/auxiliary/documents/', { params })
export const getDocument = (id) => request.get(`/auxiliary/documents/${id}/`)
export const createDocument = (data) => request.post('/auxiliary/documents/', data)
export const updateDocument = (id, data) => request.put(`/auxiliary/documents/${id}/`, data)
export const deleteDocument = (id) => request.delete(`/auxiliary/documents/${id}/`)

// ===== 文档文件 =====
export const getDocumentFiles = (params) => request.get('/auxiliary/document-files/', { params })
export const getDocumentFile = (id) => request.get(`/auxiliary/document-files/${id}/`)
export const createDocumentFile = (data) => request.post('/auxiliary/document-files/', data)
export const updateDocumentFile = (id, data) => request.put(`/auxiliary/document-files/${id}/`, data)
export const deleteDocumentFile = (id) => request.delete(`/auxiliary/document-files/${id}/`)
