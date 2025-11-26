<template>
  <div class="vm-config-tab">
    <a-card :bordered="false">
      <a-empty v-if="!configEntries.length" description="暂无配置数据" />
      <a-descriptions v-else :column="1" bordered>
        <a-descriptions-item
          v-for="item in configEntries"
          :key="item.label"
          :label="item.label"
        >
          <pre class="config-pre">{{ item.value }}</pre>
        </a-descriptions-item>
      </a-descriptions>
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

const configEntries = computed(() => {
  const config = props.vm?.pve_config || {}
  return Object.keys(config).map(key => ({
    label: key,
    value: typeof config[key] === 'object' ? JSON.stringify(config[key], null, 2) : String(config[key])
  }))
})
</script>

<style scoped>
.vm-config-tab {
  width: 100%;
}

.config-pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: var(--font-family-code);
  font-size: 12px;
  line-height: 1.4;
}
</style>

