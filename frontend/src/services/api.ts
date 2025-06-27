import axios from 'axios'
import { message } from 'antd'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem('token')
          delete api.defaults.headers.common['Authorization']
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          break
        case 403:
          message.error('权限不足')
          break
        case 404:
          message.error('请求的资源不存在')
          break
        case 500:
          message.error('服务器内部错误')
          break
        default:
          if (data?.message) {
            message.error(data.message)
          } else {
            message.error('请求失败')
          }
      }
    } else if (error.request) {
      message.error('网络连接失败')
    } else {
      message.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default api
