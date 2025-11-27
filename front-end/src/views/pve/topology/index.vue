<template>
  <div class="pve-topology-list">
    <a-card class="topology-card" :loading="loading">
      <template #title>
        <a-typography-title :heading="4">拓扑管理</a-typography-title>
      </template>
      <template #extra>
        <a-space>
          <a-input-search
            v-model="searchKeyword"
            placeholder="搜索名称 / 描述"
            allow-clear
            @search="handleSearch"
            @clear="handleSearch"
            style="width: 220px"
          />
          <a-button type="primary" @click="handleCreate">
            <template #icon>
              <icon-plus />
            </template>
            新建拓扑
          </a-button>
        </a-space>
      </template>

      <a-table
        :columns="columns"
        :data="tableData"
        :pagination="pagination"
        :loading="loading"
        row-key="id"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        :bordered="false"
      >
        <template #name="{ record }">
          <a-space direction="vertical" size="mini">
            <span class="topology-name">{{ record.name }}</span>
            <span class="topology-desc">{{ record.description || '—' }}</span>
          </a-space>
        </template>
        <template #status="{ record }">
          <a-tag :color="record.is_active ? 'green' : 'gray'">
            {{ record.is_active ? '启用' : '禁用' }}
          </a-tag>
        </template>
        <template #updated_at="{ record }">
          {{ formatTime(record.updated_at) }}
        </template>
        <template #actions="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="handleEdit(record)">
              <icon-edit />
              编辑
            </a-button>
            <a-popconfirm content="确定删除该拓扑？" @ok="() => handleDelete(record)">
              <a-button type="text" size="small" status="danger">
                <icon-delete />
                删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { IconPlus, IconEdit, IconDelete } from '@arco-design/web-vue/es/icon'
import { getNetworkTopologies, deleteNetworkTopology } from '@/api/pve'

const router = useRouter()

const loading = ref(false)
const tableData = ref([])
const searchKeyword = ref('')
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: true
})

const columns = [
  { title: '名称 / 描述', dataIndex: 'name', slotName: 'name', width: 320 },
  { title: '节点数', dataIndex: ['metadata', 'stats', 'nodes'], width: 100 },
  { title: '连线数', dataIndex: ['metadata', 'stats', 'edges'], width: 100 },
  { title: '状态', dataIndex: 'is_active', slotName: 'status', width: 120 },
  { title: '更新时间', dataIndex: 'updated_at', slotName: 'updated_at', width: 200 },
  { title: '操作', slotName: 'actions', width: 180 }
]

const formatTime = (value) => {
  if (!value) return '-'
  try {
    return new Date(value).toLocaleString()
  } catch (e) {
    return value
  }
}

const fetchList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const res = await getNetworkTopologies(params)
    if (Array.isArray(res)) {
      tableData.value = res
      pagination.total = res.length
    } else {
      tableData.value = res?.results || []
      pagination.total = res?.count || 0
    }
  } catch (error) {
    Message.error('获取拓扑列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  fetchList()
}

const handlePageChange = (page) => {
  pagination.current = page
  fetchList()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.current = 1
  fetchList()
}

const handleCreate = () => {
  router.push({ name: 'PVETopologyEdit' })
}

const handleEdit = (record) => {
  if (!record?.id) return
  router.push({ name: 'PVETopologyEdit', params: { id: record.id } })
}

const handleDelete = async (record) => {
  if (!record?.id) return
  try {
    await deleteNetworkTopology(record.id)
    Message.success('删除成功')
    fetchList()
  } catch (error) {
    Message.error('删除失败：' + (error.message || '未知错误'))
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.pve-topology-list {
  padding: 16px;
}

.topology-card {
  width: 100%;
}

.topology-name {
  font-weight: 600;
  color: var(--color-text-1);
}

.topology-desc {
  font-size: 12px;
  color: var(--color-text-3);
}
</style>
<template>
  <div class="pve-topology-list">
    <a-card class="topology-card" :loading="loading">
      <template #title>
        <a-typography-title :heading="4">拓扑管理</a-typography-title>
      </template>
      <template #extra>
        <a-space>
          <a-input-search
            v-model="searchKeyword"
            placeholder="搜索名称 / 描述"
            allow-clear
            @search="handleSearch"
            @clear="handleSearch"
            style="width: 220px"
          />
          <a-button type="primary" @click="handleCreate">
            <template #icon>
              <icon-plus />
            </template>
            新建拓扑
          </a-button>
        </a-space>
      </template>

      <a-table
        :columns="columns"
        :data="tableData"
        :pagination="pagination"
        :loading="loading"
        row-key="id"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        :bordered="false"
      >
        <template #name="{ record }">
          <a-space direction="vertical" size="mini">
            <span class="topology-name">{{ record.name }}</span>
            <span class="topology-desc">{{ record.description || '—' }}</span>
          </a-space>
        </template>
        <template #status="{ record }">
          <a-tag :color="record.is_active ? 'green' : 'gray'">
            {{ record.is_active ? '启用' : '禁用' }}
          </a-tag>
        </template>
        <template #updated_at="{ record }">
          {{ formatTime(record.updated_at) }}
        </template>
        <template #actions="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="handleEdit(record)">
              <icon-edit />
              编辑
            </a-button>
            <a-popconfirm content="确定删除该拓扑？" @ok="() => handleDelete(record)">
              <a-button type="text" size="small" status="danger">
                <icon-delete />
                删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { IconPlus, IconEdit, IconDelete } from '@arco-design/web-vue/es/icon'
import { getNetworkTopologies, deleteNetworkTopology } from '@/api/pve'

const router = useRouter()

const loading = ref(false)
const tableData = ref([])
const searchKeyword = ref('')
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: true
})

const columns = [
  { title: '名称 / 描述', dataIndex: 'name', slotName: 'name', width: 320 },
  { title: '节点数', dataIndex: ['metadata', 'stats', 'nodes'], width: 100 },
  { title: '连线数', dataIndex: ['metadata', 'stats', 'edges'], width: 100 },
  { title: '状态', dataIndex: 'is_active', slotName: 'status', width: 120 },
  { title: '更新时间', dataIndex: 'updated_at', slotName: 'updated_at', width: 200 },
  { title: '操作', slotName: 'actions', width: 180 }
]

const formatTime = (value) => {
  if (!value) return '-'
  try {
    return new Date(value).toLocaleString()
  } catch (e) {
    return value
  }
}

const fetchList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const res = await getNetworkTopologies(params)
    if (Array.isArray(res)) {
      tableData.value = res
      pagination.total = res.length
    } else {
      tableData.value = res?.results || []
      pagination.total = res?.count || 0
    }
  } catch (error) {
    Message.error('获取拓扑列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  fetchList()
}

const handlePageChange = (page) => {
  pagination.current = page
  fetchList()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.current = 1
  fetchList()
}

const handleCreate = () => {
  router.push({ name: 'PVETopologyEdit' })
}

const handleEdit = (record) => {
  if (!record?.id) return
  router.push({ name: 'PVETopologyEdit', params: { id: record.id } })
}

const handleDelete = async (record) => {
  if (!record?.id) return
  try {
    await deleteNetworkTopology(record.id)
    Message.success('删除成功')
    fetchList()
  } catch (error) {
    Message.error('删除失败：' + (error.message || '未知错误'))
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.pve-topology-list {
  padding: 16px;
}

.topology-card {
  width: 100%;
}

.topology-name {
  font-weight: 600;
  color: var(--color-text-1);
}

.topology-desc {
  font-size: 12px;
  color: var(--color-text-3);
}
</style>
<template>
  <div class="pve-topology-list">
    <a-card class="topology-card" :loading="loading">
      <template #title>
        <a-typography-title :heading="4">拓扑管理</a-typography-title>
      </template>
      <template #extra>
        <a-space>
          <a-input-search
            v-model="searchKeyword"
            placeholder="搜索名称 / 描述"
            allow-clear
            @search="handleSearch"
            @clear="handleSearch"
            style="width: 220px"
          />
          <a-button type="primary" @click="handleCreate">
            <template #icon>
              <icon-plus />
            </template>
            新建拓扑
          </a-button>
        </a-space>
      </template>

      <a-table
        :columns="columns"
        :data="tableData"
        :pagination="pagination"
        :loading="loading"
        row-key="id"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        :bordered="false"
      >
        <template #name="{ record }">
          <a-space direction="vertical" size="mini">
            <span class="topology-name">{{ record.name }}</span>
            <span class="topology-desc">{{ record.description || '—' }}</span>
          </a-space>
        </template>
        <template #status="{ record }">
          <a-tag :color="record.is_active ? 'green' : 'gray'">
            {{ record.is_active ? '启用' : '禁用' }}
          </a-tag>
        </template>
        <template #updated_at="{ record }">
          {{ formatTime(record.updated_at) }}
        </template>
        <template #actions="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="handleEdit(record)">
              <icon-edit />
              编辑
            </a-button>
            <a-popconfirm content="确定删除该拓扑？" @ok="() => handleDelete(record)">
              <a-button type="text" size="small" status="danger">
                <icon-delete />
                删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { IconPlus, IconEdit, IconDelete } from '@arco-design/web-vue/es/icon'
import { getNetworkTopologies, deleteNetworkTopology } from '@/api/pve'

const router = useRouter()

const loading = ref(false)
const tableData = ref([])
const searchKeyword = ref('')
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: true
})

const columns = [
  { title: '名称 / 描述', dataIndex: 'name', slotName: 'name', width: 320 },
  { title: '节点数', dataIndex: ['metadata', 'stats', 'nodes'], width: 100 },
  { title: '连线数', dataIndex: ['metadata', 'stats', 'edges'], width: 100 },
  { title: '状态', dataIndex: 'is_active', slotName: 'status', width: 120 },
  { title: '更新时间', dataIndex: 'updated_at', slotName: 'updated_at', width: 200 },
  { title: '操作', slotName: 'actions', width: 180 }
]

const formatTime = (value) => {
  if (!value) return '-'
  try {
    return new Date(value).toLocaleString()
  } catch (e) {
    return value
  }
}

const fetchList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const res = await getNetworkTopologies(params)
    if (Array.isArray(res)) {
      tableData.value = res
      pagination.total = res.length
    } else {
      tableData.value = res?.results || []
      pagination.total = res?.count || 0
    }
  } catch (error) {
    Message.error('获取拓扑列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  fetchList()
}

const handlePageChange = (page) => {
  pagination.current = page
  fetchList()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.current = 1
  fetchList()
}

const handleCreate = () => {
  router.push({ name: 'PVETopologyEdit' })
}

const handleEdit = (record) => {
  if (!record?.id) return
  router.push({ name: 'PVETopologyEdit', params: { id: record.id } })
}

const handleDelete = async (record) => {
  if (!record?.id) return
  try {
    await deleteNetworkTopology(record.id)
    Message.success('删除成功')
    fetchList()
  } catch (error) {
    Message.error('删除失败：' + (error.message || '未知错误'))
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.pve-topology-list {
  padding: 16px;
}

.topology-card {
  width: 100%;
}

.topology-name {
  font-weight: 600;
  color: var(--color-text-1);
}

.topology-desc {
  font-size: 12px;
  color: var(--color-text-3);
}
</style>
<template>
  <div class="pve-topology-page">
    <a-row :gutter="16">
      <a-col :span="6">
        <a-card class="topology-list-card" title="拓扑列表">
          <template #extra>
            <a-space>
              <a-button type="text" size="mini" @click="handleRefreshList" :loading="listLoading">
                <icon-refresh />
              </a-button>
              <a-button type="primary" size="mini" @click="openCreateModal">
                <template #icon>
                  <icon-plus />
                </template>
                新建拓扑
              </a-button>
            </a-space>
          </template>
          <a-empty v-if="!listLoading && !topologyList.length" description="暂无拓扑，点击右上角创建" />
          <a-spin :loading="listLoading">
            <div class="topology-list">
              <a-list :bordered="false" size="small">
                <a-list-item
                  v-for="item in topologyList"
                  :key="item.id"
                  :class="['topology-list__item', { active: currentTopology && currentTopology.id === item.id }]"
                  @click="handleSelectTopology(item)"
                >
                  <div class="item-main">
                    <div class="title">{{ item.name }}</div>
                    <div class="meta">
                      <span>{{ formatTime(item.updated_at) }}</span>
                      <a-tag size="small" :color="item.is_active ? 'green' : 'gray'">
                        {{ item.is_active ? '启用' : '禁用' }}
                      </a-tag>
                    </div>
                  </div>
                  <a-popconfirm content="确定删除该拓扑？" @ok="() => handleDeleteTopology(item)">
                    <a-button type="text" size="mini">
                      <icon-delete />
                    </a-button>
                  </a-popconfirm>
                </a-list-item>
              </a-list>
            </div>
          </a-spin>
        </a-card>

        <a-card
          v-if="currentTopology"
          class="topology-info-card"
          title="拓扑信息"
          :loading="saving || detailLoading"
        >
          <a-form :model="topologyForm" layout="vertical">
            <a-form-item field="name" label="名称" required>
              <a-input v-model="topologyForm.name" placeholder="输入拓扑名称" />
            </a-form-item>
            <a-form-item field="description" label="描述">
              <a-textarea v-model="topologyForm.description" placeholder="简要描述网络用途" :auto-size="{ minRows: 2, maxRows: 4 }" />
            </a-form-item>
            <a-form-item field="is_active" label="状态">
              <a-switch v-model="topologyForm.is_active" checked-text="启用" unchecked-text="禁用" />
            </a-form-item>
          </a-form>
          <a-space>
            <a-button type="primary" :loading="saving" @click="handleSaveTopology">
              <template #icon>
                <icon-save />
              </template>
              保存拓扑
            </a-button>
            <a-button :loading="saving" @click="handleResetCanvas">
              <icon-refresh />
              清空画布
            </a-button>
          </a-space>
        </a-card>

        <a-card class="palette-card" title="元素面板">
          <a-space wrap>
            <a-button
              v-for="item in palette"
              :key="item.type"
              size="small"
              :type="item.type === 'link' ? 'outline' : 'secondary'"
              @click="() => addNode(item)"
            >
              <span class="palette-dot" :style="{ background: item.color }" />
              {{ item.label }}
            </a-button>
          </a-space>
          <div class="palette-hint">点击按钮即可向画布添加对应节点，拖拽连线即可定义网络关系。</div>
        </a-card>
      </a-col>

      <a-col :span="18">
        <a-card class="canvas-card" :title="currentTopology ? currentTopology.name : '拓扑画布'">
          <template #extra>
            <a-space>
              <span v-if="currentTopology" class="stats">
                节点：{{ graphStats.nodes }} / 连线：{{ graphStats.edges }}
              </span>
              <a-button size="small" @click="handleFitView">
                <icon-fullscreen />
                自适应
              </a-button>
              <a-button size="small" @click="handleSnapshot">
                <icon-download />
                导出图片
              </a-button>
            </a-space>
          </template>
          <div ref="canvasRef" class="logicflow-canvas" />
          <div v-if="!currentTopology" class="canvas-placeholder">
            <div class="placeholder-text">请选择左侧拓扑或创建一个新的拓扑开始绘制</div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <a-modal
      v-model:visible="createModalVisible"
      title="新建拓扑"
      :mask-closable="false"
      @ok="handleCreateTopology"
      :ok-loading="createSubmitting"
    >
      <a-form :model="createForm" layout="vertical">
        <a-form-item field="name" label="名称" required>
          <a-input v-model="createForm.name" placeholder="例如：生产集群网络拓扑" />
        </a-form-item>
        <a-form-item field="description" label="描述">
          <a-textarea v-model="createForm.description" placeholder="补充拓扑用途、包含资源等信息" />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-drawer
      v-model:visible="nodeDrawerVisible"
      title="编辑节点"
      width="360px"
      unmount-on-close
    >
      <a-form :model="nodeForm" layout="vertical">
        <a-form-item field="title" label="名称" required>
          <a-input v-model="nodeForm.title" placeholder="节点名称，如：Node01 或 VM-001" />
        </a-form-item>
        <a-form-item field="interface" label="网口/接口名称">
          <a-input v-model="nodeForm.interface" placeholder="例如：eth0、vmbr0、tap100i0" />
        </a-form-item>
        <a-form-item field="network" label="网段或 VLAN">
          <a-input v-model="nodeForm.network" placeholder="例如：192.168.10.0/24 或 VLAN 20" />
        </a-form-item>
        <a-form-item field="description" label="备注">
          <a-textarea
            v-model="nodeForm.description"
            placeholder="可记录用途、网口带宽等补充信息"
            :auto-size="{ minRows: 2, maxRows: 4 }"
          />
        </a-form-item>
      </a-form>
      <template #footer>
        <a-space>
          <a-button @click="nodeDrawerVisible = false">取消</a-button>
          <a-button type="primary" @click="handleSaveNode">保存</a-button>
        </a-space>
      </template>
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { Message } from '@arco-design/web-vue'
import {
  IconPlus,
  IconRefresh,
  IconDelete,
  IconSave,
  IconFullscreen,
  IconDownload
} from '@arco-design/web-vue/es/icon'
import LogicFlow from '@logicflow/core'
import { MiniMap, Snapshot, SelectionSelect } from '@logicflow/extension'
import '@logicflow/core/es/index.css'
import '@logicflow/extension/es/index.css'
import {
  getNetworkTopologies,
  getNetworkTopology,
  createNetworkTopology,
  updateNetworkTopology,
  deleteNetworkTopology
} from '@/api/pve'

const canvasRef = ref(null)
const logicflow = ref(null)
const currentTopology = ref(null)
const topologyList = ref([])
const listLoading = ref(false)
const saving = ref(false)
const createModalVisible = ref(false)
const createSubmitting = ref(false)
const graphStats = reactive({ nodes: 0, edges: 0 })
const detailLoading = ref(false)
const nodeDrawerVisible = ref(false)
const nodeForm = reactive({
  id: '',
  title: '',
  interface: '',
  network: '',
  description: '',
  borderColor: '#165dff'
})

const topologyForm = reactive({
  name: '',
  description: '',
  is_active: true
})

const createForm = reactive({
  name: '',
  description: ''
})

const palette = [
  { type: 'pve-node', label: 'PVE 节点', color: '#165dff' },
  { type: 'vm-node', label: '虚拟机', color: '#00b42a' },
  { type: 'network-node', label: '网络设备', color: '#ff7d00' },
  { type: 'storage-node', label: '存储', color: '#722ed1' }
]

const defaultGraphData = { nodes: [], edges: [] }

const formatNodeText = (title, interfaceName, network) => {
  const lines = []
  if (title) lines.push(title)
  if (interfaceName) lines.push(`[${interfaceName}]`)
  if (network) lines.push(network)
  return lines.join('\n') || '未命名节点'
}

const applyNodeVisual = (nodeId, color = '#165dff') => {
  const lf = logicflow.value
  if (!lf) return
  const nodeModel = lf.graphModel?.getNodeModelById(nodeId)
  if (nodeModel) {
    nodeModel.updateStyles({
      stroke: color || '#165dff',
      fill: '#fff',
      borderRadius: 6
    })
  }
}

const openNodeDrawer = (data) => {
  const props = data.properties || {}
  nodeForm.id = data.id
  nodeForm.title = props.title || data.text?.value?.split('\n')[0] || ''
  nodeForm.interface = props.interface || ''
  nodeForm.network = props.network || ''
  nodeForm.description = props.description || ''
  nodeForm.borderColor = props.borderColor || props.stroke || '#165dff'
  nodeDrawerVisible.value = true
}

const initLogicFlow = () => {
  if (!canvasRef.value) return
  logicflow.value = new LogicFlow({
    container: canvasRef.value,
    grid: true,
    plugins: [MiniMap, Snapshot, SelectionSelect],
    background: {
      color: '#fafafa'
    }
  })
  logicflow.value.setDefaultEdgeType('polyline')
  logicflow.value.render(defaultGraphData)
  logicflow.value.on('node:add', () => updateGraphStats())
  logicflow.value.on('edge:add', () => updateGraphStats())
  logicflow.value.on('edge:delete', () => updateGraphStats())
  logicflow.value.on('node:delete', ({ data }) => {
    if (data?.id === nodeForm.id) {
      nodeDrawerVisible.value = false
    }
    updateGraphStats()
  })
  logicflow.value.on('node:click', ({ data }) => {
    if (data) {
      openNodeDrawer(data)
    }
  })
}

const applyTopologyDetail = (detail) => {
  if (!detail) return
  currentTopology.value = detail
  Object.assign(topologyForm, {
    name: detail.name || '',
    description: detail.description || '',
    is_active: detail.is_active ?? true
  })
  renderGraph(detail.diagram_data || defaultGraphData)
}

const handleSelectTopology = async (item) => {
  if (!item?.id) return
  detailLoading.value = true
  try {
    const detail = await getNetworkTopology(item.id)
    applyTopologyDetail(detail)
  } catch (error) {
    Message.error('加载拓扑详情失败：' + (error.message || '未知错误'))
  } finally {
    detailLoading.value = false
  }
}

const loadTopologyList = async () => {
  listLoading.value = true
  try {
    const res = await getNetworkTopologies({ page_size: 100 })
    const list = Array.isArray(res) ? res : res?.results || []
    topologyList.value = list
    if (!list.length) {
      currentTopology.value = null
      handleResetCanvas()
      return
    }
    if (!currentTopology.value) {
      await handleSelectTopology(list[0])
      return
    }
    const refreshed = list.find(item => item.id === currentTopology.value.id)
    if (refreshed) {
      await handleSelectTopology(refreshed)
    } else {
      currentTopology.value = null
      handleResetCanvas()
      await handleSelectTopology(list[0])
    }
  } catch (error) {
    Message.error('获取拓扑列表失败：' + (error.message || '未知错误'))
  } finally {
    listLoading.value = false
  }
}

const renderGraph = (data) => {
  if (!logicflow.value) return
  const graphData = data && typeof data === 'object' ? data : defaultGraphData
  logicflow.value.render(graphData)
  updateGraphStats(graphData)
  nextTick(() => {
    (graphData?.nodes || []).forEach(node => {
      const props = node.properties || {}
      if (props.title || props.interface || props.network) {
        const text = formatNodeText(
          props.title || node.text,
          props.interface,
          props.network
        )
        logicflow.value.updateText(node.id, text)
      }
      applyNodeVisual(node.id, props.borderColor || '#165dff')
    })
  })
}

const addNode = (paletteItem) => {
  if (!logicflow.value) return
  const { width, height } = canvasRef.value.getBoundingClientRect()
  const x = width / 2 + (Math.random() * 80 - 40)
  const y = height / 2 + (Math.random() * 80 - 40)
  const node = logicflow.value.addNode({
    type: 'rect',
    x,
    y,
    text: paletteItem.label,
    width: 120,
    height: 40,
    properties: {
      title: paletteItem.label,
      category: paletteItem.type,
      borderColor: paletteItem.color,
      interface: '',
      network: '',
      description: ''
    },
    style: {
      stroke: paletteItem.color,
      fill: '#fff',
      borderRadius: 6
    }
  })
  if (node?.id) {
    const text = formatNodeText(paletteItem.label, '', '')
    logicflow.value.updateText(node.id, text)
    applyNodeVisual(node.id, paletteItem.color)
  }
}

const handleRefreshList = () => {
  loadTopologyList()
}

const openCreateModal = () => {
  createForm.name = ''
  createForm.description = ''
  createModalVisible.value = true
}

const handleCreateTopology = async () => {
  if (!createForm.name.trim()) {
    Message.warning('请输入拓扑名称')
    return
  }
  createSubmitting.value = true
  try {
    const payload = {
      name: createForm.name.trim(),
      description: createForm.description || '',
      is_active: true,
      diagram_data: defaultGraphData,
      metadata: {}
    }
    const res = await createNetworkTopology(payload)
    Message.success('拓扑创建成功')
    createModalVisible.value = false
    await loadTopologyList()
    if (res?.id) {
      const item = topologyList.value.find(entry => entry.id === res.id)
      if (item) {
        handleSelectTopology(item)
      }
    }
  } catch (error) {
    Message.error('创建拓扑失败：' + (error.message || '未知错误'))
  } finally {
    createSubmitting.value = false
  }
}

const handleSaveTopology = async () => {
  if (!currentTopology.value) {
    Message.warning('请先选择拓扑')
    return
  }
  if (!topologyForm.name.trim()) {
    Message.warning('拓扑名称不能为空')
    return
  }
  saving.value = true
  try {
    const graphData = logicflow.value ? logicflow.value.getGraphData() : defaultGraphData
    const payload = {
      name: topologyForm.name.trim(),
      description: topologyForm.description || '',
      is_active: topologyForm.is_active,
      diagram_data: graphData,
      metadata: {
        ...(currentTopology.value.metadata || {}),
        stats: {
          nodes: graphData?.nodes?.length || 0,
          edges: graphData?.edges?.length || 0,
          updated_at: new Date().toISOString()
        }
      }
    }
    const res = await updateNetworkTopology(currentTopology.value.id, payload)
    Message.success('拓扑保存成功')
    currentTopology.value = res
    updateGraphStats(graphData)
    await loadTopologyList()
  } catch (error) {
    Message.error('保存失败：' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

const handleDeleteTopology = async (item) => {
  if (!item?.id) return
  try {
    await deleteNetworkTopology(item.id)
    Message.success('已删除拓扑')
    if (currentTopology.value && currentTopology.value.id === item.id) {
      currentTopology.value = null
      handleResetCanvas()
    }
    await loadTopologyList()
  } catch (error) {
    Message.error('删除失败：' + (error.message || '未知错误'))
  }
}

const handleResetCanvas = () => {
  if (!logicflow.value) return
  logicflow.value.clearData()
  logicflow.value.render(defaultGraphData)
  updateGraphStats(defaultGraphData)
}

const handleFitView = () => {
  if (!logicflow.value) return
  logicflow.value.view.fitView()
}

const handleSnapshot = async () => {
  if (!logicflow.value) return
  try {
    const snapshot = await logicflow.value.getSnapshot()
    const link = document.createElement('a')
    link.href = snapshot
    link.download = `${topologyForm.name || 'topology'}.png`
    link.click()
  } catch (error) {
    Message.error('导出图片失败')
  }
}

const updateGraphStats = (graphData) => {
  const data = graphData || (logicflow.value ? logicflow.value.getGraphData() : defaultGraphData)
  graphStats.nodes = Array.isArray(data?.nodes) ? data.nodes.length : 0
  graphStats.edges = Array.isArray(data?.edges) ? data.edges.length : 0
}

const handleSaveNode = () => {
  if (!logicflow.value || !nodeForm.id) {
    Message.warning('请先选择节点')
    return
  }
  const lf = logicflow.value
  const nodeModel = lf.graphModel?.getNodeModelById(nodeForm.id)
  const category = nodeModel?.properties?.category || 'custom'
  const text = formatNodeText(nodeForm.title, nodeForm.interface, nodeForm.network)
  lf.updateText(nodeForm.id, text)
  lf.setProperties(nodeForm.id, {
    title: nodeForm.title,
    interface: nodeForm.interface,
    network: nodeForm.network,
    description: nodeForm.description,
    borderColor: nodeForm.borderColor,
    category
  })
  applyNodeVisual(nodeForm.id, nodeForm.borderColor)
  nodeDrawerVisible.value = false
  Message.success('节点信息已更新')
}

const formatTime = (value) => {
  if (!value) return '-'
  try {
    const date = new Date(value)
    return date.toLocaleString()
  } catch (e) {
    return value
  }
}

onMounted(async () => {
  await nextTick()
  initLogicFlow()
  loadTopologyList()
})

onBeforeUnmount(() => {
  if (logicflow.value) {
    logicflow.value.destroy()
  }
})
</script>

<style scoped>
.pve-topology-page {
  padding: 16px;
}

.topology-list-card,
.topology-info-card,
.palette-card,
.canvas-card {
  margin-bottom: 16px;
}

.topology-list {
  max-height: 320px;
  overflow: auto;
}

.topology-list__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
}

.topology-list__item.active {
  background: var(--color-primary-light-1, #f0f5ff);
}

.item-main .title {
  font-weight: 600;
}

.item-main .meta {
  font-size: 12px;
  color: var(--color-text-3);
  display: flex;
  gap: 8px;
  align-items: center;
}

.palette-card .palette-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
}

.palette-card .palette-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-text-3);
}

.logicflow-canvas {
  height: 600px;
  border: 1px dashed var(--color-border-2);
  border-radius: 8px;
  background: #fff;
}

.canvas-placeholder {
  position: absolute;
  inset: 64px 16px 16px 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.placeholder-text {
  font-size: 14px;
  color: var(--color-text-4);
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px dashed var(--color-border-2);
}

.stats {
  font-size: 12px;
  color: var(--color-text-2);
}
</style>

