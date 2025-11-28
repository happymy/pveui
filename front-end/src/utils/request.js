import axios from 'axios'
import { Message } from '@arco-design/web-vue'

// JWT 认证
// 如果设置了 VITE_HOST，直接使用（开发环境或直接连接后端）
// 否则使用空字符串（生产环境通过 nginx 代理，API 路径已包含 /api）
const baseURL = import.meta.env.VITE_HOST || '/api'
const service = axios.create({
  baseURL: baseURL,
  timeout: 10000,
})

// 获取 JWT token（从 localStorage 中读取）
function getAccessToken() {
  return localStorage.getItem('access_token') || null
}

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 添加 JWT token 到请求头
    const token = getAccessToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    } else {
      console.warn('[request] No token found for request:', config.url)
    }

    // 调试日志
    console.log('[request]', config.method?.toUpperCase(), config.baseURL + config.url, {
      hasToken: !!token,
      tokenPreview: token ? token.substring(0, 20) + '...' : null,
      authHeader: config.headers['Authorization'] ? 'Bearer ***' : 'missing'
    })

    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data

    // 如果后端返回的状态码不是 200-299，视为错误
    if (response.status >= 400) {
      Message.error(res.detail || res.message || '请求失败')
      return Promise.reject(new Error(res.detail || res.message || 'Error'))
    }

    return res
  },
  error => {
    // 处理401未授权错误（token过期或无效）
    if (error.response?.status === 401) {
      // 清除token并跳转到登录页
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      // 避免在登录页重复跳转
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      Message.error('登录已过期，请重新登录')
      return Promise.reject(error)
    }

    // 处理其他错误响应
    const errorMessage = error.response?.data?.detail ||
                         error.response?.data?.message ||
                         error.message ||
                         '请求失败'

    Message.error(errorMessage)
    return Promise.reject(error)
  }
)

export default service
