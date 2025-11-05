<template>
  <label
    @click="(ev) => ev.stopPropagation()"
    :disabled="disabled"
    class="flex flex-row items-baseline gap-1"
  >
    <input v-model="model" type="checkbox" :disabled="disabled" />
    <div class="grow">{{ label }}</div>
  </label>
</template>

<script setup lang="ts">
defineProps<{ label: string; disabled?: boolean }>()
const model = defineModel<boolean>()
</script>
