<template>
  <div
    v-if="text === undefined || text === null"
    class="animate-pulse rounded-full bg-slate-400 h-2 inline-block"
    :class="loading ?? ''"
  />
  <component v-else :is="is ?? 'div'">{{ text }}</component>
</template>

<script setup lang="ts">
defineProps<{
  is?: string
  text?: string
  loading?: string
}>()
</script>
