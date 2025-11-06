import request from '@/utils/request'

/**
 * 操作日志 API
 */
export function getOperationLogList(params) {
  return request({ 
    url: '/api/audit/logs/', 
    method: 'get',
    params
  })
}

export function getOperationLogDetail(id) {
  return request({ 
    url: `/api/audit/logs/${id}/`, 
    method: 'get'
  })
}

/**
 * 登录日志 API
 */
export function getLoginLogList(params) {
  return request({
    url: '/api/audit/login-logs/',
    method: 'get',
    params
  })
}

