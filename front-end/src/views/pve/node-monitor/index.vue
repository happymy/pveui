<template>
  <div class="pve-node-monitor">
    <a-card class="filter-card" :bordered="false">
      <div class="filter-grid">
        <div class="filter-item">
          <div class="label">PVE服务器</div>
          <a-select
            v-model="selectedServer"
            placeholder="请选择服务器"
            allow-clear
            :loading="serverLoading"
          >
            <a-option v-for="item in serverOptions" :key="item.value" :value="item.value">
              {{ item.label }}
            </a-option>
          </a-select>
        </div>
        <div class="filter-item">
          <div class="label">所属节点</div>
          <a-select
            v-model="selectedNode"
            placeholder="请选择节点"
            allow-clear
            :disabled="!selectedServer"
            :loading="nodeLoading"
          >
            <a-option v-for="item in nodeOptions" :key="item.value" :value="item.value">
              {{ item.label }}
            </a-option>
          </a-select>
        </div>
        <div class="filter-item">
          <div class="label">时间范围</div>
          <a-radio-group
            v-model="timeframe"
            type="button"
            size="small"
            :options="timeframeOptions"
            @change="handleTimeframeChange"
          />
        </div>
        <div class="filter-item actions">
          <a-space>
            <div class="meta" v-if="summary.node">
              <span>状态：</span>
              <a-tag :color="getStatusTag(summary.status).color" size="small">
                {{ getStatusTag(summary.status).text }}
              </a-tag>
            </div>
            <div class="meta" v-if="summary.last_update">
              <span>最近更新：</span>
              <span>{{ formatTime(summary.last_update) }}</span>
            </div>
            <a-button type="primary" size="small" @click="loadMonitor" :loading="monitorLoading">
              <template #icon>
                <icon-refresh />
              </template>
              刷新
            </a-button>
          </a-space>
        </div>
      </div>
    </a-card>

    <div class="summary-row">
      <div class="stat-card">
        <div class="stat-header">
          <span>CPU使用率</span>
          <a-tag size="small">{{ summary.cpu.cores || '-' }} 核</a-tag>
        </div>
        <div class="stat-value">{{ summary.cpu.percent.toFixed(1) }}%</div>
        <a-progress
          :percent="summary.cpu.percent"
          :status="getProgressStatus(summary.cpu.percent, [75, 90])"
          stroke-width="6"
        />
        <div class="stat-desc">负载：{{ formatLoad(summary.cpu.loadavg) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-header">
          <span>内存使用率</span>
          <a-tag size="small">{{ formatBytes(summary.memory.used) }}/{{ formatBytes(summary.memory.total) }}</a-tag>
        </div>
        <div class="stat-value">{{ summary.memory.percent.toFixed(1) }}%</div>
        <a-progress
          :percent="summary.memory.percent"
          :status="getProgressStatus(summary.memory.percent, [80, 90])"
          stroke-width="6"
        />
        <div class="stat-desc">NUMA：{{ summary.memory.total ? '已启用/默认' : '-' }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-header">
          <span>存储使用率</span>
          <a-tag size="small">{{ formatBytes(summary.storage.used) }}/{{ formatBytes(summary.storage.total) }}</a-tag>
        </div>
        <div class="stat-value">{{ summary.storage.percent.toFixed(1) }}%</div>
        <a-progress
          :percent="summary.storage.percent"
          :status="getProgressStatus(summary.storage.percent, [80, 90])"
          stroke-width="6"
        />
        <div class="stat-desc">根存储使用</div>
      </div>
      <div class="stat-card">
        <div class="stat-header">
          <span>网络吞吐</span>
          <a-tag size="small">实时</a-tag>
        </div>
        <div class="stat-value">{{ formatThroughput(summary.network.in) }}/s</div>
        <div class="stat-sub-value">出：{{ formatThroughput(summary.network.out) }}/s</div>
        <div class="stat-desc">运行时长：{{ formatDuration(summary.uptime) }}</div>
      </div>
    </div>

    <a-card title="资源走势" class="chart-card" :bordered="false">
      <a-spin :loading="monitorLoading">
        <template #tip>正在加载节点监控数据...</template>
        <a-grid v-if="metrics.length" :cols="3" :col-gap="16" :row-gap="16" class="chart-grid">
          <a-grid-item>
            <a-card title="CPU使用率" :bordered="true" class="chart-item-card">
              <div ref="cpuChartRef" class="chart-container"></div>
            </a-card>
          </a-grid-item>
          <a-grid-item>
            <a-card title="内存使用率" :bordered="true" class="chart-item-card">
              <div ref="memoryChartRef" class="chart-container"></div>
            </a-card>
          </a-grid-item>
          <a-grid-item>
            <a-card title="存储使用率" :bordered="true" class="chart-item-card">
              <div ref="storageChartRef" class="chart-container"></div>
            </a-card>
          </a-grid-item>
          <a-grid-item>
            <a-card title="网络吞吐" :bordered="true" class="chart-item-card">
              <div ref="networkChartRef" class="chart-container"></div>
            </a-card>
          </a-grid-item>
        </a-grid>
        <a-empty v-else description="暂无监控数据" />
      </a-spin>
    </a-card>

    <a-card title="健康告警" class="alert-card" :bordered="false">
      <template #extra>
        <span v-if="alerts.length">共 {{ alerts.length }} 条</span>
      </template>
      <a-list v-if="alerts.length" :data="alerts" :bordered="false" :split="false">
        <template #item="{ item }">
          <a-alert
            :type="item.level === 'danger' ? 'error' : 'warning'"
            :show-icon="true"
            :closable="false"
            class="alert-item"
          >
            {{ item.message }}
          </a-alert>
        </template>
      </a-list>
      <a-empty v-else description="一切正常，暂无告警" />
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { Message } from '@arco-design/web-vue'
import { IconRefresh } from '@arco-design/web-vue/es/icon'
import * as echarts from 'echarts'
import {
  getPVEServers,
  getPVEServerNodes,
  getNodeMonitor
} from '@/api/pve'

const servers = ref([])
const nodes = ref([])
const selectedServer = ref(null)
const selectedNode = ref(null)
const timeframe = ref('hour')
const metrics = ref([])
const alerts = ref([])
const serverLoading = ref(false)
const nodeLoading = ref(false)
const monitorLoading = ref(false)
let monitorRequestId = 0

const summary = reactive({
  cpu: { percent: 0, cores: 0, loadavg: null },
  memory: { total: 0, used: 0, percent: 0 },
  storage: { total: 0, used: 0, percent: 0 },
  network: { in: 0, out: 0 },
  uptime: 0,
  node: '',
  status: '',
  last_update: null
})

const timeframeOptions = [
  { label: '1小时', value: 'hour' },
  { label: '1天', value: 'day' },
  { label: '1周', value: 'week' },
  { label: '1月', value: 'month' },
  { label: '1年', value: 'year' }
]

const serverOptions = computed(() =>
  servers.value.map(item => ({
    label: `${item.name || item.host} (${item.host})`,
    value: item.id
  }))
)

const nodeOptions = computed(() =>
  nodes.value.map(item => ({
    label: item.node || item.name,
    value: item.node || item.name
  }))
)

const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
const storageChartRef = ref(null)
const networkChartRef = ref(null)
let cpuChartInstance = null
let memoryChartInstance = null
let storageChartInstance = null
let networkChartInstance = null

const formattedMetrics = computed(() => {
  if (!metrics.value?.length) return []
  // 从 summary 获取内存和存储的总量，用于计算百分比
  const memoryTotal = summary.memory.total || 0
  const storageTotal = summary.storage.total || 0
  
  return metrics.value.map(item => {
    const time = item.time
    const cpuPercent = typeof item.cpu === 'number' ? +(item.cpu * 100).toFixed(2) : 0
    
    // 处理内存：优先使用 item.mem 和 item.maxmem，如果没有则使用 summary 的数据
    let memoryPercent = 0
    if (item.maxmem && item.mem !== undefined) {
      memoryPercent = +(item.mem / item.maxmem * 100).toFixed(2)
    } else if (memoryTotal > 0 && item.mem !== undefined) {
      memoryPercent = +(item.mem / memoryTotal * 100).toFixed(2)
    } else if (summary.memory.percent > 0) {
      // 如果 metrics 中没有内存数据，使用 summary 的百分比
      memoryPercent = summary.memory.percent
    }
    
    // 处理存储：优先使用 item.disk 和 item.maxdisk，如果没有则使用 summary 的数据
    let storagePercent = 0
    if (item.maxdisk && item.disk !== undefined) {
      storagePercent = +(item.disk / item.maxdisk * 100).toFixed(2)
    } else if (storageTotal > 0 && item.disk !== undefined) {
      storagePercent = +(item.disk / storageTotal * 100).toFixed(2)
    } else if (summary.storage.percent > 0) {
      // 如果 metrics 中没有存储数据，使用 summary 的百分比
      storagePercent = summary.storage.percent
    }
    
    return {
      time,
      cpu: cpuPercent,
      memory: memoryPercent,
      storage: storagePercent,
      netIn: item.netin || 0,
      netOut: item.netout || 0
    }
  })
})

function handleServerChange() {
  if (selectedServer.value) {
    loadNodes()
  } else {
    selectedNode.value = null
    metrics.value = []
    alerts.value = []
    resetSummary()
  }
}

function handleNodeChange() {
  if (selectedNode.value) {
    loadMonitor()
  } else {
    metrics.value = []
    alerts.value = []
    resetSummary()
  }
}

function handleTimeframeChange() {
  if (selectedServer.value && selectedNode.value) {
    loadMonitor()
  }
}

function resetSummary(data = {}) {
  summary.cpu.percent = data.cpu?.percent ?? 0
  summary.cpu.cores = data.cpu?.cores ?? 0
  summary.cpu.loadavg = data.cpu?.loadavg ?? null
  summary.memory.total = data.memory?.total ?? 0
  summary.memory.used = data.memory?.used ?? 0
  summary.memory.percent = data.memory?.percent ?? 0
  summary.storage.total = data.storage?.total ?? 0
  summary.storage.used = data.storage?.used ?? 0
  summary.storage.percent = data.storage?.percent ?? 0
  summary.network.in = data.network?.in ?? 0
  summary.network.out = data.network?.out ?? 0
  summary.uptime = data.uptime ?? 0
  summary.node = data.node ?? ''
  summary.status = data.status ?? ''
  summary.last_update = data.last_update ?? null
}

async function loadServers() {
  serverLoading.value = true
  try {
    const res = await getPVEServers({ page_size: 200 })
    const data = Array.isArray(res) ? res : res?.results || []
    servers.value = data.filter(item => item.is_active !== false)
    if (!selectedServer.value && servers.value.length) {
      selectedServer.value = servers.value[0].id
    }
  } catch (error) {
    Message.error('获取服务器列表失败：' + (error.message || '未知错误'))
  } finally {
    serverLoading.value = false
  }
}

async function loadNodes() {
  if (!selectedServer.value) return
  nodeLoading.value = true
  try {
    const res = await getPVEServerNodes(selectedServer.value)
    nodes.value = Array.isArray(res) ? res : res?.data || []
    if (nodes.value.length && !selectedNode.value) {
      selectedNode.value = nodes.value[0].node || nodes.value[0].name
    } else if (selectedNode.value) {
      const exists = nodes.value.some(item => (item.node || item.name) === selectedNode.value)
      if (!exists) {
        selectedNode.value = nodes.value[0]?.node || nodes.value[0]?.name || null
      }
    }
    if (!nodes.value.length) {
      selectedNode.value = null
    }
  } catch (error) {
    Message.error('获取节点列表失败：' + (error.message || '未知错误'))
    nodes.value = []
    selectedNode.value = null
  } finally {
    nodeLoading.value = false
  }
}

async function loadMonitor() {
  if (!selectedServer.value || !selectedNode.value) {
    return
  }
  const requestId = ++monitorRequestId
  monitorLoading.value = true
  try {
    const res = await getNodeMonitor(selectedServer.value, selectedNode.value, { timeframe: timeframe.value })
    if (requestId !== monitorRequestId) {
      return
    }
    const result = res?.data || res || {}
    resetSummary(result.summary || {})
    metrics.value = Array.isArray(result.metrics) ? result.metrics : []
    alerts.value = Array.isArray(result.alerts) ? result.alerts : []
    
    // 如果 summary 中有内存数据但 metrics 中没有，尝试从 status 获取
    if (result.status?.memory && (!summary.memory.total || summary.memory.total === 0)) {
      const statusMem = result.status.memory
      if (statusMem.total && statusMem.used !== undefined) {
        summary.memory.total = statusMem.total
        summary.memory.used = statusMem.used
        summary.memory.percent = statusMem.total > 0 ? +((statusMem.used / statusMem.total) * 100).toFixed(2) : 0
      }
    }
    
    await nextTick()
    updateCharts()
  } catch (error) {
    if (requestId !== monitorRequestId) {
      return
    }
    Message.error('获取节点监控数据失败：' + (error.message || '未知错误'))
    metrics.value = []
    alerts.value = []
    resetSummary()
  } finally {
    if (requestId === monitorRequestId) {
      monitorLoading.value = false
    }
  }
}

function updateCharts() {
  const data = formattedMetrics.value
  cpuChartInstance = renderLineChart(cpuChartRef, cpuChartInstance, data, {
    seriesKey: 'cpu',
    name: 'CPU %',
    color: '#165DFF',
    yAxisFormatter: value => `${value}%`
  })
  memoryChartInstance = renderLineChart(memoryChartRef, memoryChartInstance, data, {
    seriesKey: 'memory',
    name: '内存 %',
    color: '#00B42A',
    yAxisFormatter: value => `${value}%`
  })
  storageChartInstance = renderLineChart(storageChartRef, storageChartInstance, data, {
    seriesKey: 'storage',
    name: '存储 %',
    color: '#F77234',
    yAxisFormatter: value => `${value}%`
  })
  networkChartInstance = renderLineChart(networkChartRef, networkChartInstance, data, {
    seriesKey: ['netIn', 'netOut'],
    name: ['入站', '出站'],
    color: ['#14C9C9', '#F53F3F'],
    yAxisFormatter: value => formatThroughput(value, true)
  })
  // 确保图表正确调整大小
  nextTick(() => {
    cpuChartInstance?.resize()
    memoryChartInstance?.resize()
    storageChartInstance?.resize()
    networkChartInstance?.resize()
  })
}

function renderLineChart(refEl, chartInstance, data, config) {
  if (!refEl.value) {
    if (chartInstance) {
      chartInstance.dispose()
    }
    return null
  }
  if (!chartInstance) {
    chartInstance = echarts.init(refEl.value, null, {
      width: 'auto',
      height: 'auto'
    })
  }
  const timeData = data.map(item => item.time)
  const series = []
  if (Array.isArray(config.seriesKey)) {
    config.seriesKey.forEach((key, idx) => {
      series.push({
        name: config.name[idx] || key,
        type: 'line',
        smooth: true,
        showSymbol: false,
        data: data.map(item => item[key]),
        areaStyle: {
          opacity: 0.08
        },
        lineStyle: {
          width: 2,
          color: config.color[idx]
        }
      })
    })
  } else {
    series.push({
      name: config.name,
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: data.map(item => item[config.seriesKey]),
      areaStyle: {
        opacity: 0.08
      },
      lineStyle: {
        width: 2,
        color: config.color
      }
    })
  }
  // 计算Y轴的最大值，用于统一单位显示
  let maxValue = 0
  if (Array.isArray(config.seriesKey)) {
    config.seriesKey.forEach(key => {
      const values = data.map(item => item[key] || 0)
      maxValue = Math.max(maxValue, ...values)
    })
  } else {
    const values = data.map(item => item[config.seriesKey] || 0)
    maxValue = Math.max(maxValue, ...values)
  }

  // 网络吞吐需要统一单位
  let yAxisFormatter = config.yAxisFormatter
  const isNetworkChart = Array.isArray(config.seriesKey) && (config.seriesKey.includes('netIn') || config.seriesKey.includes('netOut'))
  if (isNetworkChart) {
    // 确定网络吞吐的统一单位
    const baseUnit = maxValue >= 1024 * 1024 ? 'MB' : maxValue >= 1024 ? 'KB' : 'B'
    yAxisFormatter = value => {
      if (!value && value !== 0) return '0 B'
      let num = Number(value)
      if (baseUnit === 'MB') {
        num = num / (1024 * 1024)
        return `${num.toFixed(1)} MB`
      } else if (baseUnit === 'KB') {
        num = num / 1024
        return `${num.toFixed(1)} KB`
      }
      return `${num.toFixed(0)} B`
    }
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      borderColor: 'transparent',
      textStyle: {
        color: '#fff',
        fontSize: 12
      },
      formatter: params => {
        if (!params?.length) return ''
        const time = formatTime(params[0].axisValue)
        const lines = params.map(item => {
          const color = item.color
          const label = item.seriesName
          const value = config.yAxisFormatter ? config.yAxisFormatter(item.value) : item.value
          return `<span style="display:inline-block;margin-right:6px;width:10px;height:10px;border-radius:50%;background:${color}"></span>${label}: ${value}`
        })
        return `<div style="padding: 4px 0;">${time}<br/>${lines.join('<br/>')}</div>`
      }
    },
    grid: {
      left: '5%',
      right: '5%',
      top: '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: timeData,
      axisLabel: {
        formatter: value => formatTime(value, true),
        fontSize: 11,
        color: '#86909c',
        rotate: 0,
        interval: 'auto'
      },
      axisLine: {
        lineStyle: {
          color: '#e5e6eb'
        }
      },
      splitLine: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: value => yAxisFormatter ? yAxisFormatter(value) : (config.yAxisFormatter ? config.yAxisFormatter(value) : value),
        fontSize: 11,
        color: '#86909c',
        margin: 8
      },
      axisLine: {
        lineStyle: {
          color: '#e5e6eb'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#f2f3f5',
          type: 'dashed'
        }
      },
      scale: false
    },
    series
  }
  chartInstance.setOption(option)
  // 确保图表正确计算尺寸
  chartInstance.resize()
  return chartInstance
}

function formatBytes(value) {
  if (!value && value !== 0) return '-'
  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
  let index = 0
  let num = Number(value)
  while (num >= 1024 && index < units.length - 1) {
    num /= 1024
    index++
  }
  return `${num.toFixed(num >= 10 || num < 1 ? 1 : 2)} ${units[index]}`
}

function formatThroughput(value, short = false) {
  if (!value && value !== 0) return '-'
  const units = [
    { unit: 'B', scale: 1 },
    { unit: 'KB', scale: 1024 },
    { unit: 'MB', scale: 1024 ** 2 },
    { unit: 'GB', scale: 1024 ** 3 }
  ]
  let num = Number(value)
  let idx = 0
  while (num >= 1024 && idx < units.length - 1) {
    num /= 1024
    idx++
  }
  const fixed = num >= 10 || short ? 1 : 2
  return `${num.toFixed(fixed)} ${units[idx].unit}${short ? '' : '/s'}`
}

function formatDuration(seconds) {
  const sec = Number(seconds || 0)
  if (!sec) return '-'
  const days = Math.floor(sec / 86400)
  const hours = Math.floor((sec % 86400) / 3600)
  const minutes = Math.floor((sec % 3600) / 60)
  if (days > 0) return `${days}天${hours}小时`
  if (hours > 0) return `${hours}小时${minutes}分钟`
  if (minutes > 0) return `${minutes}分钟`
  return `${sec}s`
}

function formatTime(timestamp, short = false) {
  if (!timestamp) return '-'
  const date = new Date(Number(timestamp))
  if (Number.isNaN(date.getTime())) return '-'
  if (short) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).replace(/\//g, '-')
}

function formatLoad(loadavg) {
  if (!loadavg && loadavg !== 0) return '-'
  if (Array.isArray(loadavg)) {
    return loadavg.map(item => Number(item || 0).toFixed(2)).join(' / ')
  }
  return Number(loadavg).toFixed(2)
}

function getProgressStatus(percent, thresholds = []) {
  if (percent >= (thresholds[1] || 90)) return 'danger'
  if (percent >= (thresholds[0] || 75)) return 'warning'
  return 'success'
}

function getStatusTag(status) {
  if (!status) {
    return { color: 'gray', text: '未知' }
  }
  const lower = status.toLowerCase()
  if (lower === 'online' || lower === 'running') {
    return { color: 'green', text: '在线' }
  }
  if (lower === 'offline') {
    return { color: 'red', text: '离线' }
  }
  return { color: 'orange', text: status }
}

function handleResize() {
  cpuChartInstance?.resize()
  memoryChartInstance?.resize()
  storageChartInstance?.resize()
  networkChartInstance?.resize()
}

watch(selectedServer, () => {
  handleServerChange()
})

watch(selectedNode, () => {
  handleNodeChange()
})

watch(formattedMetrics, () => {
  nextTick(() => updateCharts())
})

onMounted(() => {
  loadServers()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  cpuChartInstance?.dispose()
  memoryChartInstance?.dispose()
  storageChartInstance?.dispose()
  networkChartInstance?.dispose()
})
</script>

<style scoped>
.pve-node-monitor {
  padding: 24px;
  background: var(--color-bg-1);
  min-height: 100%;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow-x: visible;
}

.filter-card {
  margin-bottom: 24px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: visible;
}

.filter-card :deep(.arco-card-body) {
  padding: 24px;
}

.filter-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  align-items: flex-end;
}

.filter-item {
  flex: 0 0 auto;
  min-width: 200px;
}

.filter-item .label {
  font-size: 13px;
  color: var(--color-text-2);
  margin-bottom: 8px;
  font-weight: 500;
}

.filter-item.actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 16px;
}

.filter-item .meta {
  font-size: 12px;
  color: var(--color-text-2);
  white-space: nowrap;
}

.filter-item .meta span:first-child {
  color: var(--color-text-3);
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 24px;
  width: 100%;
  box-sizing: border-box;
}

.summary-row > .stat-card {
  flex: 0 0 auto;
  width: 100%;
}

.stat-card {
  background: var(--color-bg-2);
  border-radius: 8px;
  padding: 24px;
  height: 100%;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
  transition: all 0.3s ease;
  overflow: visible;
  border: 1px solid var(--color-border-2);
  display: flex;
  flex-direction: column;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
  border-color: var(--color-border-3);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: var(--color-text-1);
  font-weight: 500;
  margin-bottom: 16px;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: var(--color-text-1);
  margin: 16px 0 12px;
  line-height: 1.2;
}

.stat-sub-value {
  font-size: 18px;
  font-weight: 500;
  color: var(--color-text-2);
  margin-bottom: 12px;
}

.stat-desc {
  font-size: 12px;
  color: var(--color-text-3);
  margin-top: 8px;
}

.stat-card :deep(.arco-progress) {
  margin-top: 8px;
}

.chart-card {
  margin-bottom: 24px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: visible;
}

.chart-card :deep(.arco-card-body) {
  padding: 24px;
}

.chart-grid {
  width: 100%;
}

.chart-grid :deep(.arco-grid-item) {
  min-width: 0;
  width: 100%;
}

.chart-item-card {
  height: 100%;
  width: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.chart-item-card :deep(.arco-card) {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-item-card :deep(.arco-card-body) {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  width: 100%;
  min-width: 0;
}

.chart-container {
  width: 100%;
  height: 450px;
  min-height: 450px;
  flex: 1;
  min-width: 0;
  box-sizing: border-box;
}

.alert-card {
  margin-bottom: 24px;
  width: 100%;
  max-width: 100%;

  box-sizing: border-box;
  overflow: visible;
}

.alert-card :deep(.arco-card-body) {
  padding: 24px;
}

.alert-card .alert-item {
  margin-bottom: 12px;
}

.alert-card .alert-item:last-child {
  margin-bottom: 0;
}

/* 响应式布局 */
@media (max-width: 1600px) {
  .chart-card :deep(.arco-grid) {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

@media (max-width: 1200px) {
  .chart-card :deep(.arco-grid) {
    grid-template-columns: 1fr !important;
  }
}

@media (max-width: 992px) {
  .pve-node-monitor {
    padding: 20px;
  }

  .filter-card,
  .chart-card,
  .alert-card {
    margin-bottom: 20px;
  }

  .filter-card :deep(.arco-card-body),
  .chart-card :deep(.arco-card-body),
  .alert-card :deep(.arco-card-body),
  .stat-card :deep(.arco-card-body) {
    padding: 20px;
  }

  .filter-grid {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
  }

  .filter-item {
    min-width: 100%;
  }

  .filter-item.actions {
    margin-left: 0;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .summary-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-bottom: 20px;
  }

  .summary-row > .stat-card {
    width: 100%;
  }

  .chart-grid {
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .pve-node-monitor {
    padding: 16px;
  }

  .filter-card,
  .chart-card,
  .alert-card {
    margin-bottom: 16px;
  }

  .filter-card :deep(.arco-card-body),
  .chart-card :deep(.arco-card-body),
  .alert-card :deep(.arco-card-body),
  .stat-card :deep(.arco-card-body) {
    padding: 16px;
  }

  .filter-grid {
    gap: 16px;
  }

  .summary-row {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .summary-row > .stat-card {
    width: 100%;
  }

  .stat-value {
    font-size: 28px;
  }
}
</style>

