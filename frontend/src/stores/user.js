import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref({
    name: '管理员',
    role: 'PM',
    department: '',
  })
  const permissions = ref([])

  const setUserInfo = (info) => { userInfo.value = { ...userInfo.value, ...info } }
  const setPermissions = (perms) => { permissions.value = perms }

  return { userInfo, permissions, setUserInfo, setPermissions }
})
