<template>
  <div class="dashboard-page">
    <a-card>
      <template #title>
        <a-typography-title :heading="4">仪表盘</a-typography-title>
      </template>

      <div class="toolbar" style="margin-bottom: 16px;">
        <a-space>
          <a-button type="primary" @click="fetchData" :loading="loading">刷新</a-button>
          <a-switch v-model="autoRefresh" checked-text="自动刷新" unchecked-text="手动" />
          <a-input-number v-model="intervalSec" :min="5" :max="300" />
          <a-typography-text type="secondary">秒</a-typography-text>
        </a-space>
      </div>

      <!-- 统计卡片 -->
      <a-grid :cols="4" :col-gap="16" :row-gap="16" style="margin-bottom: 16px;">
        <a-grid-item>
          <a-card>
            <a-statistic
              title="用户数"
              :value="data.stats?.users || 0"
              :value-style="{ color: '#165DFF' }"
            >
              <template #prefix>
                <icon-user />
              </template>
            </a-statistic>
          </a-card>
        </a-grid-item>
        <a-grid-item>
          <a-card>
            <a-statistic
              title="角色数"
              :value="data.stats?.roles || 0"
              :value-style="{ color: '#00B42A' }"
            >
              <template #prefix>
                <icon-user-group />
              </template>
            </a-statistic>
          </a-card>
        </a-grid-item>
        <a-grid-item>
          <a-card>
            <a-statistic
              title="菜单数"
              :value="data.stats?.menus || 0"
              :value-style="{ color: '#FF7D00' }"
            >
              <template #prefix>
                <icon-menu />
              </template>
            </a-statistic>
          </a-card>
        </a-grid-item>
        <a-grid-item>
          <a-card>
            <a-statistic
              title="操作日志"
              :value="data.stats?.operation_logs || 0"
              :value-style="{ color: '#722ED1' }"
            >
              <template #prefix>
                <icon-file />
              </template>
            </a-statistic>
          </a-card>
        </a-grid-item>
      </a-grid>

      <a-grid :cols="2" :col-gap="16" :row-gap="16">
        <!-- 每日操作统计图表 -->
        <a-grid-item>
          <a-card title="每日操作统计（最近7天）">
            <div ref="chartRef" style="width: 100%; height: 300px;"></div>
          </a-card>
        </a-grid-item>

        <!-- 系统状态 -->
        <a-grid-item>
          <a-card title="系统状态">
            <a-descriptions v-if="data.system_status" :column="1" bordered>
              <a-descriptions-item label="CPU使用率">
                <a-progress :percent="data.system_status.cpu_percent" :status="getStatusColor(data.system_status.cpu_percent)" />
                {{ data.system_status.cpu_percent }}%
              </a-descriptions-item>
              <a-descriptions-item label="内存使用率">
                <a-progress :percent="data.system_status.memory_percent" :status="getStatusColor(data.system_status.memory_percent)" />
                {{ data.system_status.memory_percent }}% ({{ data.system_status.memory_used_gb }}GB / {{ data.system_status.memory_total_gb }}GB)
              </a-descriptions-item>
              <a-descriptions-item label="错误操作（7天）">
                <a-tag :color="data.error_count > 0 ? 'red' : 'green'">
                  {{ data.error_count || 0 }}
                </a-tag>
              </a-descriptions-item>
            </a-descriptions>
            <a-empty v-else description="暂无系统状态数据" />
          </a-card>
        </a-grid-item>

        <!-- 最近操作日志 -->
        <a-grid-item>
          <a-card title="最近操作日志">
            <a-table :data="data.recent_logs || []" :pagination="false" :loading="loading" size="small">
              <template #columns>
                <a-table-column title="用户" data-index="username" :width="100" />
                <a-table-column title="操作" data-index="action_type_display" :width="80">
                  <template #cell="{ record }">
                    <a-tag :color="getActionTypeColor(record.action_type)" size="small">
                      {{ record.action_type_display }}
                    </a-tag>
                  </template>
                </a-table-column>
                <a-table-column title="路径" data-index="request_path" :ellipsis="true" />
                <a-table-column title="状态" data-index="status_code" :width="80">
                  <template #cell="{ record }">
                    <a-tag :color="getStatusColor(record.status_code)" size="small">
                      {{ record.status_code }}
                    </a-tag>
                  </template>
                </a-table-column>
                <a-table-column title="时间" data-index="created_at" :width="150">
                  <template #cell="{ record }">
                    {{ formatDate(record.created_at) }}
                  </template>
                </a-table-column>
              </template>
            </a-table>
          </a-card>
        </a-grid-item>

        <!-- 最近活跃用户 -->
        <a-grid-item>
          <a-card title="最近活跃用户（7天）">
            <a-list :data="data.recent_users || []" :loading="loading">
              <template #item="{ item }">
                <a-list-item>
                  <a-list-item-meta>
                    <template #avatar>
                      <a-avatar :style="{ backgroundColor: '#165DFF' }">
                        {{ item.username?.[0]?.toUpperCase() || 'U' }}
                      </a-avatar>
                    </template>
                    <template #title>
                      {{ item.username }}
                      <a-tag size="small" style="margin-left: 8px;">
                        {{ item.log_count }} 次操作
                      </a-tag>
                    </template>
                    <template #description>
                      {{ item.email || '-' }}
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
          </a-card>
        </a-grid-item>
      </a-grid>

      <!-- 最活跃的 API 路径 -->
      <a-card style="margin-top: 16px" title="最活跃的 API 路径（7天）">
        <a-table :data="data.top_paths || []" :pagination="false" :loading="loading" size="small">
          <template #columns>
            <a-table-column title="路径" data-index="path" :ellipsis="true" />
            <a-table-column title="访问次数" data-index="count" :width="120">
              <template #cell="{ record }">
                <a-tag color="blue">{{ record.count }}</a-tag>
              </template>
            </a-table-column>
          </template>
        </a-table>
      </a-card>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import { IconUser, IconUserGroup, IconMenu, IconFile } from '@arco-design/web-vue/es/icon'
import { getDashboardData } from '@/api/system'
import * as echarts from 'echarts'

const loading = ref(false)
const autoRefresh = ref(false)
const intervalSec = ref(30)
const chartRef = ref(null)
let chartInstance = null
let refreshTimer = null

const data = reactive({
  stats: {},
  recent_logs: [],
  action_stats: {},
  daily_stats: [],
  recent_users: [],
  system_status: {},
  error_count: 0,
  top_paths: [],
})

function fetchData() {
  loading.value = true
  getDashboardData().then(res => {
    const result = res.data || res
    Object.assign(data, result)
    
    // 更新图表
    nextTick(() => {
      updateChart()
    })
  }).catch(err => {
    Message.error('获取仪表盘数据失败：' + (err.message || '未知错误'))
  }).finally(() => {
    loading.value = false
  })
}

function updateChart() {
  if (!chartRef.value || !data.daily_stats || data.daily_stats.length === 0) {
    return
  }

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.daily_stats.map(item => item.date),
      axisTick: {
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '操作次数',
        type: 'bar',
        barWidth: '60%',
        data: data.daily_stats.map(item => item.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).replace(/\//g, '-')
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

function getStatusColor(value) {
  if (typeof value === 'number' && value <= 100) {
    // 进度条颜色（0-100）
    if (value < 50) return 'success'
    if (value < 80) return 'warning'
    return 'danger'
  }
  // HTTP 状态码颜色
  if (!value) return 'gray'
  if (value >= 200 && value < 300) return 'green'
  if (value >= 300 && value < 400) return 'cyan'
  if (value >= 400 && value < 500) return 'orange'
  if (value >= 500) return 'red'
  return 'gray'
}

// 监听自动刷新
watch(autoRefresh, (val) => {
  if (val) {
    refreshTimer = setInterval(() => {
      fetchData()
    }, intervalSec.value * 1000)
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }
})

watch(intervalSec, (val) => {
  if (autoRefresh.value && refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = setInterval(() => {
      fetchData()
    }, val * 1000)
  }
})

onMounted(() => {
  fetchData()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<script>
export default {
  name: 'Dashboard'
}
</script>

<style scoped>
.dashboard-page {
  padding: 16px;
}
</style>

