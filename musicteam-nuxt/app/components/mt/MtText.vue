<template>
  <div
    v-if="text === undefined"
    class="animate-pulse rounded-full bg-slate-400 h-2 inline-block"
    :class="loading ?? ''"
  />
  <div v-else-if="text === null" class="inline-block w-6 h-6" />
  <component v-else :is="is ?? 'div'">{{ text }}</component>
</template>

<script setup lang="ts">
defineProps<{
  is?: string
  text?: string | null
  loading?: string
}>()
</script>
