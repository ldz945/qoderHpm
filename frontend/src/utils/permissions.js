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
    'project.read', 'project.create', 'project.update', 'project.status.update',
    'plan.task.read', 'plan.task.write', 'plan.task.batch_update',
    'plan.version.read', 'plan.version.write',
    'execution.read', 'execution.detail.read', 'execution.actual_hours.read',
    'menu.project.list.view', 'menu.plan.list.view', 'menu.execution.view'
  ],
  PROJECT_MANAGER: [
    'project.read', 'project.create', 'project.update', 'project.status.update',
    'plan.task.read', 'plan.task.write', 'plan.task.batch_update',
    'plan.version.read', 'plan.version.write',
    'execution.read', 'execution.detail.read',
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

export const getCurrentRole = () => {
  return window.localStorage.getItem('hpm_role') || 'SUPER_ADMIN'
}

export const hasPermission = (permissionCode) => {
  const role = getCurrentRole()
  const perms = rolePermissions[role] || []
  return perms.includes('*') || perms.includes(permissionCode)
}

export const getRolePermissions = () => {
  const role = getCurrentRole()
  return rolePermissions[role] || []
}

