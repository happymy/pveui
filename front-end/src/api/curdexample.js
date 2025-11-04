import request from '@/utils/request'

/**
 * 示例管理 CRUD 接口
 */
export function getExampleList(params) {
  return request({ 
    url: '/api/curd/examples/', 
    method: 'get',
    params
  })
}

export function getExampleDetail(id) {
  return request({ 
    url: `/api/curd/examples/${id}/`, 
    method: 'get'
  })
}

export function createExample(data) {
  return request({ 
    url: '/api/curd/examples/', 
    method: 'post',
    data
  })
}

export function updateExample(id, data) {
  return request({ 
    url: `/api/curd/examples/${id}/`, 
    method: 'put',
    data
  })
}

export function patchExample(id, data) {
  return request({ 
    url: `/api/curd/examples/${id}/`, 
    method: 'patch',
    data
  })
}

export function deleteExample(id) {
  return request({ 
    url: `/api/curd/examples/${id}/`, 
    method: 'delete'
  })
}

