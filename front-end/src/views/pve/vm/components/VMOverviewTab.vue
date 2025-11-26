<template>
  <div class="vm-overview-tab">
    <a-row :gutter="16">
      <a-col :span="12">
        <a-card title="基本信息" :bordered="false">
          <a-descriptions :column="1" bordered :data="overviewData.basic" />
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="资源" :bordered="false">
          <a-descriptions :column="1" bordered :data="overviewData.resource" />
        </a-card>
      </a-col>
    </a-row>
    <a-card title="时间与状态" :bordered="false" style="margin-top: 16px;">
      <a-descriptions :column="2" bordered :data="overviewData.meta" />
    </a-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  vm: {
    type: Object,
    required: true
  }
})

const getStatusText = (status) => {
  const textMap = {
    running: '运行中',
    stopped: '已停止',
    paused: '已暂停',
    unknown: '未知'
  }
  return textMap[status] || '未知'
}

const overviewData = computed(() => {
  const vm = props.vm
  if (!vm) {
    return { basic: [], resource: [], meta: [] }
  }
  return {
    basic: [
      { label: '虚拟机ID', value: vm.vmid || '-' },
      { label: '节点', value: vm.node || '-' },
      { label: '所属服务器', value: vm.server_name || '-' },
      { label: '描述', value: vm.description || '无' }
    ],
    resource: [
      { label: 'CPU核心数', value: vm.cpu_cores ? `${vm.cpu_cores} vCPU` : '-' },
      { label: '内存', value: vm.memory_mb ? `${vm.memory_mb} MB` : '-' },
      { label: '磁盘', value: vm.disk_gb ? `${vm.disk_gb} GB` : '-' },
      { label: 'IP地址', value: vm.ip_address || '未分配' }
    ],
    meta: [
      { label: '创建时间', value: vm.created_at || '-' },
      { label: '更新时间', value: vm.updated_at || '-' },
      { label: '状态', value: getStatusText(vm.status) }
    ]
  }
})
</script>

<style scoped>
.vm-overview-tab {
  width: 100%;
  max-height: 500px;
  overflow-y: auto;
}
</style>

