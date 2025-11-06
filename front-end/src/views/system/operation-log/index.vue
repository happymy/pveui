<template>
  <div class="operation-log-page">
    <a-card>
      <template #title>
        <a-typography-title :heading="5">操作日志</a-typography-title>
      </template>
      
      <div class="toolbar" style="margin-bottom: 12px;">
        <a-form :model="query" layout="inline">
          <a-form-item label="用户名">
            <a-input v-model="query.username" placeholder="搜索用户名" allow-clear style="width: 200px" />
          </a-form-item>
          <a-form-item label="操作类型">
            <a-select v-model="query.action_type" placeholder="全部" allow-clear style="width: 150px">
              <a-option value="create">创建</a-option>
              <a-option value="update">更新</a-option>
              <a-option value="delete">删除</a-option>
              <a-option value="view">查看</a-option>
              <a-option value="list">列表</a-option>
              <a-option value="other">其他</a-option>
            </a-select>
          </a-form-item>
          <a-form-item label="请求方法">
            <a-select v-model="query.request_method" placeholder="全部" allow-clear style="width: 120px">
              <a-option value="GET">GET</a-option>
              <a-option value="POST">POST</a-option>
              <a-option value="PUT">PUT</a-option>
              <a-option value="PATCH">PATCH</a-option>
              <a-option value="DELETE">DELETE</a-option>
            </a-select>
          </a-form-item>
          <a-form-item label="IP地址">
            <a-input v-model="query.ip_address" placeholder="搜索IP" allow-clear style="width: 150px" />
          </a-form-item>
          <a-form-item label="时间范围">
            <a-range-picker v-model="dateRange" style="width: 300px" />
          </a-form-item>
          <a-form-item>
            <a-space>
              <a-button type="primary" @click="fetchList">查询</a-button>
              <a-button @click="resetQuery">重置</a-button>
            </a-space>
          </a-form-item>
        </a-form>
      </div>

      <a-table 
        :data="list" 
        :loading="loading" 
        row-key="id" 
        :pagination="pagination" 
        @page-change="handlePageChange" 
        @page-size-change="handlePageSizeChange"
      >
        <template #columns>
          <a-table-column title="ID" data-index="id" :width="80" />
          <a-table-column title="用户名" data-index="user_display" :width="120">
            <template #cell="{ record }">
              {{ record.user_display || record.username || '匿名' }}
            </template>
          </a-table-column>
          <a-table-column title="操作类型" data-index="action_type_display" :width="100">
            <template #cell="{ record }">
              <a-tag :color="getActionTypeColor(record.action_type)">
                {{ record.action_type_display }}
              </a-tag>
            </template>
          </a-table-column>
          <a-table-column title="请求路径" data-index="request_path" :width="300" :ellipsis="true" />
          <a-table-column title="请求方法" data-index="request_method" :width="100">
            <template #cell="{ record }">
              <a-tag :color="getMethodColor(record.request_method)">
                {{ record.request_method }}
              </a-tag>
            </template>
          </a-table-column>
          <a-table-column title="IP地址" data-index="ip_address" :width="150" />
          <a-table-column title="状态码" data-index="status_code" :width="100">
            <template #cell="{ record }">
              <a-tag :color="getStatusColor(record.status_code)">
                {{ record.status_code || '-' }}
              </a-tag>
            </template>
          </a-table-column>
          <a-table-column title="操作时间" data-index="created_at" :width="180">
            <template #cell="{ record }">
              {{ formatDate(record.created_at) }}
            </template>
          </a-table-column>
          <a-table-column title="操作" :width="100" fixed="right">
            <template #cell="{ record }">
              <a-button type="text" size="small" @click="showDetail(record)">详情</a-button>
            </template>
          </a-table-column>
        </template>
      </a-table>
    </a-card>

    <!-- 详情对话框 -->
    <a-modal 
      v-model:visible="detailVisible" 
      title="操作日志详情" 
      :width="800"
      :footer="false"
    >
      <a-descriptions v-if="currentDetail" :column="1" bordered>
        <a-descriptions-item label="ID">{{ currentDetail.id }}</a-descriptions-item>
        <a-descriptions-item label="操作人">
          {{ currentDetail.user_display || currentDetail.username || '匿名' }}
        </a-descriptions-item>
        <a-descriptions-item label="操作类型">
          <a-tag :color="getActionTypeColor(currentDetail.action_type)">
            {{ currentDetail.action_type_display }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="操作对象">
          {{ currentDetail.object_repr || '-' }}
          <span v-if="currentDetail.content_type_display" style="color: #86909c; margin-left: 8px;">
            ({{ currentDetail.content_type_display }})
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="请求路径">{{ currentDetail.request_path }}</a-descriptions-item>
        <a-descriptions-item label="请求方法">
          <a-tag :color="getMethodColor(currentDetail.request_method)">
            {{ currentDetail.request_method }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="IP地址">{{ currentDetail.ip_address || '-' }}</a-descriptions-item>
        <a-descriptions-item label="浏览器信息">{{ currentDetail.user_agent || '-' }}</a-descriptions-item>
        <a-descriptions-item label="状态码">
          <a-tag :color="getStatusColor(currentDetail.status_code)">
            {{ currentDetail.status_code || '-' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="错误信息" v-if="currentDetail.error_message">
          <a-typography-text type="danger">{{ currentDetail.error_message }}</a-typography-text>
        </a-descriptions-item>
        <a-descriptions-item label="请求参数">
          <pre style="max-height: 200px; overflow: auto; background: #f5f5f5; padding: 8px; margin: 0; border-radius: 4px;">{{ formatJson(currentDetail.request_params) }}</pre>
        </a-descriptions-item>
        <a-descriptions-item label="操作时间">{{ formatDate(currentDetail.created_at) }}</a-descriptions-item>
        <a-descriptions-item label="备注" v-if="currentDetail.remark">
          {{ currentDetail.remark }}
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import { getOperationLogList, getOperationLogDetail } from '@/api/audit'

const loading = ref(false)
const list = ref([])
const detailVisible = ref(false)
const currentDetail = ref(null)
const dateRange = ref([])

const query = reactive({
  username: '',
  action_type: undefined,
  request_method: undefined,
  ip_address: '',
  created_at_start: undefined,
  created_at_end: undefined,
})

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showTotal: true,
})

// 监听日期范围变化
watch(dateRange, (val) => {
  if (val && val.length === 2) {
    query.created_at_start = val[0]
    query.created_at_end = val[1]
  } else {
    query.created_at_start = undefined
    query.created_at_end = undefined
  }
})

function fetchList() {
  loading.value = true
  const params = {
    ...query,
    page: pagination.current,
    page_size: pagination.pageSize,
  }
  
  // 清理空值
  Object.keys(params).forEach(key => {
    if (params[key] === '' || params[key] === undefined || params[key] === null) {
      delete params[key]
    }
  })
  
  getOperationLogList(params).then(res => {
    if (res.data && res.data.results) {
      list.value = res.data.results
      pagination.total = res.data.count || 0
    } else if (res.results) {
      list.value = res.results
      pagination.total = res.count || 0
    } else {
      list.value = []
      pagination.total = 0
    }
  }).catch(err => {
    Message.error('获取操作日志失败：' + (err.message || '未知错误'))
    list.value = []
    pagination.total = 0
  }).finally(() => {
    loading.value = false
  })
}

function resetQuery() {
  query.username = ''
  query.action_type = undefined
  query.request_method = undefined
  query.ip_address = ''
  query.created_at_start = undefined
  query.created_at_end = undefined
  dateRange.value = []
  pagination.current = 1
  fetchList()
}

function handlePageChange(page) {
  pagination.current = page
  fetchList()
}

function handlePageSizeChange(pageSize) {
  pagination.pageSize = pageSize
  pagination.current = 1
  fetchList()
}

function showDetail(record) {
  currentDetail.value = record
  detailVisible.value = true
  
  // 如果需要获取完整详情，可以调用详情接口
  // getOperationLogDetail(record.id).then(res => {
  //   currentDetail.value = res.data || res
  // })
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function formatJson(obj) {
  if (!obj) return '无'
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

function getActionTypeColor(actionType) {
  const colors = {
    create: 'green',
    update: 'blue',
    delete: 'red',
    view: 'cyan',
    list: 'purple',
    other: 'gray',
  }
  return colors[actionType] || 'gray'
}

function getMethodColor(method) {
  const colors = {
    GET: 'blue',
    POST: 'green',
    PUT: 'orange',
    PATCH: 'cyan',
    DELETE: 'red',
  }
  return colors[method] || 'gray'
}

function getStatusColor(statusCode) {
  if (!statusCode) return 'gray'
  if (statusCode >= 200 && statusCode < 300) return 'green'
  if (statusCode >= 300 && statusCode < 400) return 'cyan'
  if (statusCode >= 400 && statusCode < 500) return 'orange'
  if (statusCode >= 500) return 'red'
  return 'gray'
}

// 初始化加载
fetchList()
</script>

<style scoped>
.operation-log-page {
  padding: 16px;
}

.toolbar {
  margin-bottom: 16px;
}
</style>

