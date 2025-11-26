<template>
  <div class="vm-snapshot-tab">
    <a-card :bordered="false">
      <template #title>
        <div class="snapshot-header">
          <span>快照列表</span>
          <div class="snapshot-actions">
            <a-button size="small" @click="loadData" :loading="loading">刷新</a-button>
            <a-button type="primary" size="small" style="margin-left: 8px;" @click="openCreate">
              创建快照
            </a-button>
          </div>
        </div>
      </template>

      <a-table
        :data="snapshots"
        :loading="loading"
        :pagination="false"
        :scroll="{ y: 400 }"
        size="small"
        row-key="name"
      >
        <template #columns>
          <a-table-column title="名称">
            <template #cell="{ record }">
              <a-tag v-if="record.is_current" color="blue">当前</a-tag>
              {{ record.name }}
            </template>
          </a-table-column>
          <a-table-column title="描述" data-index="description" />
          <a-table-column title="创建时间">
            <template #cell="{ record }">
              {{ formatTime(record.snaptime) }}
            </template>
          </a-table-column>
          <a-table-column title="包含内存">
            <template #cell="{ record }">
              <a-tag :color="record.vmstate ? 'green' : 'gray'">
                {{ record.vmstate ? '是' : '否' }}
              </a-tag>
            </template>
          </a-table-column>
          <a-table-column title="父快照" data-index="parent" />
          <a-table-column title="操作">
            <template #cell="{ record }">
              <a-space size="mini">
                <a-button
                  type="text"
                  size="small"
                  :disabled="record.is_current"
                  @click="handleRollback(record)"
                >
                  回滚
                </a-button>
                <a-popconfirm
                  content="确定要删除该快照吗？"
                  @ok="handleDelete(record)"
                  :disabled="record.is_current"
                >
                  <a-button type="text" size="small" status="danger" :disabled="record.is_current">
                    删除
                  </a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table-column>
        </template>
      </a-table>
    </a-card>

    <a-modal
      v-model:visible="createVisible"
      title="创建快照"
      :width="480"
      :footer="false"
      unmount-on-close
    >
      <a-form :model="createForm" layout="vertical">
        <a-form-item label="快照名称">
          <a-input v-model="createForm.name" placeholder="请输入快照名称" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea
            v-model="createForm.description"
            placeholder="可选，用于说明快照用途"
            auto-size
            allow-clear
          />
        </a-form-item>
        <a-form-item>
          <a-checkbox v-model="createForm.include_memory">
            同时保存内存（将占用更多时间和空间）
          </a-checkbox>
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
import { ref, watch, onMounted } from 'vue'
import dayjs from 'dayjs'
import { Message } from '@arco-design/web-vue'
import {
  getVMSnapshots,
  createVMSnapshot,
  rollbackVMSnapshot,
  deleteVMSnapshot
} from '@/api/pve'

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
const snapshots = ref([])
const createVisible = ref(false)
const creating = ref(false)

const createForm = ref({
  name: '',
  description: '',
  include_memory: false
})

const formatTime = (snaptime) => {
  if (!snaptime) return '-'
  return dayjs.unix(snaptime).format('YYYY-MM-DD HH:mm:ss')
}

const loadData = async () => {
  if (!props.vmId) {
    snapshots.value = []
    return
  }
  loading.value = true
  try {
    const res = await getVMSnapshots(props.vmId)
    snapshots.value = res?.snapshots || []
  } catch (error) {
    Message.error('获取快照列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  createForm.value = {
    name: '',
    description: '',
    include_memory: false
  }
  createVisible.value = true
}

const handleCreate = async () => {
  if (!props.vmId) return
  if (!createForm.value.name) {
    Message.warning('请输入快照名称')
    return
  }
  creating.value = true
  try {
    await createVMSnapshot(props.vmId, {
      name: createForm.value.name,
      description: createForm.value.description,
      include_memory: createForm.value.include_memory
    })
    Message.success('快照任务已提交')
    createVisible.value = false
    await loadData()
  } catch (error) {
    Message.error('创建快照失败：' + (error.message || '未知错误'))
  } finally {
    creating.value = false
  }
}

const handleRollback = async (snapshot) => {
  if (!props.vmId || snapshot.is_current) return
  try {
    await rollbackVMSnapshot(props.vmId, { name: snapshot.name })
    Message.success('回滚任务已提交')
    await loadData()
  } catch (error) {
    Message.error('回滚快照失败：' + (error.message || '未知错误'))
  }
}

const handleDelete = async (snapshot) => {
  if (!props.vmId || snapshot.is_current) return
  try {
    await deleteVMSnapshot(props.vmId, { name: snapshot.name })
    Message.success('删除快照任务已提交')
    await loadData()
  } catch (error) {
    Message.error('删除快照失败：' + (error.message || '未知错误'))
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
.vm-snapshot-tab {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.vm-snapshot-tab :deep(.arco-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.vm-snapshot-tab :deep(.arco-card-body) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.snapshot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.snapshot-actions {
  display: flex;
  align-items: center;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>

