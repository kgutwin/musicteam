<template>
  <div
    v-if="text === undefined"
    class="animate-pulse rounded-full bg-slate-400 h-2 inline-block"
    :class="loading ?? ''"
  />
  <div
    v-else-if="!text"
    class="inline-block"
    :class="{ 'w-6 h-6': !placeholder, 'italic text-gray-300': placeholder }"
  >
    {{ placeholder }}
  </div>
  <component v-else :is="is ?? 'span'">{{ text }}</component>
</template>

<script setup lang="ts">
defineProps<{
  is?: string
  text?: string | null
  loading?: string
  placeholder?: string
}>()
</script>
