<template>
  <div class="vm-hardware-tab">
    <a-card :bordered="false">
      <div class="hardware-toolbar">
        <div class="toolbar-info">
          共 {{ hardwareRows.length }} 个硬件设备
        </div>
        <a-dropdown trigger="click">
          <a-button type="primary" size="small">
            添加硬件
            <icon-down />
          </a-button>
          <template #content>
            <a-doption
              v-for="option in hardwareAddOptions"
              :key="option.type"
              @click="openAddHardwareDialog(option.type)"
            >
              {{ option.label }}
            </a-doption>
          </template>
        </a-dropdown>
      </div>
      <a-table
        :columns="hardwareColumns"
        :data="hardwareRows"
        :pagination="false"
        :scroll="{ y: 400 }"
        size="small"
        :bordered="false"
      >
        <template #value="{ record }">
          <div class="hardware-value">
            <div v-if="record.formattedValue" class="formatted-value">
              {{ record.formattedValue }}
            </div>
            <div class="raw-value" :title="record.value">
              {{ record.value }}
            </div>
          </div>
        </template>
        <template #actions="{ record }">
          <a-space>
            <a-button
              v-if="record.editable"
              type="text"
              size="small"
              @click="openEditDialog(record.editType || record.key, record.key)"
            >
              编辑
            </a-button>
            <a-popconfirm
              v-if="record.deletable !== false"
              content="确定要删除此硬件设备吗？此操作不可恢复。"
              type="warning"
              @ok="handleDeleteHardware(record.key, record.label)"
            >
              <a-button
                type="text"
                size="small"
                status="danger"
              >
                删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </a-card>

    <!-- 编辑硬件对话框 -->
    <a-modal
      v-model:visible="editState.visible"
      :title="editState.title"
      :footer="false"
      :width="520"
      unmount-on-close
    >
      <a-form
        ref="editFormRef"
        :model="editForm"
        :rules="editFormRules"
        label-align="left"
        label-col="{ span: 7 }"
        wrapper-col="{ span: 17 }"
        layout="horizontal"
      >
        <template v-if="editState.type === 'cpu'">
          <a-form-item field="sockets" label="CPU Sockets">
            <a-input-number v-model="editForm.sockets" :min="1" :max="8" />
          </a-form-item>
          <a-form-item field="cores" label="每Socket核心">
            <a-input-number v-model="editForm.cores" :min="1" :max="64" />
          </a-form-item>
          <a-form-item field="cpu" label="CPU类型">
            <a-select v-model="editForm.cpu" allow-search>
              <a-option v-for="option in cpuOptions" :key="option" :value="option">
                {{ option }}
              </a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="numa" label="NUMA">
            <a-switch v-model="editForm.numa" />
          </a-form-item>
        </template>
        <template v-else-if="editState.type === 'memory'">
          <a-form-item field="memory" label="内存(MB)">
            <a-input-number v-model="editForm.memory" :min="256" :step="256" />
          </a-form-item>
        </template>
        <template v-else-if="editState.type === 'disk'">
          <a-form-item field="storage" label="存储">
            <a-select
              v-model="editForm.storage"
              :loading="storagesLoading"
              placeholder="请选择存储"
            >
              <a-option
                v-for="storage in storages"
                :key="storage.storage"
                :value="storage.storage"
              >
                {{ storage.storage }} ({{ storage.type }})
              </a-option>
            </a-select>
          </a-form-item>
          <a-form-item 
            field="volume" 
            :label="editForm.hasVolume ? '卷名' : '大小'"
          >
            <a-input 
              v-model="editForm.volume" 
              :placeholder="editForm.hasVolume ? '卷名（如：vm-130-disk-0）' : '大小（如：10G、32G）'"
              :disabled="editForm.hasVolume"
            />
            <template #extra>
              <span style="color: var(--color-text-3); font-size: 12px;">
                <span v-if="editForm.hasVolume">已有磁盘的卷名，不可修改</span>
                <span v-else>新磁盘的大小，格式：数字+G（如：10G、32G）</span>
              </span>
            </template>
          </a-form-item>
          <a-form-item field="iothread" label="启用IO Thread">
            <a-switch v-model="editForm.iothread" />
          </a-form-item>
          <a-form-item field="size" label="调整大小 (可选)" v-if="editForm.hasVolume">
            <a-input 
              v-model="editForm.size" 
              placeholder="如：10G、20G（仅调整大小时填写）"
            />
            <template #extra>
              <span style="color: var(--color-text-3); font-size: 12px;">
                仅当需要调整磁盘大小时填写，格式：数字+G
              </span>
            </template>
          </a-form-item>
        </template>
        <template v-else-if="editState.type === 'network'">
          <a-form-item field="model" label="网卡模型">
            <a-select v-model="editForm.model">
              <a-option value="virtio">virtio</a-option>
              <a-option value="e1000">e1000</a-option>
              <a-option value="vmxnet3">vmxnet3</a-option>
              <a-option value="rtl8139">rtl8139</a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="bridge" label="桥接">
            <a-select
              v-model="editForm.bridge"
              :loading="networksLoading"
              allow-search
            >
              <a-option
                v-for="bridge in bridgeOptions"
                :key="bridge"
                :value="bridge"
              >
                {{ bridge }}
              </a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="macaddr" label="MAC地址 (可选)">
            <a-input v-model="editForm.macaddr" placeholder="示例：DE:AD:BE:EF:12:34" />
          </a-form-item>
          <a-form-item field="firewall" label="启用防火墙">
            <a-switch v-model="editForm.firewall" />
          </a-form-item>
        </template>
        <template v-else-if="editState.type === 'efi'">
          <a-form-item field="efiValue" label="EFI 磁盘">
            <a-input v-model="editForm.efiValue" placeholder="示例：local-lvm:1,efitype=4m,pre-enrolled-keys=1" />
            <template #extra>
              直接使用PVE格式，如：local-lvm:1,efitype=4m,pre-enrolled-keys=1
            </template>
          </a-form-item>
        </template>
        <template v-else-if="editState.type === 'tpm'">
          <a-form-item field="tpmValue" label="TPM 设备">
            <a-input v-model="editForm.tpmValue" placeholder="示例：local-lvm:4,version=v2.0,model=tpm-crb" />
            <template #extra>
              直接使用PVE格式，如：local-lvm:4,version=v2.0,model=tpm-crb
            </template>
          </a-form-item>
        </template>
        <template v-else-if="editState.type === 'usb'">
          <a-form-item field="usbValue" label="USB 设备">
            <a-input v-model="editForm.usbValue" placeholder="示例：1234:abcd,usb3=1" />
            <template #extra>
              直接使用PVE格式，如：1234:abcd,usb3=1
            </template>
          </a-form-item>
        </template>
        <template v-else-if="editState.type === 'pci'">
          <a-form-item field="pciValue" label="PCI 设备">
            <a-input v-model="editForm.pciValue" placeholder="示例：0000:00:14.0,pcie=1" />
            <template #extra>
              直接使用PVE格式，如：0000:00:14.0,pcie=1
            </template>
          </a-form-item>
        </template>
        <template v-else-if="editState.type === 'serial'">
          <a-form-item field="serialValue" label="串口">
            <a-input v-model="editForm.serialValue" placeholder="示例：socket 或 socket,path=/var/run/qemu-server/serial0" />
            <template #extra>
              直接使用PVE格式，如：socket 或 socket,path=/var/run/qemu-server/serial0
            </template>
          </a-form-item>
        </template>
        <template v-else-if="editState.type === 'audio'">
          <a-form-item field="audioValue" label="音频设备">
            <a-input v-model="editForm.audioValue" placeholder="示例：device=ich9-intel-hda,driver=spice" />
            <template #extra>
              直接使用PVE格式，如：device=ich9-intel-hda,driver=spice
            </template>
          </a-form-item>
        </template>
        <template v-else-if="editState.type === 'rng'">
          <a-form-item field="rngValue" label="随机数设备">
            <a-input v-model="editForm.rngValue" placeholder="示例：source=/dev/urandom" />
            <template #extra>
              直接使用PVE格式，如：source=/dev/urandom
            </template>
          </a-form-item>
        </template>
        <template v-else-if="editState.type === 'virtiofs'">
          <a-form-item field="virtiofsValue" label="Virtiofs">
            <a-input v-model="editForm.virtiofsValue" placeholder="示例：mount_tag=share,path=/mnt/share" />
            <template #extra>
              直接使用PVE格式，如：mount_tag=share,path=/mnt/share
            </template>
          </a-form-item>
        </template>
      </a-form>

      <div class="edit-footer">
        <a-button @click="handleEditCancel" style="margin-right: 12px;">取消</a-button>
        <a-button type="primary" :loading="editState.submitting" @click="handleEditSubmit">
          保存
        </a-button>
      </div>
    </a-modal>

    <!-- 添加硬件对话框 -->
    <a-modal
      v-model:visible="addState.visible"
      :title="addState.title"
      :footer="false"
      :width="560"
      unmount-on-close
    >
      <a-form
        ref="addFormRef"
        :model="addForm"
        :rules="addFormRules"
        layout="vertical"
      >
        <template v-if="addState.type === 'disk'">
          <a-form-item field="storage" label="存储">
            <a-select
              v-model="addForm.storage"
              :loading="storagesLoading"
              placeholder="请选择存储"
            >
              <a-option
                v-for="storage in storages"
                :key="storage.storage"
                :value="storage.storage"
              >
                {{ storage.storage }} ({{ storage.type }})
              </a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="size" label="容量(GB)">
            <a-input-number v-model="addForm.size" :min="1" />
          </a-form-item>
          <a-form-item field="iothread" label="启用IO Thread">
            <a-switch v-model="addForm.iothread" />
          </a-form-item>
        </template>
        <template v-else-if="addState.type === 'cdrom'">
          <a-form-item field="isoStorage" label="ISO存储">
            <a-select
              v-model="addForm.isoStorage"
              :loading="storagesLoading"
              @change="handleISOStorageChange"
            >
              <a-option
                v-for="storage in isoStorages"
                :key="storage.storage"
                :value="storage.storage"
              >
                {{ storage.storage }}
              </a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="iso" label="ISO镜像">
            <a-select
              v-model="addForm.iso"
              :loading="isoLoading"
            >
              <a-option
                v-for="iso in isoList"
                :key="iso.volid"
                :value="iso.volid"
              >
                {{ iso.volid }}
              </a-option>
            </a-select>
          </a-form-item>
        </template>
        <template v-else-if="addState.type === 'network'">
          <a-form-item field="model" label="网卡模型">
            <a-select v-model="addForm.model">
              <a-option value="virtio">virtio</a-option>
              <a-option value="e1000">e1000</a-option>
              <a-option value="vmxnet3">vmxnet3</a-option>
              <a-option value="rtl8139">rtl8139</a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="bridge" label="桥接">
            <a-select
              v-model="addForm.bridge"
              :loading="networksLoading"
              allow-search
            >
              <a-option
                v-for="bridge in bridgeOptions"
                :key="bridge"
                :value="bridge"
              >
                {{ bridge }}
              </a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="macaddr" label="MAC地址 (可选)">
            <a-input v-model="addForm.macaddr" placeholder="示例：DE:AD:BE:EF:12:34" />
          </a-form-item>
          <a-form-item field="firewall" label="启用防火墙">
            <a-switch v-model="addForm.firewall" />
          </a-form-item>
        </template>
        <template v-else-if="addState.type === 'efi'">
          <a-form-item field="storage" label="EFI存储">
            <a-select v-model="addForm.storage" :loading="storagesLoading">
              <a-option
                v-for="storage in storages"
                :key="storage.storage"
                :value="storage.storage"
              >
                {{ storage.storage }}
              </a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="efitype" label="EFI类型">
            <a-select v-model="addForm.efitype">
              <a-option value="4m">4M (默认)</a-option>
              <a-option value="2m">2M</a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="pre_enrolled" label="预置微软密钥">
            <a-switch v-model="addForm.pre_enrolled" />
          </a-form-item>
        </template>
        <template v-else-if="addState.type === 'tpm'">
          <a-form-item field="storage" label="TPM存储">
            <a-select v-model="addForm.storage" :loading="storagesLoading">
              <a-option
                v-for="storage in storages"
                :key="storage.storage"
                :value="storage.storage"
              >
                {{ storage.storage }}
              </a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="version" label="版本">
            <a-select v-model="addForm.version">
              <a-option value="v2.0">v2.0</a-option>
              <a-option value="v1.2">v1.2</a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="model" label="模型">
            <a-select v-model="addForm.model">
              <a-option value="tpm-crb">tpm-crb</a-option>
              <a-option value="tpm-tis">tpm-tis</a-option>
            </a-select>
          </a-form-item>
        </template>
        <template v-else-if="addState.type === 'usb'">
          <a-form-item field="host" label="主机设备 (Vendor:Product)">
            <a-input v-model="addForm.host" placeholder="示例：1234:abcd" />
          </a-form-item>
          <a-form-item field="usb3" label="USB3">
            <a-switch v-model="addForm.usb3" />
          </a-form-item>
        </template>
        <template v-else-if="addState.type === 'pci'">
          <a-form-item field="host" label="PCI设备 (Domain:Bus:Slot.Func)">
            <a-input v-model="addForm.host" placeholder="示例：0000:00:14.0" />
          </a-form-item>
          <a-form-item field="pcie" label="启用PCIE">
            <a-switch v-model="addForm.pcie" />
          </a-form-item>
        </template>
        <template v-else-if="addState.type === 'serial'">
          <a-form-item field="mode" label="模式">
            <a-select v-model="addForm.mode">
              <a-option value="socket">socket</a-option>
              <a-option value="server">server</a-option>
              <a-option value="telnet">telnet</a-option>
              <a-option value="pipe">pipe</a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="path" label="路径/端口 (可选)">
            <a-input v-model="addForm.path" placeholder="示例：/var/run/qemu-server/serial0" />
          </a-form-item>
        </template>
        <template v-else-if="addState.type === 'cloudinit'">
          <a-alert type="warning" style="margin-bottom: 12px;">
            CloudInit 会自动创建配置盘，如已有 ide2 设备请先移除。
          </a-alert>
          <a-form-item field="storage" label="存储">
            <a-select v-model="addForm.storage" :loading="storagesLoading">
              <a-option
                v-for="storage in storages"
                :key="storage.storage"
                :value="storage.storage"
              >
                {{ storage.storage }}
              </a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="ciuser" label="默认用户">
            <a-input v-model="addForm.ciuser" />
          </a-form-item>
          <a-form-item field="cipassword" label="密码">
            <a-input-password v-model="addForm.cipassword" />
          </a-form-item>
          <a-form-item field="ipconfig0" label="IP配置 (可选)">
            <a-input v-model="addForm.ipconfig0" placeholder="示例：ip=dhcp 或 ip=192.168.1.10/24,gw=192.168.1.1" />
          </a-form-item>
        </template>
        <template v-else-if="addState.type === 'audio'">
          <a-form-item field="device" label="音频设备">
            <a-select v-model="addForm.device">
              <a-option value="ich9-intel-hda">ich9-intel-hda</a-option>
              <a-option value="intel-hda">intel-hda</a-option>
              <a-option value="ac97">ac97</a-option>
            </a-select>
          </a-form-item>
          <a-form-item field="driver" label="驱动">
            <a-select v-model="addForm.driver">
              <a-option value="spice">spice</a-option>
              <a-option value="none">none</a-option>
            </a-select>
          </a-form-item>
        </template>
        <template v-else-if="addState.type === 'rng'">
          <a-form-item field="source" label="随机源">
            <a-input v-model="addForm.source" placeholder="/dev/urandom" />
          </a-form-item>
        </template>
        <template v-else-if="addState.type === 'virtiofs'">
          <a-form-item field="tag" label="Mount Tag">
            <a-input v-model="addForm.tag" />
          </a-form-item>
          <a-form-item field="path" label="主机路径">
            <a-input v-model="addForm.path" />
          </a-form-item>
        </template>
      </a-form>
      <div class="edit-footer">
        <a-button @click="handleAddCancel" style="margin-right: 12px;">取消</a-button>
        <a-button type="primary" :loading="addState.submitting" @click="handleAddSubmit">
          添加
        </a-button>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { IconDown } from '@arco-design/web-vue/es/icon'
import {
  updateVirtualMachineHardware,
  getNodeStorage,
  getNodeNetwork,
  getStorageISO
} from '@/api/pve'

const props = defineProps({
  vm: {
    type: Object,
    required: true
  },
  vmId: {
    type: [Number, String],
    required: true
  }
})

const emit = defineEmits(['refresh'])

const editFormRef = ref(null)
const addFormRef = ref(null)

const editState = reactive({
  visible: false,
  type: '',
  title: '',
  submitting: false,
  targetKey: ''
})

const editForm = reactive({})

const addState = reactive({
  visible: false,
  type: '',
  title: '',
  submitting: false
})

const addForm = reactive({})

const storages = ref([])
const storagesLoading = ref(false)
const networks = ref([])
const networksLoading = ref(false)
const isoStorages = ref([])
const isoList = ref([])
const isoLoading = ref(false)

const hardwareAddOptions = [
  { type: 'disk', label: '硬盘' },
  { type: 'cdrom', label: 'CD/DVD 驱动器' },
  { type: 'network', label: '网络设备' },
  { type: 'efi', label: 'EFI 磁盘' },
  { type: 'tpm', label: 'TPM 状态' },
  { type: 'usb', label: 'USB 设备' },
  { type: 'pci', label: 'PCI 设备' },
  { type: 'serial', label: '串行端口' },
  { type: 'cloudinit', label: 'CloudInit 设备' },
  { type: 'audio', label: '音频设备' },
  { type: 'rng', label: 'VirtIO RNG' },
  { type: 'virtiofs', label: 'Virtiofs' }
]

const hardwareColumns = [
  { 
    title: '硬件类型', 
    dataIndex: 'label', 
    width: 180,
    fixed: 'left'
  },
  { 
    title: '配置信息', 
    dataIndex: 'value', 
    slotName: 'value',
    ellipsis: true,
    tooltip: true
  },
  { 
    title: '操作', 
    dataIndex: 'actions', 
    slotName: 'actions', 
    width: 120,
    fixed: 'right'
  }
]

// 解析磁盘配置
const parseDiskConfig = (value) => {
  if (!value) return null
  const parts = value.split(',')
  const storagePart = parts[0] || ''
  const [storage, volumeOrSize] = storagePart.split(':')
  
  // 先提取所有options
  const options = {}
  parts.slice(1).forEach(part => {
    const [key, val] = part.split('=')
    if (key) {
      if (val === undefined || val === '') {
        options[key] = true
      } else {
        options[key] = val
      }
    }
  })
  
  // 判断是已有磁盘（卷名）还是新磁盘（大小）
  const hasVolume = volumeOrSize && !/^\d+\.?\d*[GM]?$/i.test(volumeOrSize)
  
  let size = ''
  let volume = ''
  if (hasVolume) {
    // 已有磁盘，volumeOrSize是卷名
    volume = volumeOrSize
    // 从options中提取size（如果存在）
    if (options.size) {
      size = options.size
    }
  } else {
    // 新磁盘，volumeOrSize是大小
    size = volumeOrSize || ''
    if (size) {
      // 格式化显示大小
      let sizeNum = parseFloat(size)
      if (isNaN(sizeNum)) {
        const match = size.match(/(\d+\.?\d*)/)
        if (match) {
          sizeNum = parseFloat(match[1])
          const unit = size.replace(match[1], '').toUpperCase()
          if (unit.includes('T')) {
            sizeNum = sizeNum * 1024
          } else if (unit.includes('M')) {
            sizeNum = sizeNum / 1024
          }
        }
      }
      if (sizeNum >= 1024) {
        size = `${(sizeNum / 1024).toFixed(2)} TB`
      } else if (sizeNum > 0) {
        size = `${sizeNum.toFixed(0)} GB`
      }
    }
  }
  
  return { storage, volume, size, hasVolume, options, raw: value }
}

// 解析网络配置
const parseNetworkConfig = (value) => {
  if (!value) return null
  const parts = value.split(',')
  const model = parts[0] || ''
  const options = {}
  parts.slice(1).forEach(part => {
    const [key, val] = part.split('=')
    if (key) options[key] = val || true
  })
  return { model, bridge: options.bridge || '-', macaddr: options.macaddr || '-', firewall: options.firewall === '1' || options.firewall === 1, raw: value }
}

// 解析其他设备配置
const parseDeviceConfig = (value, type) => {
  if (!value) return null
  if (type === 'efi') {
    const parts = value.split(',')
    const storagePart = parts[0] || ''
    const [storage] = storagePart.split(':')
    const options = {}
    parts.slice(1).forEach(part => {
      const [key, val] = part.split('=')
      if (key) options[key] = val || true
    })
    return { storage, efitype: options.efitype || '4m', raw: value }
  }
  return { raw: value }
}

const hardwareRows = computed(() => {
  const vm = props.vm
  if (!vm) {
    return []
  }
  const config = vm.pve_config || {}
  const rows = []
  const sockets = Number(config.sockets || 1)
  const coresPerSocket = Number(config.cores || (vm.cpu_cores ? Math.max(1, Math.floor(vm.cpu_cores / (sockets || 1))) : 1))
  const cpuType = config.cpu || '默认'
  const totalCores = sockets * coresPerSocket
  rows.push({
    key: 'cpu',
    label: '处理器',
    value: `sockets=${sockets},cores=${coresPerSocket},cpu=${cpuType}${config.numa ? ',numa=1' : ''}`,
    formattedValue: `${sockets} Socket × ${coresPerSocket} Core = ${totalCores} 核心 (CPU: ${cpuType})${config.numa ? ', NUMA已启用' : ''}`,
    editable: true,
    deletable: false
  })
  
  const memoryMB = config.memory || vm.memory_mb || 0
  const memoryGB = (memoryMB / 1024).toFixed(2)
  rows.push({
    key: 'memory',
    label: '内存',
    value: `memory=${memoryMB}`,
    formattedValue: `${memoryMB} MB (${memoryGB} GB)`,
    editable: true,
    deletable: false
  })

  Object.keys(config).forEach((key) => {
    if (/^scsi\d+$/.test(key)) {
      const diskInfo = parseDiskConfig(config[key])
      let formattedValue = config[key]
      if (diskInfo) {
        if (diskInfo.hasVolume) {
          formattedValue = `存储: ${diskInfo.storage}, 卷名: ${diskInfo.volume}`
          if (diskInfo.size) {
            formattedValue += `, 大小: ${diskInfo.size}`
          }
        } else {
          formattedValue = `存储: ${diskInfo.storage}, 大小: ${diskInfo.size || '未知'}`
        }
        if (diskInfo.options.iothread) {
          formattedValue += ', IO Thread: 启用'
        }
      }
      rows.push({
        key,
        label: `磁盘 (${key})`,
        value: config[key],
        formattedValue,
        editable: true,
        editType: 'disk',
        deletable: true
      })
    } else if (/^ide\d+$/.test(key)) {
      const isCDROM = String(config[key]).includes('media=cdrom')
      if (isCDROM) {
        const isoMatch = config[key].match(/([^:]+):(.+),media=cdrom/)
        rows.push({
          key,
          label: `CD/DVD (${key})`,
          value: config[key],
          formattedValue: isoMatch ? `ISO: ${isoMatch[2]}` : config[key],
          editable: true,
          editType: 'disk',
          deletable: true
        })
      } else {
        const diskInfo = parseDiskConfig(config[key])
        let formattedValue = config[key]
        if (diskInfo) {
          if (diskInfo.hasVolume) {
            formattedValue = `存储: ${diskInfo.storage}, 卷名: ${diskInfo.volume}`
            if (diskInfo.size) {
              formattedValue += `, 大小: ${diskInfo.size}`
            }
          } else {
            formattedValue = `存储: ${diskInfo.storage}, 大小: ${diskInfo.size || '未知'}`
          }
          if (diskInfo.options.iothread) {
            formattedValue += ', IO Thread: 启用'
          }
        }
        rows.push({
          key,
          label: `磁盘 (${key})`,
          value: config[key],
          formattedValue,
          editable: true,
          editType: 'disk',
          deletable: true
        })
      }
    } else if (/^virtio\d+$/.test(key)) {
      const diskInfo = parseDiskConfig(config[key])
      let formattedValue = config[key]
      if (diskInfo) {
        if (diskInfo.hasVolume) {
          formattedValue = `存储: ${diskInfo.storage}, 卷名: ${diskInfo.volume}`
          if (diskInfo.size) {
            formattedValue += `, 大小: ${diskInfo.size}`
          }
        } else {
          formattedValue = `存储: ${diskInfo.storage}, 大小: ${diskInfo.size || '未知'}`
        }
        if (diskInfo.options.iothread) {
          formattedValue += ', IO Thread: 启用'
        }
      }
      rows.push({
        key,
        label: `磁盘 (${key})`,
        value: config[key],
        formattedValue,
        editable: true,
        editType: 'disk',
        deletable: true
      })
    } else if (/^sata\d+$/.test(key)) {
      const diskInfo = parseDiskConfig(config[key])
      let formattedValue = config[key]
      if (diskInfo) {
        if (diskInfo.hasVolume) {
          formattedValue = `存储: ${diskInfo.storage}, 卷名: ${diskInfo.volume}`
          if (diskInfo.size) {
            formattedValue += `, 大小: ${diskInfo.size}`
          }
        } else {
          formattedValue = `存储: ${diskInfo.storage}, 大小: ${diskInfo.size || '未知'}`
        }
        if (diskInfo.options.iothread) {
          formattedValue += ', IO Thread: 启用'
        }
      }
      rows.push({
        key,
        label: `磁盘 (${key})`,
        value: config[key],
        formattedValue,
        editable: true,
        editType: 'disk',
        deletable: true
      })
    } else if (/^net\d+$/.test(key)) {
      const netInfo = parseNetworkConfig(config[key])
      rows.push({
        key,
        label: `网络 (${key})`,
        value: config[key],
        formattedValue: netInfo ? `模型: ${netInfo.model}, 桥接: ${netInfo.bridge}, MAC: ${netInfo.macaddr}, 防火墙: ${netInfo.firewall ? '启用' : '禁用'}` : config[key],
        editable: true,
        editType: 'network',
        deletable: true
      })
    }
  })

  if (config.efidisk0) {
    const efiInfo = parseDeviceConfig(config.efidisk0, 'efi')
    rows.push({ 
      key: 'efidisk0', 
      label: 'EFI 磁盘', 
      value: config.efidisk0,
      formattedValue: efiInfo ? `存储: ${efiInfo.storage}, 类型: ${efiInfo.efitype}` : config.efidisk0,
      editable: true, 
      editType: 'efi',
      deletable: true
    })
  }
  if (config.tpmstate0) {
    rows.push({ 
      key: 'tpmstate0', 
      label: 'TPM', 
      value: config.tpmstate0,
      formattedValue: config.tpmstate0,
      editable: true, 
      editType: 'tpm',
      deletable: true
    })
  }
  if (config.usb0) {
    rows.push({ 
      key: 'usb0', 
      label: 'USB 设备', 
      value: config.usb0,
      formattedValue: config.usb0,
      editable: true, 
      editType: 'usb',
      deletable: true
    })
  }
  if (config.hostpci0) {
    rows.push({ 
      key: 'hostpci0', 
      label: 'PCI 设备', 
      value: config.hostpci0,
      formattedValue: config.hostpci0,
      editable: true, 
      editType: 'pci',
      deletable: true
    })
  }
  if (config.serial0) {
    rows.push({ 
      key: 'serial0', 
      label: '串口', 
      value: config.serial0,
      formattedValue: config.serial0,
      editable: true, 
      editType: 'serial',
      deletable: true
    })
  }
  if (config.audio0) {
    rows.push({ 
      key: 'audio0', 
      label: '音频', 
      value: config.audio0,
      formattedValue: config.audio0,
      editable: true, 
      editType: 'audio',
      deletable: true
    })
  }
  if (config.rng0) {
    rows.push({ 
      key: 'rng0', 
      label: '随机数设备', 
      value: config.rng0,
      formattedValue: config.rng0,
      editable: true, 
      editType: 'rng',
      deletable: true
    })
  }
  if (config.virtiofs0) {
    rows.push({ 
      key: 'virtiofs0', 
      label: 'Virtiofs', 
      value: config.virtiofs0,
      formattedValue: config.virtiofs0,
      editable: true, 
      editType: 'virtiofs',
      deletable: true
    })
  }

  return rows
})

const cpuOptions = [
  'host',
  'x86-64-v2-AES',
  'x86-64-v3',
  'x86-64-v4',
  'kvm64',
  'qemu64'
]

const bridgeOptions = computed(() => {
  const bridges = networks.value
    .filter(item => item.type === 'bridge' && item.iface)
    .map(item => item.iface)
  const unique = Array.from(new Set(bridges))
  if (!unique.includes('vmbr0')) {
    unique.push('vmbr0')
  }
  return unique
})

const getConfig = () => props.vm?.pve_config || {}

const loadHardwareResources = async () => {
  const vm = props.vm
  if (!vm || !vm.server || !vm.node) {
    storages.value = []
    networks.value = []
    isoStorages.value = []
    return
  }
  await Promise.all([fetchStorages(vm), fetchNetworks(vm)])
  isoStorages.value = storages.value.filter(item => item.content?.includes('iso') || item.type === 'dir' || item.type === 'nfs')
}

const fetchStorages = async (vm) => {
  storagesLoading.value = true
  try {
    const res = await getNodeStorage(vm.server, vm.node)
    storages.value = Array.isArray(res) ? res : []
  } catch (error) {
    storages.value = []
    Message.error('获取存储列表失败：' + (error.message || '未知错误'))
  } finally {
    storagesLoading.value = false
  }
}

const fetchNetworks = async (vm) => {
  networksLoading.value = true
  try {
    const res = await getNodeNetwork(vm.server, vm.node)
    networks.value = Array.isArray(res) ? res : []
  } catch (error) {
    networks.value = []
    Message.error('获取网络接口失败：' + (error.message || '未知错误'))
  } finally {
    networksLoading.value = false
  }
}

const resetEditForm = () => {
  Object.keys(editForm).forEach((key) => {
    delete editForm[key]
  })
}

const openEditDialog = (type, targetKey = '') => {
  if (!props.vm) {
    return
  }
  editState.targetKey = targetKey || type || ''
  const config = getConfig()
  resetEditForm()
  editState.type = type
  editState.submitting = false
  switch (type) {
    case 'cpu':
      editState.title = '编辑处理器'
      Object.assign(editForm, {
        sockets: Number(config.sockets || 1),
        cores: Number(config.cores || (props.vm.cpu_cores || 1)),
        cpu: config.cpu || 'x86-64-v2-AES',
        numa: config.numa === 1 || config.numa === '1' || config.numa === true
      })
      break
    case 'memory':
      editState.title = '编辑内存'
      Object.assign(editForm, {
        memory: Number(config.memory || props.vm.memory_mb || 512)
      })
      break
    case 'disk': {
      editState.title = `编辑磁盘 (${editState.targetKey || 'scsi0'})`
      const diskValue = config[editState.targetKey || 'scsi0'] || ''
      const diskInfo = parseDiskConfig(diskValue)
      if (diskInfo) {
        Object.assign(editForm, {
          storage: diskInfo.storage || '',
          volume: diskInfo.hasVolume ? diskInfo.volume : (diskInfo.size || ''),
          hasVolume: diskInfo.hasVolume,
          iothread: diskInfo.options.iothread === 'on' || diskInfo.options.iothread === 1 || diskInfo.options.iothread === true || diskInfo.options.iothread === '1',
          size: diskInfo.hasVolume ? (diskInfo.options.size || '') : ''
        })
      } else {
        Object.assign(editForm, {
          storage: storages.value[0]?.storage || '',
          volume: '',
          hasVolume: false,
          iothread: false,
          size: ''
        })
      }
      break
    }
    case 'network': {
      editState.title = `编辑网络 (${editState.targetKey || 'net0'})`
      const netValue = config[editState.targetKey || 'net0'] || ''
      const netInfo = parseNetworkConfig(netValue)
      if (netInfo) {
        Object.assign(editForm, {
          model: netInfo.model || 'virtio',
          bridge: netInfo.bridge !== '-' ? netInfo.bridge : 'vmbr0',
          macaddr: netInfo.macaddr !== '-' ? netInfo.macaddr : '',
          firewall: netInfo.firewall
        })
      } else {
        Object.assign(editForm, {
          model: 'virtio',
          bridge: 'vmbr0',
          macaddr: '',
          firewall: true
        })
      }
      break
    }
    case 'efi':
      editState.title = '编辑 EFI 磁盘'
      Object.assign(editForm, {
        efiValue: config.efidisk0 || ''
      })
      break
    case 'tpm':
      editState.title = '编辑 TPM 设备'
      Object.assign(editForm, {
        tpmValue: config.tpmstate0 || ''
      })
      break
    case 'usb':
      editState.title = '编辑 USB 设备'
      Object.assign(editForm, {
        usbValue: config.usb0 || ''
      })
      break
    case 'pci':
      editState.title = '编辑 PCI 设备'
      Object.assign(editForm, {
        pciValue: config.hostpci0 || ''
      })
      break
    case 'serial':
      editState.title = '编辑串口'
      Object.assign(editForm, {
        serialValue: config.serial0 || ''
      })
      break
    case 'audio':
      editState.title = '编辑音频设备'
      Object.assign(editForm, {
        audioValue: config.audio0 || ''
      })
      break
    case 'rng':
      editState.title = '编辑随机数设备'
      Object.assign(editForm, {
        rngValue: config.rng0 || ''
      })
      break
    case 'virtiofs':
      editState.title = '编辑 Virtiofs'
      Object.assign(editForm, {
        virtiofsValue: config.virtiofs0 || ''
      })
      break
    default:
      editState.title = '编辑硬件'
      break
  }
  editState.visible = true
  nextTick(() => {
    editFormRef.value?.clearValidate()
  })
}

const editFormRules = computed(() => {
  switch (editState.type) {
    case 'cpu':
      return {
        sockets: [{ required: true, message: '请输入Sockets', type: 'number' }],
        cores: [{ required: true, message: '请输入核心数', type: 'number' }],
        cpu: [{ required: true, message: '请选择CPU类型' }]
      }
    case 'memory':
      return {
        memory: [{ required: true, message: '请输入内存大小', type: 'number' }]
      }
    case 'disk':
      return {
        storage: [{ required: true, message: '请选择存储' }],
        volume: [{ required: true, message: '请输入卷名或大小' }]
      }
    case 'network':
      return {
        bridge: [{ required: true, message: '请选择桥接' }],
        macaddr: [{
          validator: (value, callback) => {
            if (!value) return callback()
            if (macPattern.test(value)) return callback()
            return callback('MAC地址格式不正确')
          }
        }]
      }
    case 'efi':
      return {
        efiValue: [{ required: true, message: '请输入EFI配置' }]
      }
    case 'tpm':
      return {
        tpmValue: [{ required: true, message: '请输入TPM配置' }]
      }
    case 'usb':
      return {
        usbValue: [{ required: true, message: '请输入USB配置' }]
      }
    case 'pci':
      return {
        pciValue: [{ required: true, message: '请输入PCI配置' }]
      }
    case 'serial':
      return {
        serialValue: [{ required: true, message: '请输入串口配置' }]
      }
    case 'audio':
      return {
        audioValue: [{ required: true, message: '请输入音频配置' }]
      }
    case 'rng':
      return {
        rngValue: [{ required: true, message: '请输入随机数设备配置' }]
      }
    case 'virtiofs':
      return {
        virtiofsValue: [{ required: true, message: '请输入Virtiofs配置' }]
      }
    default:
      return {}
  }
})

const buildParams = () => {
  switch (editState.type) {
    case 'cpu':
      return {
        sockets: Number(editForm.sockets),
        cores: Number(editForm.cores),
        cpu: editForm.cpu,
        numa: editForm.numa ? 1 : 0
      }
    case 'memory':
      return {
        memory: Number(editForm.memory)
      }
    case 'disk': {
      if (!editForm.storage || !editForm.volume) {
        throw new Error('存储和卷名/大小不能为空')
      }
      
      // 构建磁盘配置值
      // 格式：storage:volume或storage:size
      let diskValue = `${editForm.storage}:${editForm.volume}`
      
      // 如果是已有磁盘且有调整大小参数，添加size参数
      if (editForm.hasVolume && editForm.size) {
        diskValue += `,size=${editForm.size}`
      }
      
      // 添加iothread参数
      if (editForm.iothread) {
        diskValue += ',iothread=on'
      }
      
      return editState.targetKey
        ? { [editState.targetKey]: diskValue }
        : { scsi0: diskValue }
    }
    case 'network': {
      const parts = [editForm.model || 'virtio']
      if (editForm.bridge) parts.push(`bridge=${editForm.bridge}`)
      if (editForm.macaddr) parts.push(`macaddr=${editForm.macaddr}`)
      parts.push(`firewall=${editForm.firewall ? 1 : 0}`)
      const networkValue = parts.join(',')
      return editState.targetKey
        ? { [editState.targetKey]: networkValue }
        : { net0: networkValue }
    }
    case 'efi':
      return { efidisk0: editForm.efiValue }
    case 'tpm':
      return { tpmstate0: editForm.tpmValue }
    case 'usb':
      return { usb0: editForm.usbValue }
    case 'pci':
      return { hostpci0: editForm.pciValue }
    case 'serial':
      return { serial0: editForm.serialValue }
    case 'audio':
      return { audio0: editForm.audioValue }
    case 'rng':
      return { rng0: editForm.rngValue }
    case 'virtiofs':
      return { virtiofs0: editForm.virtiofsValue }
    default:
      return {}
  }
}

const handleEditCancel = () => {
  editState.visible = false
}

const handleEditSubmit = async () => {
  if (!props.vmId) {
    Message.warning('缺少虚拟机ID，无法更新硬件配置')
    return
  }
  if (editFormRef.value) {
    try {
      await editFormRef.value.validate()
    } catch (error) {
      return
    }
  }
  const params = buildParams()
  if (!Object.keys(params).length) {
    Message.warning('暂无可更新的参数')
    return
  }
  editState.submitting = true
  try {
    await updateVirtualMachineHardware(props.vmId, { params })
    Message.success('硬件配置更新已提交')
    editState.visible = false
    emit('refresh')
  } catch (error) {
    Message.error('更新失败：' + (error.message || '未知错误'))
  } finally {
    editState.submitting = false
  }
}

const getNextDeviceKey = (prefix, startIndex = 0) => {
  const config = getConfig()
  let index = startIndex
  while (config.hasOwnProperty(`${prefix}${index}`)) {
    index += 1
  }
  return `${prefix}${index}`
}

const openAddHardwareDialog = (type) => {
  if (!props.vm) return
  addState.type = type
  addState.title = hardwareAddOptions.find(item => item.type === type)?.label || '添加硬件'
  addState.submitting = false
  Object.keys(addForm).forEach(key => delete addForm[key])
  switch (type) {
    case 'disk':
      addForm.storage = storages.value[0]?.storage || ''
      addForm.size = 10
      addForm.iothread = true
      break
    case 'cdrom':
      addForm.isoStorage = isoStorages.value[0]?.storage || ''
      addForm.iso = ''
      if (addForm.isoStorage) {
        handleISOStorageChange(addForm.isoStorage)
      }
      break
    case 'network':
      addForm.model = 'virtio'
      addForm.bridge = bridgeOptions.value[0] || 'vmbr0'
      addForm.macaddr = ''
      addForm.firewall = true
      break
    case 'efi':
      addForm.storage = storages.value[0]?.storage || ''
      addForm.efitype = '4m'
      addForm.pre_enrolled = true
      break
    case 'tpm':
      addForm.storage = storages.value[0]?.storage || ''
      addForm.version = 'v2.0'
      addForm.model = 'tpm-crb'
      break
    case 'usb':
      addForm.host = ''
      addForm.usb3 = true
      break
    case 'pci':
      addForm.host = ''
      addForm.pcie = true
      break
    case 'serial':
      addForm.mode = 'socket'
      addForm.path = ''
      break
    case 'cloudinit':
      addForm.storage = storages.value[0]?.storage || ''
      addForm.ciuser = 'root'
      addForm.cipassword = ''
      addForm.ipconfig0 = 'ip=dhcp'
      break
    case 'audio':
      addForm.device = 'ich9-intel-hda'
      addForm.driver = 'spice'
      break
    case 'rng':
      addForm.source = '/dev/urandom'
      break
    case 'virtiofs':
      addForm.tag = 'share'
      addForm.path = '/mnt/share'
      break
  }
  addState.visible = true
  nextTick(() => {
    addFormRef.value?.clearValidate()
  })
}

const macPattern = /^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$/

const addFormRules = computed(() => {
  switch (addState.type) {
    case 'disk':
      return {
        storage: [{ required: true, message: '请选择存储' }],
        size: [{ required: true, message: '请输入容量', type: 'number' }]
      }
    case 'cdrom':
      return {
        isoStorage: [{ required: true, message: '请选择ISO存储' }],
        iso: [{ required: true, message: '请选择ISO镜像' }]
      }
    case 'network':
      return {
        bridge: [{ required: true, message: '请选择桥接' }],
        macaddr: [{
          validator: (value, callback) => {
            if (!value) return callback()
            if (macPattern.test(value)) return callback()
            return callback('MAC地址格式不正确')
          }
        }]
      }
    case 'efi':
      return { storage: [{ required: true, message: '请选择存储' }] }
    case 'tpm':
      return { storage: [{ required: true, message: '请选择存储' }] }
    case 'usb':
      return { host: [{ required: true, message: '请输入设备ID (Vendor:Product)' }] }
    case 'pci':
      return { host: [{ required: true, message: '请输入PCI地址' }] }
    case 'cloudinit':
      return {
        storage: [{ required: true, message: '请选择存储' }],
        ciuser: [{ required: true, message: '请输入默认用户' }]
      }
    case 'virtiofs':
      return {
        tag: [{ required: true, message: '请输入Mount Tag' }],
        path: [{ required: true, message: '请输入路径' }]
      }
    default:
      return {}
  }
})

const handleISOStorageChange = async (storage) => {
  if (!storage || !props.vm) {
    isoList.value = []
    addForm.iso = ''
    return
  }
  isoLoading.value = true
  try {
    const res = await getStorageISO(props.vm.server, props.vm.node, storage)
    isoList.value = Array.isArray(res) ? res : []
    addForm.iso = isoList.value[0]?.volid || ''
  } catch (error) {
    isoList.value = []
    addForm.iso = ''
    Message.error('获取ISO列表失败：' + (error.message || '未知错误'))
  } finally {
    isoLoading.value = false
  }
}

const buildAddParams = () => {
  switch (addState.type) {
    case 'disk': {
      const storageInfo = storages.value.find(s => s.storage === addForm.storage)
      const storageType = storageInfo?.type || ''
      const size = Number(addForm.size)
      const base = ['rbd', 'lvm', 'lvmthin'].includes(storageType)
        ? `${addForm.storage}:${size}`
        : `${addForm.storage}:${size}G`
      const value = addForm.iothread ? `${base},iothread=on` : base
      const key = getNextDeviceKey('scsi')
      return { key, value }
    }
    case 'cdrom': {
      const key = getNextDeviceKey('ide', 2)
      const value = `${addForm.iso},media=cdrom`
      return { key, value }
    }
    case 'network': {
      const key = getNextDeviceKey('net')
      const parts = [addForm.model || 'virtio']
      if (addForm.bridge) parts.push(`bridge=${addForm.bridge}`)
      if (addForm.macaddr) parts.push(`macaddr=${addForm.macaddr}`)
      parts.push(`firewall=${addForm.firewall ? 1 : 0}`)
      return { key, value: parts.join(',') }
    }
    case 'efi': {
      if (getConfig().efidisk0) throw new Error('已存在EFI磁盘，请先移除')
      const value = `${addForm.storage}:1,efitype=${addForm.efitype || '4m'},pre-enrolled-keys=${addForm.pre_enrolled ? 1 : 0}`
      return { key: 'efidisk0', value }
    }
    case 'tpm': {
      if (getConfig().tpmstate0) throw new Error('已存在TPM设备，请先移除')
      const value = `${addForm.storage}:4,version=${addForm.version || 'v2.0'},model=${addForm.model || 'tpm-crb'}`
      return { key: 'tpmstate0', value }
    }
    case 'usb': {
      const key = getNextDeviceKey('usb')
      const value = `${addForm.host}${addForm.usb3 ? ',usb3=1' : ''}`
      return { key, value }
    }
    case 'pci': {
      const key = getNextDeviceKey('hostpci')
      const value = `${addForm.host}${addForm.pcie ? ',pcie=1' : ''}`
      return { key, value }
    }
    case 'serial': {
      const key = getNextDeviceKey('serial')
      const value = addForm.path ? `${addForm.mode || 'socket'},path=${addForm.path}` : (addForm.mode || 'socket')
      return { key, value }
    }
    case 'cloudinit': {
      const value = `${addForm.storage}:cloudinit`
      const params = {
        ide2: value,
        ciuser: addForm.ciuser || 'root'
      }
      if (addForm.cipassword) params.cipassword = addForm.cipassword
      if (addForm.ipconfig0) params.ipconfig0 = addForm.ipconfig0
      return { params }
    }
    case 'audio': {
      if (getConfig().audio0) throw new Error('已存在音频设备，请先移除')
      const value = `device=${addForm.device || 'ich9-intel-hda'},driver=${addForm.driver || 'spice'}`
      return { key: 'audio0', value }
    }
    case 'rng': {
      if (getConfig().rng0) throw new Error('已存在RNG设备，请先移除')
      const value = `source=${addForm.source || '/dev/urandom'}`
      return { key: 'rng0', value }
    }
    case 'virtiofs': {
      const key = getNextDeviceKey('virtiofs')
      const value = `mount_tag=${addForm.tag},path=${addForm.path}`
      return { key, value }
    }
    default:
      return { key: '', value: '' }
  }
}

const handleAddCancel = () => {
  addState.visible = false
}

const handleAddSubmit = async () => {
  if (!props.vmId) return
  if (addFormRef.value) {
    try {
      await addFormRef.value.validate()
    } catch (error) {
      return
    }
  }
  let payload
  try {
    const result = buildAddParams()
    if (result.params) {
      payload = result.params
    } else if (result.key) {
      payload = { [result.key]: result.value }
    } else {
      Message.warning('无可提交的参数')
      return
    }
  } catch (error) {
    Message.error(error.message || '构建参数失败')
    return
  }
  addState.submitting = true
  try {
    await updateVirtualMachineHardware(props.vmId, { params: payload })
    Message.success(`${addState.title} 创建任务已提交`)
    addState.visible = false
    emit('refresh')
  } catch (error) {
    Message.error('添加硬件失败：' + (error.message || '未知错误'))
  } finally {
    addState.submitting = false
  }
}

// 删除硬件设备
const handleDeleteHardware = async (key, label) => {
  if (!props.vmId) {
    Message.warning('缺少虚拟机ID，无法删除硬件')
    return
  }
  
  // 对于CPU和内存，不允许删除
  if (key === 'cpu' || key === 'memory') {
    Message.warning('无法删除CPU和内存配置')
    return
  }
  
  try {
    // 删除硬件设备：在PVE API中，删除配置项需要将值设置为空字符串
    // 或者使用 delete 参数（格式：delete=key1,key2）
    // 这里我们使用空字符串的方式，因为更简单直接
    const params = { [key]: '' }
    
    // 对于某些设备，可能需要使用delete参数
    // 但先尝试空字符串方式，如果失败再考虑其他方式
    await updateVirtualMachineHardware(props.vmId, { params })
    Message.success(`已删除 ${label}`)
    emit('refresh')
  } catch (error) {
    // 如果空字符串方式失败，尝试使用delete参数
    try {
      const deleteParams = { delete: key }
      await updateVirtualMachineHardware(props.vmId, { params: deleteParams })
      Message.success(`已删除 ${label}`)
      emit('refresh')
    } catch (deleteError) {
      Message.error('删除硬件失败：' + (error.message || deleteError.message || '未知错误'))
    }
  }
}

// 监听 vm 变化，加载硬件资源
watch(() => props.vm, (newVm) => {
  if (newVm) {
    loadHardwareResources()
  }
}, { immediate: true })

onMounted(() => {
  if (props.vm) {
    loadHardwareResources()
  }
})
</script>

<style scoped>
.vm-hardware-tab {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.vm-hardware-tab :deep(.arco-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.vm-hardware-tab :deep(.arco-card-body) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}


.hardware-value {
  white-space: pre-wrap;
  word-break: break-all;
}

.hardware-value .formatted-value {
  font-weight: 500;
  color: var(--color-text-1);
  margin-bottom: 4px;
  line-height: 1.5;
}

.hardware-value .raw-value {
  font-size: 12px;
  color: var(--color-text-3);
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  word-break: break-all;
  opacity: 0.7;
  margin-top: 2px;
}

.hardware-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-shrink: 0;
}

.hardware-toolbar .toolbar-info {
  font-size: 12px;
  color: var(--color-text-3);
}

.edit-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>

