const rolePermissions = {
  SUPER_ADMIN: ['*'],
  MD_ADMIN: [
    'master_data.employee.read', 'master_data.employee.write',
    'master_data.department.read', 'master_data.department.write',
    'master_data.resource.read', 'master_data.resource.write',
    'master_data.price.read', 'master_data.price.write',
    'menu.master_data.employees.view', 'menu.master_data.departments.view',
    'menu.master_data.resources.view', 'menu.master_data.prices.view'
  ],
  PMO: [
    'project.read', 'project.create', 'project.update', 'project.status.update', 'project.pm.update',
    'plan.task.read', 'plan.task.write', 'plan.task.batch_update',
    'plan.version.read', 'plan.version.write',
    'execution.read', 'execution.detail.read', 'execution.actual_hours.read',
    'master_data.department.read', 'master_data.employee.read',
    'master_data.resource.read', 'master_data.price.read',
    'menu.project.list.view', 'menu.plan.list.view', 'menu.execution.view'
  ],
  PROJECT_MANAGER: [
    'project.read', 'project.create', 'project.update', 'project.status.update',
    'plan.task.read', 'plan.task.write', 'plan.task.batch_update',
    'plan.version.read', 'plan.version.write',
    'execution.read', 'execution.detail.read',
    'master_data.department.read', 'master_data.employee.read',
    'master_data.resource.read', 'master_data.price.read',
    'menu.project.list.view', 'menu.plan.list.view', 'menu.execution.view'
  ],
  PLAN_ENGINEER: [
    'plan.task.read', 'plan.task.write', 'plan.task.batch_update',
    'plan.version.read',
    'master_data.department.read', 'master_data.employee.read',
    'menu.plan.list.view'
  ],
  EXECUTOR: [
    'execution.read', 'execution.detail.read', 'execution.progress.write', 'execution.actual_hours.read',
    'master_data.department.read', 'master_data.employee.read',
    'menu.execution.view'
  ],
  AUDITOR: [
    'project.read', 'plan.task.read', 'plan.version.read', 'execution.read', 'execution.detail.read',
    'master_data.employee.read', 'master_data.department.read', 'master_data.resource.read', 'master_data.price.read'
  ]
}

export const getCurrentRoles = () => {
  try {
    const user = JSON.parse(localStorage.getItem('hpm_user') || '{}')
    if (user.roles && Array.isArray(user.roles)) return user.roles
  } catch {}
  const legacy = window.localStorage.getItem('hpm_role')
  return legacy ? [legacy] : ['SUPER_ADMIN']
}

export const getCurrentRole = () => {
  return getCurrentRoles()[0] || 'SUPER_ADMIN'
}

export const hasPermission = (permissionCode) => {
  const roles = getCurrentRoles()
  for (const role of roles) {
    const perms = rolePermissions[role] || []
    if (perms.includes('*') || perms.includes(permissionCode)) return true
  }
  return false
}

export const hasAnyPermission = (codes = []) => codes.some(c => hasPermission(c))

export const getRolePermissions = () => {
  const roles = getCurrentRoles()
  const merged = new Set()
  for (const role of roles) {
    for (const p of (rolePermissions[role] || [])) {
      merged.add(p)
    }
  }
  return [...merged]
}
