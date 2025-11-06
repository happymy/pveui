<template>
  <div class="login-log-page">
    <a-card>
      <template #title>
        <a-typography-title :heading="5">登录日志</a-typography-title>
      </template>

      <div class="toolbar" style="margin-bottom: 12px;">
        <a-form :model="query" layout="inline">
          <a-form-item label="用户名">
            <a-input v-model="query.username" placeholder="搜索用户名" allow-clear style="width: 200px" />
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
          <a-table-column title="类型" data-index="action_type_display" :width="100">
            <template #cell="{ record }">
              <a-tag :color="record.action_type === 'login' ? 'green' : 'blue'">
                {{ record.action_type_display }}
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
          <a-table-column title="User-Agent" data-index="user_agent" :ellipsis="true" />
          <a-table-column title="时间" data-index="created_at" :width="180">
            <template #cell="{ record }">
              {{ formatDate(record.created_at) }}
            </template>
          </a-table-column>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import { getLoginLogList } from '@/api/audit'

const loading = ref(false)
const list = ref([])
const dateRange = ref([])

const query = reactive({
  username: '',
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
  Object.keys(params).forEach(key => {
    if (params[key] === '' || params[key] === undefined || params[key] === null) {
      delete params[key]
    }
  })
  getLoginLogList(params).then(res => {
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
    Message.error('获取登录日志失败：' + (err.message || '未知错误'))
    list.value = []
    pagination.total = 0
  }).finally(() => {
    loading.value = false
  })
}

function resetQuery() {
  query.username = ''
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

function getStatusColor(statusCode) {
  if (!statusCode) return 'gray'
  if (statusCode >= 200 && statusCode < 300) return 'green'
  if (statusCode >= 300 && statusCode < 400) return 'cyan'
  if (statusCode >= 400 && statusCode < 500) return 'orange'
  if (statusCode >= 500) return 'red'
  return 'gray'
}

fetchList()
</script>

<style scoped>
.login-log-page {
  padding: 16px;
}
.toolbar {
  margin-bottom: 16px;
}
</style>


