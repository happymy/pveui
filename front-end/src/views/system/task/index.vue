<template>
  <div class="task-page">
    <a-card>
      <template #title>
        <a-typography-title :heading="5">任务管理</a-typography-title>
      </template>
      <div class="toolbar" style="margin-bottom:12px;">
        <a-space>
          <a-button type="primary" @click="openEdit()">新增</a-button>
          <a-input v-model="query.job_name" placeholder="按名称搜索" allow-clear style="width:200px" />
          <a-button @click="fetchList">查询</a-button>
        </a-space>
      </div>
      <a-table :data="list" :loading="loading" row-key="jobId" :pagination="pagination" @page-change="handlePageChange" @page-size-change="handlePageSizeChange">
        <template #columns>
          <a-table-column title="任务名称" data-index="jobName" />
          <a-table-column title="调用目标" data-index="invokeTarget" />
          <a-table-column title="Cron表达式" data-index="cronExpression" />
          <a-table-column title="下次执行" data-index="nextValidTime">
            <template #cell="{ record }">
              {{ formatDate(record.nextValidTime) }}
            </template>
          </a-table-column>
          <a-table-column title="状态" data-index="status">
            <template #cell="{ record }">
              <a-tag :color="record.status === 1 ? 'green' : 'red'">
                {{ record.status === 1 ? '启用' : '停用' }}
              </a-tag>
            </template>
          </a-table-column>
          <a-table-column title="操作" :width="220">
            <template #cell="{ record }">
              <a-space :size="8">
                <a-button type="text" size="small" @click="openEdit(record)">编辑</a-button>
                <a-button type="text" size="small" @click="handleRun(record)">执行一次</a-button>
                <a-button type="text" size="small" status="danger" @click="handleDelete(record)">删除</a-button>
              </a-space>
            </template>
          </a-table-column>
        </template>
      </a-table>
    </a-card>

    <a-modal v-model:visible="visible" :title="form.jobId ? '编辑任务' : '新增任务'" @ok="submit" :mask-closable="false">
      <a-form :model="form" layout="vertical">
        <a-form-item field="jobName" label="任务名称" required>
          <a-input v-model="form.jobName" />
        </a-form-item>
        <a-form-item field="invokeTarget" label="调用目标" required>
          <a-input v-model="form.invokeTarget" placeholder="如: NoParams, Params" />
        </a-form-item>
        <a-form-item field="cronExpression" label="Cron表达式" required>
          <a-input v-model="form.cronExpression" placeholder="* * * * * (分 时 日 月 周)" />
          <template #extra>标准5位格式：分 时 日 月 周，或6位：秒 分 时 日 月 周</template>
        </a-form-item>
        <a-form-item field="jobParams" label="参数(JSON数组)">
          <a-input v-model="paramsStr" placeholder='如 ["baize", "18"]' />
          <template #extra>参数数组，将作为位置参数传递给任务函数</template>
        </a-form-item>
        <a-form-item field="status" label="状态">
          <a-radio-group v-model="form.status">
            <a-radio :value="1">启用</a-radio>
            <a-radio :value="0">停用</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import {ref, reactive} from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { listTasks, createTask, updateTask, deleteTask, runTaskNow } from '@/api/task'

const loading = ref(false)
const list = ref([])
const visible = ref(false)
const form = reactive({ jobId: undefined, jobName: '', invokeTarget: '', cronExpression: '* * * * *', jobParams: [], status: 1 })
const paramsStr = ref('[]')
const query = reactive({ job_name: '' })
const pagination = reactive({ current: 1, pageSize: 10, total: 0, showTotal: true })

function fetchList() {
  loading.value = true
  const params = {
    ...query,
    page: pagination.current,
    page_size: pagination.pageSize
  }
  listTasks(params).then(res => {
    if (res.data && res.data.rows) {
      list.value = res.data.rows
      pagination.total = res.data.total || 0
    } else if (res.results) {
      list.value = res.results
      pagination.total = res.count || 0
    } else {
      list.value = res || []
    }
  }).catch(err => {
    console.error('获取任务列表失败:', err)
    Message.error('获取任务列表失败')
  }).finally(() => loading.value = false)
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', { 
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit', 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return dateStr
  }
}

function openEdit(record) {
  Object.assign(form, { jobId: undefined, jobName: '', invokeTarget: '', cronExpression: '* * * * *', jobParams: [], status: 1 })
  paramsStr.value = '[]'
  if (record) {
    Object.assign(form, record)
    paramsStr.value = JSON.stringify(record.jobParams || [])
  }
  visible.value = true
}

function submit() {
  try {
    form.jobParams = JSON.parse(paramsStr.value || '[]')
  } catch (e) {
    Message.error('参数需为合法 JSON 数组')
    return
  }
  const api = form.jobId ? updateTask.bind(null, form.jobId) : createTask
  api(form).then(() => {
    Message.success('保存成功')
    visible.value = false
    fetchList()
  }).catch(err => {
    Message.error(err?.response?.data?.detail || '保存失败')
  })
}

function handleDelete(record) {
  Modal.confirm({ 
    title: '确认删除', 
    content: `删除任务「${record.jobName}」?`, 
    onOk: () => deleteTask(record.jobId).then(() => { 
      Message.success('已删除')
      fetchList() 
    })
  })
}

function handleRun(record) {
  runTaskNow(record.jobId).then(() => Message.success('已触发执行')).catch(err => {
    Message.error(err?.response?.data?.detail || '执行失败')
  })
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


fetchList()
</script>

<style scoped>
.task-page { padding: 12px; }
</style>
