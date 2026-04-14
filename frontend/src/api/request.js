import axios from 'axios'
import { message } from 'ant-design-vue'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器
request.interceptors.request.use(config => config, error => Promise.reject(error))

// 响应拦截器
request.interceptors.response.use(
  response => {
    const payload = response.data
    // 兼容两套历史读取方式：res.results/res.count 与 res.data.list/res.data.total
    if (payload && typeof payload === 'object' && !Array.isArray(payload)) {
      if (typeof payload.count === 'number' && Array.isArray(payload.results)) {
        return {
          ...payload,
          data: {
            list: payload.results,
            total: payload.count
          }
        }
      }
      return {
        ...payload,
        data: payload
      }
    }
    return { data: payload }
  },
  error => {
    const msg = error.response?.data?.detail || error.message || '请求失败'
    message.error(msg)
    return Promise.reject(error)
  }
)

export default request
