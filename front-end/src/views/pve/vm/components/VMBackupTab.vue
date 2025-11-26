<template>
  <div class="vm-backup-tab">
    <a-card :bordered="false">
      <template #title>
        <div class="backup-header">
          <span>备份列表</span>
          <div class="backup-actions">
            <a-button size="small" @click="loadData" :loading="loading">刷新</a-button>
            <a-button
              type="primary"
              size="small"
              style="margin-left: 8px;"
              :disabled="!backupStorages.length"
              @click="openCreate"
            >
              创建备份
            </a-button>
          </div>
        </div>
      </template>

      <a-alert v-if="!backupStorages.length" type="warning" show-icon style="margin-bottom: 12px;">
        <template #title>暂无可用于备份的存储</template>
        请先在 PVE 中为节点配置支持 backup 的存储后再尝试创建备份。
      </a-alert>

      <a-table
        :data="backups"
        :loading="loading"
        :pagination="false"
        size="small"
        row-key="volid"
      >
        <template #columns>
          <a-table-column title="存储" data-index="storage" />
          <a-table-column title="备份文件" data-index="volid" />
          <a-table-column title="大小">
            <template #cell="{ record }">
              {{ formatSize(record.size) }}
            </template>
          </a-table-column>
          <a-table-column title="创建时间">
            <template #cell="{ record }">
              {{ formatTime(record.ctime) }}
            </template>
          </a-table-column>
          <a-table-column title="备注" data-index="notes" />
        </template>
      </a-table>
    </a-card>

    <a-modal
      v-model:visible="createVisible"
      title="创建备份"
      :width="480"
      :footer="false"
      unmount-on-close
    >
      <a-form :model="createForm" layout="vertical">
        <a-form-item label="目标存储">
          <a-select v-model="createForm.storage">
            <a-option
              v-for="item in backupStorages"
              :key="item.storage"
              :value="item.storage"
            >
              {{ item.storage }} ({{ item.type || '未知类型' }})
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="备份模式">
          <a-select v-model="createForm.mode">
            <a-option value="snapshot">snapshot (在线备份)</a-option>
            <a-option value="suspend">suspend (冻结)</a-option>
            <a-option value="stop">stop (停机)</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="压缩">
          <a-select v-model="createForm.compress">
            <a-option value="zstd">zstd</a-option>
            <a-option value="lzo">lzo</a-option>
            <a-option value="gzip">gzip</a-option>
            <a-option value="none">无压缩</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="其他选项">
          <a-checkbox v-model="createForm.remove">备份完成后删除旧备份</a-checkbox>
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea
            v-model="createForm.notes"
            placeholder="可选，记录此次备份说明"
            allow-clear
            :max-length="200"
            show-word-limit
            auto-size
          />
        </a-form-item>
      </a-form>
      <div class="modal-footer">
        <a-button @click="createVisible = false" style="margin-right: 12px;">取消</a-button>
        <a-button type="primary" :loading="creating" @click="handleCreate">
          创建
        </a-button>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import dayjs from 'dayjs'
import { Message } from '@arco-design/web-vue'
import { getVMBackups, createVMBackup } from '@/api/pve'

const props = defineProps({
  vm: {
    type: Object,
    default: null
  },
  vmId: {
    type: [Number, String],
    default: null
  }
})

const loading = ref(false)
const backups = ref([])
const storages = ref([])
const createVisible = ref(false)
const creating = ref(false)

const createForm = ref({
  storage: '',
  mode: 'snapshot',
  compress: 'zstd',
  remove: false,
  notes: ''
})

const backupStorages = computed(() => storages.value || [])

const formatSize = (size) => {
  if (!size || size <= 0) return '-'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let index = 0
  let value = size
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024
    index += 1
  }
  return `${value.toFixed(2)} ${units[index]}`
}

const formatTime = (ctime) => {
  if (!ctime) return '-'
  return dayjs.unix(ctime).format('YYYY-MM-DD HH:mm')
}

const loadData = async () => {
  if (!props.vmId) {
    backups.value = []
    storages.value = []
    return
  }
  loading.value = true
  try {
    const res = await getVMBackups(props.vmId)
    backups.value = res?.backups || []
    storages.value = res?.storages || []
    if (!createForm.value.storage && storages.value.length) {
      createForm.value.storage = storages.value[0].storage
    }
  } catch (error) {
    Message.error('获取备份列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  if (!backupStorages.value.length) {
    Message.warning('暂无可用于备份的存储')
    return
  }
  if (!createForm.value.storage) {
    createForm.value.storage = backupStorages.value[0].storage
  }
  createVisible.value = true
}

const handleCreate = async () => {
  if (!props.vmId) return
  if (!createForm.value.storage) {
    Message.warning('请选择备份存储')
    return
  }
  creating.value = true
  try {
    await createVMBackup(props.vmId, {
      storage: createForm.value.storage,
      mode: createForm.value.mode,
      compress: createForm.value.compress,
      remove: createForm.value.remove,
      notes: createForm.value.notes
    })
    Message.success('备份任务已提交')
    createVisible.value = false
    await loadData()
  } catch (error) {
    Message.error('创建备份失败：' + (error.message || '未知错误'))
  } finally {
    creating.value = false
  }
}

watch(
  () => props.vmId,
  (val, oldVal) => {
    if (val && val !== oldVal) {
      loadData()
    }
  }
)

onMounted(() => {
  if (props.vmId) {
    loadData()
  }
})
</script>

<style scoped>
.vm-backup-tab {
  width: 100%;
}

.backup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.backup-actions {
  display: flex;
  align-items: center;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>

