import request from './request'

// ===== 项目管理 =====
export const getProjects = (params) => request.get('/projects/projects/', { params })
export const getProjectList = getProjects  // 别名，供组件引用
export const getProject = (id) => request.get(`/projects/projects/${id}/`)
export const createProject = (data) => request.post('/projects/projects/', data)
export const updateProject = (id, data) => request.put(`/projects/projects/${id}/`, data)
export const partialUpdateProject = (id, data) => request.patch(`/projects/projects/${id}/`, data)
export const deleteProject = (id) => request.delete(`/projects/projects/${id}/`)

// ===== 项目任务 =====
export const getProjectTasks = (params) => request.get('/projects/project-tasks/', { params })
export const getProjectTask = (id) => request.get(`/projects/project-tasks/${id}/`)
export const createProjectTask = (data) => request.post('/projects/project-tasks/', data)
export const updateProjectTask = (id, data) => request.put(`/projects/project-tasks/${id}/`, data)
export const deleteProjectTask = (id) => request.delete(`/projects/project-tasks/${id}/`)

// ===== 项目成员 =====
export const getProjectMembers = (params) => request.get('/projects/project-members/', { params })
export const getProjectMember = (id) => request.get(`/projects/project-members/${id}/`)
export const createProjectMember = (data) => request.post('/projects/project-members/', data)
export const updateProjectMember = (id, data) => request.put(`/projects/project-members/${id}/`, data)
export const deleteProjectMember = (id) => request.delete(`/projects/project-members/${id}/`)

// ===== 实际工时 =====
export const getActualHours = (params) => request.get('/projects/actual-hours/', { params })
export const getActualHour = (id) => request.get(`/projects/actual-hours/${id}/`)

// ===== 执行模块别名 =====
export const getExecutionList = getProjects  // 执行列表复用项目列表
export const getExecutionDetail = getProject  // 执行详情复用项目详情
export const updateTaskProgress = (id, data) => request.patch(`/plans/plan-tasks/${id}/`, data)  // 更新任务进度
