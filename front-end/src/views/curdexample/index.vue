<template>
  <div class="example-management">
    <a-card>
      <template #title>
        <a-typography-title :heading="4">示例管理</a-typography-title>
      </template>

      <!-- 工具栏 -->
      <div class="toolbar">
        <a-space>
          <a-input-search
            v-model="searchText"
            placeholder="搜索名称或描述"
            style="width: 300px"
            @search="handleSearch"
            @clear="handleSearch"
            allow-clear
          />
          <a-button type="primary" @click="handleCreate">
            <template #icon>
              <icon-plus />
            </template>
            新增示例
          </a-button>
        </a-space>
      </div>

      <!-- 表格 -->
      <a-table
        :columns="columns"
        :data="tableData"
        :loading="loading"
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        :bordered="false"
        :hoverable="true"
        style="margin-top: 16px"
      >
        <template #price="{ record }">
          {{ formatPrice(record.price) }}
        </template>

        <template #is_active="{ record }">
          <a-tag :color="record.is_active ? 'green' : 'red'">
            {{ record.is_active ? '启用' : '禁用' }}
          </a-tag>
        </template>

        <template #owner_organization="{ record }">
          {{ record.owner_organization?.name || '-' }}
        </template>

        <template #created_at="{ record }">
          {{ formatDate(record.created_at) }}
        </template>

        <template #created_by="{ record }">
          {{ record.created_by?.username || '-' }}
        </template>

        <template #actions="{ record }">
          <a-button type="text" size="small" @click="handleEdit(record)">编辑</a-button>
          <a-button type="text" size="small" status="danger" @click="handleDelete(record)">删除</a-button>
        </template>
      </a-table>
    </a-card>

    <!-- 表单对话框 -->
    <a-modal
      v-model:visible="formVisible"
      :title="formTitle"
      @before-ok="handleSubmit"
      @cancel="handleCancel"
      :width="600"
    >
      <a-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        layout="vertical"
      >
        <a-form-item field="name" label="名称">
          <a-input v-model="formData.name" placeholder="请输入名称" />
        </a-form-item>

        <a-form-item field="description" label="描述">
          <a-textarea 
            v-model="formData.description" 
            placeholder="请输入描述" 
            :auto-size="{ minRows: 3, maxRows: 5 }"
          />
        </a-form-item>

        <a-form-item field="price" label="价格">
          <a-input-number 
            v-model="formData.price" 
            :min="0" 
            :precision="2"
            placeholder="请输入价格"
            style="width: 100%"
          />
        </a-form-item>

        <a-form-item field="is_active" label="是否启用">
          <a-switch v-model="formData.is_active" />
        </a-form-item>

        <a-form-item field="remark" label="备注">
          <a-textarea 
            v-model="formData.remark" 
            placeholder="请输入备注（可选）" 
            :auto-size="{ minRows: 2, maxRows: 4 }"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'
import {
  getExampleList,
  getExampleDetail,
  createExample,
  updateExample,
  deleteExample
} from '@/api/curdexample'

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '名称', dataIndex: 'name' },
  { title: '描述', dataIndex: 'description', ellipsis: true, tooltip: true },
  { title: '价格', dataIndex: 'price', slotName: 'price', width: 120 },
  { title: '状态', dataIndex: 'is_active', slotName: 'is_active', width: 100 },
  { title: '归属组织', dataIndex: 'owner_organization', slotName: 'owner_organization', width: 150 },
  { title: '创建时间', dataIndex: 'created_at', slotName: 'created_at', width: 180 },
  { title: '创建人', dataIndex: 'created_by', slotName: 'created_by', width: 120 },
  { title: '操作', slotName: 'actions', width: 150, fixed: 'right' }
]

const searchText = ref('')
const loading = ref(false)
const tableData = ref([])
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showTotal: true,
  showPageSize: true
})

const formVisible = ref(false)
const formTitle = ref('新增示例')
const formRef = ref()
const formData = reactive({
  id: null,
  name: '',
  description: '',
  price: 0,
  is_active: true,
  remark: ''
})

const formRules = {
  name: [{ required: true, message: '请输入名称' }],
  price: [
    { required: true, message: '请输入价格' },
    { type: 'number', min: 0, message: '价格不能小于0' }
  ]
}

// 格式化价格
const formatPrice = (price) => {
  if (price === null || price === undefined) return '-'
  return `¥${Number(price).toFixed(2)}`
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 获取列表数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    }
    if (searchText.value) {
      params.search = searchText.value
    }
    const res = await getExampleList(params)
    tableData.value = res.results || res.data || []
    pagination.total = res.count || res.total || 0
  } catch (e) {
    Message.error('获取列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.current = 1
  fetchData()
}

// 分页
const handlePageChange = (page) => {
  pagination.current = page
  fetchData()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.current = 1
  fetchData()
}

// 新增
const handleCreate = () => {
  formTitle.value = '新增示例'
  Object.assign(formData, {
    id: null,
    name: '',
    description: '',
    price: 0,
    is_active: true,
    remark: ''
  })
  formVisible.value = true
}

// 编辑
const handleEdit = async (record) => {
  formTitle.value = '编辑示例'
  try {
    const res = await getExampleDetail(record.id)
    Object.assign(formData, {
      id: res.id,
      name: res.name || '',
      description: res.description || '',
      price: res.price || 0,
      is_active: res.is_active !== undefined ? res.is_active : true,
      remark: res.remark || ''
    })
    formVisible.value = true
  } catch (e) {
    Message.error('获取详情失败')
  }
}

// 删除
const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除示例"${record.name}"吗？`,
    onOk: async () => {
      try {
        await deleteExample(record.id)
        Message.success('删除成功')
        fetchData()
      } catch (e) {
        Message.error('删除失败')
      }
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
  } catch (error) {
    return false // 验证失败，阻止关闭
  }

  try {
    const data = {
      name: formData.name.trim(),
      description: formData.description?.trim() || '',
      price: formData.price || 0,
      is_active: formData.is_active,
      remark: formData.remark?.trim() || ''
    }

    if (formData.id) {
      await updateExample(formData.id, data)
      Message.success('更新成功')
    } else {
      await createExample(data)
      Message.success('创建成功')
    }

    formVisible.value = false
    fetchData()
    return true // 允许关闭
  } catch (e) {
    const errorMsg = e.response?.data?.detail || e.response?.data?.message || (formData.id ? '更新失败' : '创建失败')
    Message.error(errorMsg)
    return false // 错误时阻止关闭
  }
}

// 取消
const handleCancel = () => {
  formVisible.value = false
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.example-management {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}
</style>

