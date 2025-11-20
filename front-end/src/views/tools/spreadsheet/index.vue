<template>
  <div class="spreadsheet-page">
    <a-card>
      <template #title>
        <a-typography-title :heading="5">在线表格（Luckysheet）</a-typography-title>
      </template>

      <div class="toolbar">
        <a-space wrap>
          <a-button type="primary" @click="createNewSheet">
            <template #icon>
              <icon-plus />
            </template>
            新建表格
          </a-button>
          <a-button @click="loadSample">加载示例</a-button>
          <a-button @click="triggerImport">导入 JSON</a-button>
          <input
            ref="fileInputRef"
            type="file"
            accept=".json,application/json"
            style="display: none"
            @change="handleImportChange"
          />
          <a-button @click="exportSheet">导出 JSON</a-button>
          <a-button @click="saveToLocal">保存到本地缓存</a-button>
          <a-button @click="loadFromLocal">读取本地缓存</a-button>
        </a-space>
      </div>

      <a-alert
        type="info"
        show-icon
        banner
        style="margin-bottom: 12px"
      >
        第一次使用请先执行 <code>npm install luckysheet</code>，然后重新启动前端服务。
        当前示例仅保存到浏览器本地，如需落库可在工具栏按钮里调用后端接口。
      </a-alert>

      <div :id="containerId" class="sheet-container"></div>
    </a-card>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import $ from 'jquery'
import { Message } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'
import 'luckysheet/dist/css/luckysheet.css'
import 'luckysheet/dist/plugins/css/pluginsCss.css'
import 'luckysheet/dist/plugins/plugins.css'

if (typeof window !== 'undefined') {
  window.$ = window.jQuery = $
}

let luckysheet = null

const containerId = 'luckysheet-container'
const fileInputRef = ref(null)
let sheetInitialized = false

const defaultData = [
  {
    name: 'Sheet1',
    color: '#f5f5f5',
    status: 1,
    order: 0,
    column: 26,
    row: 60,
    data: [],
  },
]

const sampleData = [
  {
    name: '周报',
    status: 1,
    order: 0,
    column: 12,
    row: 30,
    data: [
      [
        { v: { m: '任务名称', ct: { fa: 'General', t: 's' } }, fc: '#FFFFFF', bg: '#165dff' },
        { v: { m: '负责人', ct: { t: 's' } }, fc: '#FFFFFF', bg: '#165dff' },
        { v: { m: '进度', ct: { t: 's' } }, fc: '#FFFFFF', bg: '#165dff' },
        { v: { m: '备注', ct: { t: 's' } }, fc: '#FFFFFF', bg: '#165dff' },
      ],
      [
        { v: { m: '权限模块开发' } },
        { v: { m: '小聂' } },
        { v: { m: '80%' } },
        { v: { m: '待联调' } },
      ],
      [
        { v: { m: '知识库上线' } },
        { v: { m: '小王' } },
        { v: { m: '完成' } },
        { v: { m: '已发布 v1.0' } },
      ],
    ],
  },
]

const ensureLuckysheet = async () => {
  if (!luckysheet) {
    const module = await import('luckysheet')
    luckysheet = module.default || module
  }
}

const initSheet = async (data = defaultData) => {
  await ensureLuckysheet()
  if (sheetInitialized) {
    luckysheet.destroy()
  }
  luckysheet.create({
    container: containerId,
    lang: 'zh',
    showinfobar: false,
    data,
    allowUpdate: true,
    showtoolbar: true,
    sheetFormulaBar: true,
  })
  sheetInitialized = true
}

const createNewSheet = async () => {
  await initSheet(defaultData)
  Message.success('已创建空白表格')
}

const loadSample = async () => {
  await initSheet(sampleData)
  Message.success('已加载示例数据')
}

const triggerImport = () => {
  fileInputRef.value?.click()
}

const handleImportChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const json = JSON.parse(e.target.result)
      if (!Array.isArray(json)) throw new Error('格式不正确')
      await initSheet(json)
      Message.success('导入成功')
    } catch (err) {
      Message.error('导入失败：' + err.message)
    } finally {
      event.target.value = ''
    }
  }
  reader.readAsText(file)
}

const getSheetData = () => {
  if (!sheetInitialized || !luckysheet) {
    Message.warning('请先初始化表格')
    return null
  }
  return luckysheet.getAllSheets?.() || []
}

const exportSheet = () => {
  const data = getSheetData()
  if (!data) {
    return
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `sheet-${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(link.href)
}

const localStorageKey = 'luckysheet-cache'

const saveToLocal = () => {
  const data = getSheetData()
  if (!data) return
  localStorage.setItem(localStorageKey, JSON.stringify(data))
  Message.success('已保存到本地缓存')
}

const loadFromLocal = async () => {
  const cached = localStorage.getItem(localStorageKey)
  if (!cached) {
    Message.warning('没有本地缓存')
    return
  }
  try {
    const data = JSON.parse(cached)
    await initSheet(data)
    Message.success('已载入本地缓存')
  } catch (e) {
    Message.error('缓存数据损坏，无法加载')
  }
}

onMounted(() => {
  initSheet()
})

onBeforeUnmount(() => {
  if (sheetInitialized && luckysheet) {
    luckysheet.destroy()
    sheetInitialized = false
  }
})
</script>

<style scoped>
.spreadsheet-page {
  padding: 20px;
}

.toolbar {
  margin-bottom: 12px;
}

.sheet-container {
  width: 100%;
  height: 70vh;
  background: #fff;
  border: 1px solid #e5e6eb;
}
</style>


