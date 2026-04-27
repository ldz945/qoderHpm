import request from './request'

export const login = (data) => request.post('/auth/login/', data)
export const refreshToken = (data) => request.post('/auth/refresh/', data)
export const getCurrentUser = () => request.get('/auth/me/')
export const getRoles = () => request.get('/auth/roles/')

// User management
export const getUsers = () => request.get('/users/')
export const createUser = (data) => request.post('/users/', data)
export const updateUser = (id, data) => request.patch(`/users/${id}/`, data)
export const deleteUser = (id) => request.delete(`/users/${id}/`)
export const setUserRole = (id, roles) => request.post(`/users/${id}/set_role/`, { roles })
export const resetUserPassword = (userId, password) => request.post('/users/reset_password/', { user_id: userId, password })

