import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getProjects } from '@/api/project'

export const useProjectStore = defineStore('project', () => {
  const currentProject = ref(null)
  const projectList = ref([])
  const loading = ref(false)

  const setCurrentProject = (project) => {
    currentProject.value = project
  }

  const fetchProjects = async (params = {}) => {
    loading.value = true
    try {
      const res = await getProjects(params)
      projectList.value = res.results || res
      return res
    } finally {
      loading.value = false
    }
  }

  return { currentProject, projectList, loading, setCurrentProject, fetchProjects }
})
