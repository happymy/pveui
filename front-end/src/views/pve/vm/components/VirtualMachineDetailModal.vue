<template>
  <a-modal
    v-model:visible="visibleProxy"
    title="虚拟机详情"
    :footer="false"
    :width="detailModalWidth"
    unmount-on-close
  >
    <a-spin :loading="detailLoading">
      <div v-if="currentVM" class="vm-detail">
        <div class="vm-detail-header">
          <div>
            <div class="vm-detail-name">{{ currentVM.name }}</div>
            <div class="vm-detail-sub">
              VMID {{ currentVM.vmid }} · 节点 {{ currentVM.node || '-' }} · 服务器 {{ currentVM.server_name || '-' }}
            </div>
          </div>
          <div class="vm-detail-status">
            <a-tag :color="getStatusColor(currentVM.status)">
              {{ getStatusText(currentVM.status) }}
            </a-tag>
          </div>
        </div>

        <a-tabs v-model:active-key="detailActiveTab">
          <a-tab-pane key="overview" title="概览">
            <VMOverviewTab :vm="currentVM" />
          </a-tab-pane>
          <a-tab-pane key="console" title="控制台">
            <VMConsoleTab
              :vm="currentVM"
              :vm-id="vmId"
              :active="detailActiveTab === 'console'"
            />
          </a-tab-pane>
          <a-tab-pane key="hardware" title="硬件">
            <VMHardwareTab
              :vm="currentVM"
              :vm-id="vmId"
              @refresh="loadDetail"
            />
          </a-tab-pane>
          <a-tab-pane key="config" title="配置">
            <VMConfigTab :vm="currentVM" />
          </a-tab-pane>
        </a-tabs>
      </div>
      <a-empty v-else description="暂无虚拟机数据" />
    </a-spin>
  </a-modal>
</template>

<script setup>
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue'
import { Message } from '@arco-design/web-vue'
import { getVirtualMachine } from '@/api/pve'
import VMOverviewTab from './VMOverviewTab.vue'
import VMConsoleTab from './VMConsoleTab.vue'
import VMHardwareTab from './VMHardwareTab.vue'
import VMConfigTab from './VMConfigTab.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  vmId: {
    type: [Number, String],
    default: null
  },
  fallbackRecord: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible'])

const visibleProxy = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const detailLoading = ref(false)
const detailActiveTab = ref('overview')
const detailModalWidth = ref(960)
const currentVM = ref(null)


const getStatusColor = (status) => {
  const colorMap = {
    running: 'green',
    stopped: 'red',
    paused: 'orange',
    unknown: 'gray'
  }
  return colorMap[status] || 'gray'
}

const getStatusText = (status) => {
  const textMap = {
    running: '运行中',
    stopped: '已停止',
    paused: '已暂停',
    unknown: '未知'
  }
  return textMap[status] || '未知'
}


const updateDetailWidth = () => {
  const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 1200
  // 增加控制台模态框的宽度，以便更好地显示 VNC 画面
  detailModalWidth.value = Math.max(Math.min(viewportWidth - 80, 1600), 1000)
}

const loadDetail = async (options = {}) => {
  const { preserveTab = false } = options
  if (!props.visible) {
    return
  }
  if (!preserveTab) {
    detailActiveTab.value = 'overview'
  }
  updateDetailWidth()
  if (!props.vmId) {
    currentVM.value = props.fallbackRecord || null
    return
  }
  detailLoading.value = true
  try {
    const res = await getVirtualMachine(props.vmId)
    currentVM.value = res
  } catch (error) {
    currentVM.value = props.fallbackRecord || null
    Message.error('获取虚拟机详情失败：' + (error.message || '未知错误'))
  } finally {
    detailLoading.value = false
  }
}

watch(
  () => props.visible,
  (val) => {
    if (val) {
      loadDetail()
    } else {
      currentVM.value = null
    }
  }
)

watch(
  () => props.vmId,
  (val, oldVal) => {
    if (props.visible && val !== oldVal) {
      loadDetail()
    }
  }
)

onMounted(() => {
  updateDetailWidth()
  window.addEventListener('resize', updateDetailWidth)
  if (props.visible) {
    loadDetail()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateDetailWidth)
})
</script>

<style scoped>
.vm-detail {
  width: 100%;
  overflow: hidden;
  max-width: 100%;
  box-sizing: border-box;
}

.vm-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.vm-detail-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-1);
}

.vm-detail-sub {
  color: var(--color-text-3);
  margin-top: 4px;
}

/* 确保控制台 tab 下的卡片不会超出视口 */
:deep(.arco-tabs-content) {
  overflow-x: hidden;
  max-width: 100%;
}

:deep(.arco-tabs-content .arco-card) {
  max-width: 100%;
  overflow-x: hidden;
}
</style>

